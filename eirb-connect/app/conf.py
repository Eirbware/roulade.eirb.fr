"""
This file contains the configuration for the application.
"""

import os
import hashlib
from pathlib import Path
from dotenv import load_dotenv
import pymongo

# Load environment variables from .env file
dotenv_path = Path(os.path.dirname(os.path.abspath(__file__))) / ".env"
load_dotenv(dotenv_path=dotenv_path)

APP_URL = os.getenv("APP_URL", "http://127.0.0.1:8080")
CAS_SERVICE_URL = os.getenv("CAS_SERVICE_URL", "https://cas.bordeaux-inp.fr/")

DEFAULT_ADMIN_PASS = "admin"
ADMIN_PASS = os.getenv("ADMIN_PASS", DEFAULT_ADMIN_PASS)

CAS_PROXY = os.getenv("CAS_PROXY", "")


host = os.getenv("MONGO_URI", "localhost:27017")
client: pymongo.MongoClient = pymongo.MongoClient(host=f"mongodb://{host}")
mongodb = client.AssosConnect

# The secret key should be UNIQUE and SECRET
# You may use the following command to generate a secret key:
# openssl rand -hex 32
# Copy the output and paste it in the .env file as SECRET_KEY variable

SECRET_KEY = os.getenv("SECRET_KEY", "very_secret_key")
ACCES_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCES_TOKEN_EXPIRE_MINUTES", "30"))

# encryption algorithm
ALGORITHM = os.getenv("ALGORITHM", "HS256")


def config_disp():
    return f"""Config :
APP_URL={APP_URL}
CAS_SERVICE_URL={CAS_SERVICE_URL}
CAS_PROXY={CAS_PROXY}
host={host}
SECRET_KEY={SECRET_KEY}
ACCESS_TOKEN_EXPIRE_MINUTES={ACCES_TOKEN_EXPIRE_MINUTES}
ALGORITHM={ALGORITHM}
ADMIN_PASS={ADMIN_PASS}
"""


def create_collections(collection_list):
    """
    Create collections in database if they don't exist
    """
    for collection in collection_list:
        if collection not in mongodb.list_collection_names():
            mongodb.create_collection(collection)


create_collections(["utilisateurs", "services", "roles", "assos"])

# We insert the EirbConnect service
if not mongodb.services.find_one({"service_url": "EirbConnect"}):
    mongodb.services.insert_one(
        {
            "service_url": "EirbConnect",
            "hash": hashlib.md5(APP_URL.encode()).hexdigest(),
        }
    )

from app.utils import get_password_hash

# Create an account for eirbware, used as an admin account for other services
# To prevent security issues, the admin password musn't be the default one
if ADMIN_PASS != DEFAULT_ADMIN_PASS and not mongodb.utilisateurs.find_one(
    {"utilisateurs": "eirbware"}
):
    mongodb.utilisateurs.insert_one(
        {
            "user": "eirbware",
            "attributes": {
                "nom": "",
                "prenom": "Eirbware",
                "courriel": "eirbware@enseirb-matmeca.fr",
                "email_personnel": "eirbware@enseirb-matmeca.fr",
                "profil": "asso",
                "nom_complet": "Eirbware",
                "ecole": "enseirb-matmeca",
                "diplome": "",
                "supannEtuAnneeInscription": "2024",
            },
            "password": get_password_hash(ADMIN_PASS),
            "roles": [],
        }
    )

print(config_disp())
