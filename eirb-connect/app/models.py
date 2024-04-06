"""
This file contains the models for the application.
"""

from pydantic import BaseModel


class CasUserAttributes(BaseModel):
    """
    UserAttributes model
    """
    nom: str
    prenom: str
    courriel: str
    profil: str
    nom_complet: str
    ecole: str
    diplome: str
    supannEtuAnneeInscription: str


class CasUser(BaseModel):
    """
    User model
    """
    user: str
    attributes: CasUserAttributes


class UserAttributes(BaseModel):
    """
    UserAttributes model
    """
    nom: str
    prenom: str
    courriel: str
    email_personnel: str
    profil: str
    nom_complet: str
    ecole: str
    supannEtuAnneeInscription: str
    diplome: str


class Role(BaseModel):
    """
    Role model
    """
    nom_asso: str
    mandat: str
    postes: list[str]


class User(BaseModel):
    """
    User model
    """
    user: str
    attributes: UserAttributes
    password: str
    roles: list[Role]
