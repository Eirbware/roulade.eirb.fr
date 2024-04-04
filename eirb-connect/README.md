# EirbConnect

## Description

EirbConnect est un service d'authentification pensé pour connecter les étudiants de l'ENSEIRB-MATMECA aux services de l'école créés par les étudiants (dont Eirbware et le BDE).
Il permet également aux anciens élèves de l'école de continuer de se connecter aux services associatifs apprès suppression leur compte CAS.

## Table des matières

- Technologies
- Installation
- Docker
- Utilisation

## Technologies

Framework: FastAPI
Database: MongoDB

## Installation

### Prérequis

- MongoDB
  Les collections suivantes seront créées automatiquement :
  - services : liste des services qui sont autorisés à utiliser EirbConnect 
  - assos : liste des associations (pour assos.eirb.fr)
  - utilisateurs : liste des utilisateurs
  - roles : liste de leurs rôles dans les associations
- Python

### Installation

#### Créer un environnement virtuel

```bash
python3 -m venv venv
```

#### Activer l'environnement virtuel

```bash
source venv/bin/activate
```

#### Installer les dépendances

```bash
pip install -r requirements.txt
```

#### Configurer les variables d'environnement

Voici un exemple de fichier `.env` à créer dans app :

```bash
touch app/.env
```

```
MONGO_URI = localhost:27017

# auth

# à générer avec openssl rand -hex 32
SECRET_KEY = "<clé secrète pour les tokens JWT>"
ACCES_TOKEN_EXPIRE_MINUTES = 30
ALGORITHM = "HS256"

# Config pour docker

APP_URL = "http://0.0.0.0:8080"
```

#### Lancer le serveur

```bash
./run.sh
```

## Docker

### Créer l'image

```bash
docker build -t eirb_connect .
```

### Lancer le conteneur

```bash
ocker run -d -p 8000:80 -e MONGO_URI=localhost:27017 --name EirbConnect eirb_connect
```

## Utilisation

### GET `/auth` 

Paramètres:
  - eirb_service_url: URL du service à rediriger après authentification (optionnel)

Permet d'idientifier un utilisateur avec le CAS Bordeaux INP de manière transparente pour un utilisateur qui a un compte EirbConnect.
Si l'utilisateur n'a pas de compte EirbConnect, il sera redirigé vers la page de création de compte.

### GET `/login`

Paramètres:
  - eirb_service_url: URL du service à rediriger après authentification (optionnel)

Redirige l'utilisateur vers une page de connexion. Sur cette page l'utilisateur peut se connecter avec son identifiant CAS et un mot de passe ou alors se connecter avec le CAS (redirection vers /auth).

### GET `/register`

Paramètres:
  - eirb_service_url: URL du service à rediriger après authentification (optionnel)

Redirige l'utilisateur vers le CAS Bordeaux INP, récupère les informations de l'utilisateur puis le redirige vers une page de création de compte. Sur cette page l'utilisateur est alors invité à renseigner son mail personnel et un mot de passe.

### GET `/get_user_info?token=<token>`

Paramètres:
  - token: token JWT de l'utilisateur
Permet de récupérer les informations de l'utilisateur après authentification.

### GET `/logout`

Déconnecte l'utilisateur du service.


