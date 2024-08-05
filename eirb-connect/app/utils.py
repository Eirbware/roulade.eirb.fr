"""
This module contains helper functions
"""

import base64
from app.conf import mongodb
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Helper password functions
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


def encrypt_service(service_url: str) -> str | None:
    """
    Check if the user is whitelisted
    """
    service = mongodb.services.find_one({"service_url": service_url})
    if service:
        return service["hash"]
    return None


def resolve_service_url(hashed_url: str) -> str | None:
    """
    Resolve a service url
    """
    service = mongodb.services.find_one({"hash": hashed_url})
    if service and service["service_url"] != "EirbConnect":
        return service["service_url"]
    return None


def encode_base64(string: str) -> str:
    """
    Encode a string in base64
    """
    return base64.b64encode(string.encode("utf-8")).decode("utf-8")
