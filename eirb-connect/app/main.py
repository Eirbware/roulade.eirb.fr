"""
EirbConnect : Service d'authentification des étudiants de l'ENSEIRB-MATMECA
This is the main file of the application.
"""
from pathlib import Path

from fastapi import FastAPI, Request, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from app.conf import APP_URL, CAS_SERVICE_URL
from app.utils import encrypt_service, resolve_service_url, encode_base64
from app.auth import (register_user, get_user, get_cas_user_from_ticket,
                      get_user_from_token, get_user_data, get_user_data_from_token,
                      update_user, create_access_token,
                      get_user_with_id_and_password)

BASE_DIR = Path(__file__).resolve().parent


app = FastAPI()
app.mount(
    "/static", StaticFiles(directory=str(Path(BASE_DIR, 'static'))), name="static")

templates = Jinja2Templates(directory=str(Path(BASE_DIR, 'templates')))

origins = [
    APP_URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root(request: Request):
    """
    Page de présentation
    """
    print(f"APP_URL: {APP_URL}")
    return templates.TemplateResponse(
        name="index.html",
        context={
            "request": request,
        }
    )


@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    """
    Endpoint pour le favicon
    """
    headers = {
        "Content-Security-Policy": f"default-src 'self' {APP_URL}",
    }
    return FileResponse(str(Path(BASE_DIR, 'static', 'favicon.ico')), headers=headers)


@app.get("/auth")
async def auth(eirb_service_url: str = "EirbConnect"):
    """
    Endpoint pour authentication uniquement avec le cas 
    (redirection transparente pour l'utilisateur)

    Args:
        eirb_service_url (str, optional): _description_. Defaults to "EirbConnect".

    """

    # On encrypte l'url du service et on vérifie qu'il est autorisé à utiliser EirbConnect
    encrypted_service = encrypt_service(eirb_service_url)

    if not encrypted_service:
        return HTTPException(status_code=403, detail="Service not whitelisted")

    redirect_url = f"{APP_URL}/auth/{encrypted_service}/login"

    service_url = f"{CAS_SERVICE_URL}/login?token={encode_base64(redirect_url)}@bordeaux-inp.fr"

    authentication_cas_url = f"https://cas.bordeaux-inp.fr/?service={service_url}&serviceUrl={redirect_url}"

    return RedirectResponse(url=authentication_cas_url)


@app.get("/auth/{encrypted_service}")
async def auth_redirect(encrypted_service: str):
    """
    Endpoint pour redirection vers le CAS
    """
    redirect_url = f"{APP_URL}/auth/{encrypted_service}/login"

    service_url = f"{CAS_SERVICE_URL}/login?token={encode_base64(redirect_url)}@bordeaux-inp.fr"

    authentication_cas_url = f"https://cas.bordeaux-inp.fr/?service={service_url}&serviceUrl={redirect_url}"

    return RedirectResponse(url=authentication_cas_url)


@app.get("/auth/{encrypted_service}/login")
async def auth_login(encrypted_service: str, ticket: str):
    """
    Login avec le CAS puis redirection vers "eirb_service_url"
    """

    redirect_url = f"{APP_URL}/auth/{encrypted_service}/login"
    service_url = f"{CAS_SERVICE_URL}/login?token={encode_base64(redirect_url)}@bordeaux-inp.fr"

    # On récupère l'utilisateur CAS depuis le ticket
    cas_user = get_cas_user_from_ticket(
        ticket,
        service_url
    )

    if not cas_user:
        return HTTPException(status_code=403, detail="Invalid ticket")

    eirb_service_url = resolve_service_url(encrypted_service)

    # On vérifie que l'utilisateur existe dans la base de données
    user = get_user(cas_user.user)

    if not user and eirb_service_url:
        # Si l'utilisateur n'existe pas, on redirige vers la page d'inscription
        return RedirectResponse(url=f"/register?token={create_access_token(cas_user.dict())}&eirb_service_url={encrypted_service}")
    elif not user:
        return RedirectResponse(url=f"/register?token={create_access_token(cas_user.dict())}")

    # Si l'utilisateur existe, on met a jour ses attributs "cas"
    update_user(cas_user)

    user_data = get_user_data(cas_user.user)

    if not user_data:
        return HTTPException(status_code=404, detail="User not found")

    if eirb_service_url:
        return RedirectResponse(url=f"{eirb_service_url}?token={create_access_token(user_data)}")

    return user_data


@app.get("/login")
async def login(request: Request, eirb_service_url: str = "EirbConnect"):
    """
    Page de login
    """
    encrypted_service = encrypt_service(eirb_service_url)

    if not encrypted_service:
        return HTTPException(status_code=403, detail="Service not whitelisted")

    return templates.TemplateResponse(
        name="login.html",
        context={
            "request": request,
            "encrypted_service": encrypted_service,
        }
    )


@app.post("/login/{encrypted_service}")
async def login_post(
        request: Request, encrypted_service: str,
        cas_id: str = Form(...), password: str = Form(...)):
    """
    Route qui s'exécute après l'envoi du formulaire de login et qui authentifie l'utilisateur
    """
    eirb_service_url = resolve_service_url(encrypted_service)

    user = get_user_with_id_and_password(cas_id, password)

    if not user:
        return templates.TemplateResponse(
            name="login.html",
            context={
                "request": request,
                "encrypted_service": encrypted_service,
                "error": "Identifiant ou mot de passe incorrect",
            }
        )

    if eirb_service_url:
        return RedirectResponse(
            url=f"{eirb_service_url}?token={create_access_token(user.model_dump())}",
            status_code=303
        )

    return user


@app.get("/logout")
async def logout():
    """
    Page de logout
    """
    return RedirectResponse(url="https://cas.bordeaux-inp.fr/logout")


@app.get("/register")
async def register(
        request: Request, eirb_service_url: str = "EirbConnect",
        token: str | None = None):
    """
    Page d'inscription
    """

    encrypted_service = encrypt_service(eirb_service_url)

    if not encrypted_service:
        return HTTPException(status_code=403, detail="Service not whitelisted")

    # Si le token n'est pas présent, on redirige vers la page d'authentification
    if not token:
        return RedirectResponse(url=f"/auth?eirb_service_url={eirb_service_url}")

    # Si le token est présent, on vérifie qu'il est valide
    cas_user = get_user_from_token(token)

    return templates.TemplateResponse(
        request=request, name="register.html", context={
            "cas_user": cas_user,
            "token": token,
            "encrypted_service": encrypted_service,
        }
    )


@app.post("/register/{encrypted_service}/{token}")
async def register_post(
        token: str, encrypted_service: str,
        email: str = Form(...), password: str = Form(...)):
    """
    Route qui s'exécute après l'envoi du formulaire de login et qui enregistre l'utilisateur
    """

    eirb_service_url = resolve_service_url(encrypted_service)

    # On récupère les données de l'utilisateur depuis le token
    cas_user = get_user_from_token(token)

    if not cas_user:
        return HTTPException(status_code=403, detail="Invalid token")

    register_user(
        cas_user, email, password)

    user = get_user_data(cas_user.user)

    if not user:
        return HTTPException(status_code=404, detail="User not found")

    if eirb_service_url:
        return RedirectResponse(url=f"{eirb_service_url}?token={create_access_token(user)}")

    return user


@app.get("/get_user_info")
def get_user_info(token: str):
    """
    Endpoint pour récupérer les informations d'un utilisateur à partir d'un token
    """
    return get_user_data_from_token(token)
