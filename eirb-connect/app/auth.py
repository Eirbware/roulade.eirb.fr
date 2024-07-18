"""
This module contains the authentication logic
"""

from datetime import datetime, timedelta
from typing import Annotated

from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer

from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

import requests

from app.models import CasUser, CasUserAttributes, User
from app.conf import mongodb, SECRET_KEY, ACCES_TOKEN_EXPIRE_MINUTES, ALGORITHM

from bson.objectid import ObjectId


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Pydantic Model that will be used in the
# token endpoint for the response


class Token(BaseModel):
    """
    Token model
    """
    access_token: str
    token_type: str


class Payload(BaseModel):
    """
    Payload model
    """
    status: str
    payload: dict
    token: str


# Helper password functions²

def verify_password(plain_password, hashed_password):
    """
    Helper function to check if a password matches a hashed password
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    """
    Helper function to generate a hashed password
    """
    return pwd_context.hash(password)

# Helper token functions


def create_access_token(data: dict):
    """
    Create the access token with the data and return it
    """
    to_encode = data.copy()

    # expire time of the token
    expire = datetime.utcnow() + timedelta(minutes=ACCES_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "iss": "EirbConnect"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    # return the generated token
    return encoded_jwt


def verify_token(token: str):
    """
    If the token is valid return the payload
    Else raise an exception
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return Payload(status="authorized", payload=payload, token=token)
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        ) from exc


def get_cas_user_from_ticket(ticket: str, service_url: str) -> CasUser | None:
    """
    Return the user from the CAS ticket
    """
    res = requests.get(
        f"https://cas.bordeaux-inp.fr/serviceValidate?service={service_url}&ticket={ticket}&format=json", timeout=5).json()

    if "authenticationSuccess" in res["serviceResponse"]:
        user_response = res["serviceResponse"]["authenticationSuccess"]

        user = CasUser(user=user_response["user"], attributes=CasUserAttributes(**{
            "nom": user_response["attributes"]["nom"][0],
            "prenom": user_response["attributes"]["prenom"][0],
            "courriel": user_response["attributes"]["courriel"][0],
            "email_personnel": "",
            "profil": user_response["attributes"]["profil"][0],
            "nom_complet": user_response["attributes"]["nom_complet"][0],
            "ecole": user_response["attributes"]["ecole"][0],
            "diplome": user_response["attributes"]["diplome"][0],
            "supannEtuAnneeInscription": user_response["attributes"]["supannEtuAnneeInscription"][0]
        }))
        return user
    

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=res['serviceResponse']['authenticationFailure'],
    )


def update_user(cas_user: CasUser):
    """
    Update the user in the db
    """
    cas_user_dict = cas_user.model_dump()

    mongo_user = mongodb.utilisateurs.find_one({"user": cas_user_dict["user"]})

    if mongo_user:
        # On met a jour tous les attributs "cas" de l'utilisateur
        for key in cas_user_dict["attributes"]:
            mongo_user["attributes"][key] = cas_user_dict["attributes"][key]
        mongodb.utilisateurs.update_one({"user": cas_user_dict["user"]}, {
            "$set": {"attributes": mongo_user["attributes"]}})
        return

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"User {cas_user.user} not found",
    )


def get_user(cas_id: str) -> User | None:
    """
    Get an EirbConnect user with a cas id
    """
    user = mongodb.utilisateurs.find_one({"user": cas_id})
    if user:
        if user["roles"]:
            for i, role in enumerate(user["roles"]):
                asso = mongodb.assos.find_one(ObjectId(role["id_asso"]))
                user["roles"][i]["nom_asso"] = asso["name"] if asso else ""
                del user["roles"][i]["id_asso"]
        return User(**user)
    return None


def get_user_with_id_and_password(cas_id: str, password: str) -> User | None:
    """
    Log an EirbConnect user with a cas id and a password
    """
    user = get_user(cas_id)
    if user:
        if verify_password(password, user.password):
            return user
    return None


def get_user_data(cas_id: str) -> dict | None:
    """
    Get EirbConnect user's data with a cas id
    """
    user = get_user(cas_id)
    if user:
        user_dict = user.model_dump()
        return {key: user_dict[key] for key in user_dict if key != "password"}
    return None


def get_user_data_from_token(token: str) -> dict:
    """
    Get EirbConnect user's data with a token
    """
    payload = verify_token(token)
    return {
        key: payload.payload[key] for key in payload.payload if key != "password"
    }


def get_user_from_token(token: str) -> CasUser | None:
    """
    Get a CasUser with a token
    """
    payload = verify_token(token)
    return CasUser(**payload.payload)


def register_user(cas_user: CasUser, email_personnel: str, password: str):
    """
    Register a user
    """
    # check if the user already exists
    user = get_user(cas_user.user)

    if user:
        return user

    # hash the password
    hashed_password = get_password_hash(password)

    # insert the user in the db

    mongodb.utilisateurs.insert_one({
        "user": cas_user.user,
        "attributes": {
            "nom": cas_user.attributes.nom,
            "prenom": cas_user.attributes.prenom,
            "courriel": cas_user.attributes.courriel,
            "email_personnel": email_personnel,
            "profil": cas_user.attributes.profil,
            "nom_complet": cas_user.attributes.nom_complet,
            "ecole": cas_user.attributes.ecole,
            "diplome": cas_user.attributes.diplome,
            "supannEtuAnneeInscription": cas_user.attributes.supannEtuAnneeInscription
        },
        "password": hashed_password,
        "roles": []
    })

    return mongodb.utilisateurs.find_one({"user": cas_user.user})


def login_user_with_password(cas_id: str, password: str):
    """
    Login a user
    """
    # check if the user already exists
    user = get_user(cas_id)
    if not user:
        return None, None

    # check if the password is correct
    if not verify_password(password, user.password):
        return None, None

    # generate the token
    token = create_access_token({
        "user": cas_id,
        "nom": user.attributes.nom,
        "prenom": user.attributes.prenom,
        "courriel": user.attributes.courriel,
        "email_personnel": user.attributes.email_personnel,
        "profil": user.attributes.profil,
        "nom_complet": user.attributes.nom_complet,
        "ecole": user.attributes.ecole,
        "diplome": user.attributes.diplome
    })

    # return the token
    return token, user


async def handle_auth(token: Annotated[str, Depends(oauth2_scheme)]):
    """
    Handle the authentication
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload

    except JWTError as exc:
        raise credentials_exception from exc
