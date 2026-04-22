# NeedCollab

Plateforme d'achat groupé permettant aux utilisateurs de se regrouper pour négocier de meilleurs prix auprès des commerçants.

---

## Concept

Un utilisateur crée un **besoin** (need) pour un produit ou service. D'autres utilisateurs rejoignent la collaboration. Les vendeurs soumettent des offres. Les collaborateurs votent pour accepter ou rejeter chaque offre. La force du groupe permet d'obtenir des prix négociés.

**Flux principal :**
```
Créer un besoin → Rejoindre la collab → Vendeur soumet une offre → Vote collectif
```

---

## Stack technique

| Couche          | Technologie                          |
|-----------------|--------------------------------------|
| Frontend        | Django 5 + templates Django          |
| Backend API     | Flask 3 + Flask-SQLAlchemy           |
| Base de données | SQLite (dev)                         |
| Auth            | Token Authentication (maison)        |
| UI              | Bootstrap 5 + AOS + Bootstrap Icons  |

---

## Structure du projet

```
needcollab/
├── api/                        # Flask — Backend API (port 5000)
│   ├── app.py                  # Modèles + routes JSON
│   └── needcollab.db           # Base de données SQLite
├── web/                        # Django — Frontend (port 8000)
│   ├── manage.py
│   ├── backend/
│   │   ├── settings.py
│   │   └── urls.py
│   └── web/
│       ├── views.py            # Logique frontend (appelle l'API Flask)
│       ├── urls.py             # Routes Django
│       └── templates/
│           ├── base.html       # Layout + navbar
│           ├── index.html      # Landing + liste des besoins
│           ├── login.html      # Connexion
│           ├── register.html   # Inscription
│           ├── profile.html    # Profil utilisateur
│           ├── edit_profile.html
│           ├── need_detail.html  # Détail besoin + offres + votes
│           ├── create_need.html
│           ├── edit_need.html
│           └── create_offer.html
├── requirements.txt
└── venv/
```

---

## Installation

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Initialiser la base de données Flask :
```bash
cd api && python -c "from app import app, db; app.app_context().push(); db.create_all()"
```

---

## Lancement

Ouvrir deux terminaux :

```bash
# Terminal 1 — Flask API (port 5000)
source venv/bin/activate
cd api && python app.py

# Terminal 2 — Django Frontend (port 8000)
source venv/bin/activate
cd web && python manage.py runserver
```

Accéder à l'application : **http://localhost:8000**

---

## API Reference

Base URL : `http://localhost:5000/api`

Les routes protégées nécessitent le header :
```
Authorization: Token <token>
```

### Authentification

| Méthode | Endpoint            | Auth | Description                     |
|---------|---------------------|------|---------------------------------|
| POST    | `/auth/register/`   | ✗    | Créer un compte                 |
| POST    | `/auth/login/`      | ✗    | Se connecter, retourne un token |

**POST `/auth/register/`**
```json
// Body
{ "username": "alice", "password": "motdepasse", "email": "alice@mail.com" }

// Réponse 200
{ "token": "abc123...", "user_id": 1, "username": "alice" }
```

**POST `/auth/login/`**
```json
// Body
{ "username": "alice", "password": "motdepasse" }

// Réponse 200
{ "token": "abc123...", "user_id": 1, "username": "alice" }

// Réponse 400
{ "error": "Identifiants invalides." }
```

---

### Profil

| Méthode | Endpoint             | Auth | Description                              |
|---------|----------------------|------|------------------------------------------|
| GET     | `/profile/`          | ✓    | Récupérer son profil + stats             |
| PATCH   | `/profile/update/`   | ✓    | Modifier username, email, bio, location  |
| GET     | `/profile/needs/`    | ✓    | Besoins créés par l'utilisateur          |
| GET     | `/profile/collabs/`  | ✓    | Besoins rejoints par l'utilisateur       |

---

### Besoins (Needs)

| Méthode | Endpoint                  | Auth | Description                      |
|---------|---------------------------|------|----------------------------------|
| GET     | `/needs/`                 | ✗    | Lister tous les besoins          |
| POST    | `/needs/`                 | ✓    | Créer un besoin                  |
| GET     | `/needs/<id>/`            | ✗    | Détail d'un besoin + offres      |
| PATCH   | `/needs/<id>/`            | ✓    | Modifier un besoin (créateur)    |
| DELETE  | `/needs/<id>/`            | ✓    | Supprimer un besoin (créateur)   |
| POST    | `/needs/<id>/archive/`    | ✓    | Archiver/désarchiver (créateur)  |
| POST    | `/needs/<id>/join/`       | ✓    | Rejoindre une collaboration      |

---

### Offres (Offers)

| Méthode | Endpoint                  | Auth | Description                    |
|---------|---------------------------|------|--------------------------------|
| GET     | `/needs/<id>/offers/`     | ✗    | Lister les offres d'un besoin  |
| POST    | `/needs/<id>/offers/`     | ✓    | Soumettre une offre            |

---

### Votes

| Méthode | Endpoint               | Auth | Description                  |
|---------|------------------------|------|------------------------------|
| POST    | `/offers/<id>/vote/`   | ✓    | Voter pour/contre une offre  |

```json
// Body
{ "choice": "accept" }   // ou "reject"

// Réponse 200
{ "id": 1, "user": 1, "choice": "accept" }
```

---

## Interfaces Frontend

### `/` — Landing page & liste des besoins
- Section hero avec call-to-action
- Statistiques globales (besoins actifs, vendeurs, satisfaction)
- Section "Comment ça fonctionne" en 4 étapes
- Grille de tous les besoins publiés (accessibles sans connexion)

### `/register` — Inscription
- Formulaire : username, email (optionnel), password

### `/login` — Connexion
- Formulaire : username, password
- Redirige vers la page demandée (`?next=`) ou l'accueil

### `/needs/create` — Créer un besoin `🔒`
- Formulaire : titre, description

### `/needs/<id>` — Détail d'un besoin
- Informations du besoin (titre, description, nombre de collaborateurs)
- Liste des offres avec barres de vote (accept/reject)
- Bouton "Rejoindre" `🔒`
- Bouton "Soumettre une offre" `🔒`
- Boutons de vote accept/reject sur chaque offre `🔒`
- Sans connexion : affiche les offres en lecture seule

### `/needs/<id>/edit` — Modifier un besoin `🔒`
- Formulaire pré-rempli : titre, description
- Accessible uniquement au créateur du besoin

### `/needs/<id>/offers/create` — Soumettre une offre `🔒`
- Formulaire : nom du vendeur, prix, description

### `/profile` — Profil utilisateur `🔒`
- Avatar, username, email, localisation, bio
- Stats : besoins créés, collaborations rejointes, total activités, date d'inscription
- Onglet "Mes besoins" : liste avec boutons **Modifier**, **Archiver/Désarchiver**, **Supprimer**
- Onglet "Mes collaborations" : historique des besoins rejoints

### `/profile/edit` — Modifier le profil `🔒`
- Formulaire pré-rempli : username, email, localisation, bio

> `🔒` = connexion requise, redirige vers `/login` si non authentifié

---

## Modèles de données

```
User
 ├── needs        → [Need]
 └── joined_needs → [Need]  (collaborateurs)

Need
 ├── creator      → User
 ├── collaborators → [User]
 ├── archived     → Boolean
 └── offers       → [Offer]
      └── votes   → [Vote]
                       └── user → User
```
