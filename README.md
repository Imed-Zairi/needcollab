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

| Couche    | Technologie                        |
|-----------|------------------------------------|
| Backend   | Django 5 + Django REST Framework   |
| Frontend  | Flask 3 + Jinja2                   |
| Base de données | SQLite (dev)               |
| Auth      | Token Authentication (DRF)         |
| UI        | Bootstrap 5 + AOS + Bootstrap Icons|

---

## Structure du projet

```
needcollab/
├── backend/
│   ├── api/
│   │   ├── models.py        # Need, Offer, Vote, Profile
│   │   ├── serializers.py   # Sérialisation DRF
│   │   ├── views.py         # Logique API
│   │   ├── urls.py          # Routes API
│   │   └── admin.py
│   └── backend/
│       ├── settings.py
│       └── urls.py
├── frontend/
│   ├── app.py               # Routes Flask
│   └── templates/
│       ├── base.html        # Layout + navbar
│       ├── index.html       # Landing + liste des besoins
│       ├── login.html       # Connexion
│       ├── register.html    # Inscription
│       ├── profile.html     # Profil utilisateur
│       ├── edit_profile.html
│       ├── need_detail.html # Détail besoin + offres + votes
│       ├── create_need.html
│       └── create_offer.html
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

Créer les tables :
```bash
cd backend
python manage.py migrate
```

---

## Lancement

Ouvrir deux terminaux :

```bash
# Terminal 1 — Backend Django (port 8000)
source venv/bin/activate
cd backend && python manage.py runserver

# Terminal 2 — Frontend Flask (port 5000)
source venv/bin/activate
cd frontend && python app.py
```

Accéder à l'application : **http://localhost:5000**

---

## API Reference

Base URL : `http://localhost:8000/api`

Les routes protégées nécessitent le header :
```
Authorization: Token <token>
```

### Authentification

| Méthode | Endpoint            | Auth | Description                              |
|---------|---------------------|------|------------------------------------------|
| POST    | `/auth/register/`   | ✗    | Créer un compte                          |
| POST    | `/auth/login/`      | ✗    | Se connecter, retourne un token          |

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

| Méthode | Endpoint               | Auth | Description                        |
|---------|------------------------|------|------------------------------------|
| GET     | `/profile/`            | ✓    | Récupérer son profil + stats       |
| PATCH   | `/profile/update/`     | ✓    | Modifier username, email, bio, location |
| GET     | `/profile/needs/`      | ✓    | Besoins créés par l'utilisateur    |
| GET     | `/profile/collabs/`    | ✓    | Besoins rejoints par l'utilisateur |

**GET `/profile/`**
```json
// Réponse 200
{
  "username": "alice",
  "email": "alice@mail.com",
  "bio": "Passionnée de tech",
  "location": "Paris",
  "date_joined": "2026-04-21T00:00:00Z",
  "needs_count": 3,
  "collabs_count": 5
}
```

**PATCH `/profile/update/`**
```json
// Body (tous les champs optionnels)
{ "username": "alice2", "email": "new@mail.com", "bio": "...", "location": "Lyon" }
```

---

### Besoins (Needs)

| Méthode | Endpoint              | Auth | Description                          |
|---------|-----------------------|------|--------------------------------------|
| GET     | `/needs/`             | ✗    | Lister tous les besoins              |
| POST    | `/needs/`             | ✓    | Créer un besoin                      |
| GET     | `/needs/<id>/`        | ✗    | Détail d'un besoin + offres          |
| POST    | `/needs/<id>/join/`   | ✓    | Rejoindre une collaboration          |

**POST `/needs/`**
```json
// Body
{ "title": "MacBook Pro M3", "description": "Recherche MacBook Pro 14 pouces M3 16Go RAM" }

// Réponse 201
{
  "id": 1,
  "title": "MacBook Pro M3",
  "description": "...",
  "creator": "alice",
  "collaborators_count": 0,
  "created_at": "2026-04-21T10:00:00Z",
  "offers": []
}
```

**GET `/needs/<id>/`**
```json
// Réponse 200
{
  "id": 1,
  "title": "MacBook Pro M3",
  "description": "...",
  "creator": "alice",
  "collaborators_count": 4,
  "created_at": "2026-04-21T10:00:00Z",
  "offers": [
    {
      "id": 1,
      "seller_name": "TechStore",
      "price": "1899.00",
      "description": "Livraison 48h",
      "accept_count": 3,
      "reject_count": 1,
      "votes": [...]
    }
  ]
}
```

---

### Offres (Offers)

| Méthode | Endpoint                        | Auth | Description                    |
|---------|---------------------------------|------|--------------------------------|
| GET     | `/needs/<id>/offers/`           | ✗    | Lister les offres d'un besoin  |
| POST    | `/needs/<id>/offers/`           | ✓    | Soumettre une offre            |

**POST `/needs/<id>/offers/`**
```json
// Body
{ "seller_name": "TechStore Paris", "price": "1899.00", "description": "Stock disponible, livraison 48h" }
```

---

### Votes

| Méthode | Endpoint                    | Auth | Description                         |
|---------|-----------------------------|------|-------------------------------------|
| POST    | `/offers/<id>/vote/`        | ✓    | Voter pour/contre une offre         |

**POST `/offers/<id>/vote/`**
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
- **API utilisée :** `GET /api/needs/`

### `/register` — Inscription
- Formulaire : username, email (optionnel), password
- Redirige vers l'accueil après inscription
- **API utilisée :** `POST /api/auth/register/`

### `/login` — Connexion
- Formulaire : username, password
- Redirige vers la page demandée (`?next=`) ou l'accueil
- **API utilisée :** `POST /api/auth/login/`

### `/needs/create` — Créer un besoin `🔒`
- Formulaire : titre, description
- **API utilisée :** `POST /api/needs/`

### `/needs/<id>` — Détail d'un besoin
- Informations du besoin (titre, description, nombre de collaborateurs)
- Liste des offres avec barres de vote (accept/reject)
- Bouton "Rejoindre" `🔒`
- Bouton "Soumettre une offre" `🔒`
- Boutons de vote accept/reject sur chaque offre `🔒`
- Sans connexion : affiche les offres en lecture seule avec lien vers login
- **APIs utilisées :** `GET /api/needs/<id>/`, `POST /api/needs/<id>/join/`, `POST /api/offers/<id>/vote/`

### `/needs/<id>/offers/create` — Soumettre une offre `🔒`
- Formulaire : nom du vendeur, prix, description
- **API utilisée :** `POST /api/needs/<id>/offers/`

### `/profile` — Profil utilisateur `🔒`
- Avatar, username, email, localisation, bio
- Stats : besoins créés, collaborations rejointes, total activités, date d'inscription
- Onglet "Mes besoins" : historique des besoins créés
- Onglet "Mes collaborations" : historique des besoins rejoints
- **APIs utilisées :** `GET /api/profile/`, `GET /api/profile/needs/`, `GET /api/profile/collabs/`

### `/profile/edit` — Modifier le profil `🔒`
- Formulaire pré-rempli : username, email, localisation, bio
- **API utilisée :** `PATCH /api/profile/update/`

> `🔒` = connexion requise, redirige vers `/login` si non authentifié

---

## Modèles de données

```
User (Django built-in)
 └── Profile        (bio, location)

Need
 ├── creator        → User
 ├── collaborators  → [User]
 └── offers         → [Offer]
      └── votes     → [Vote]
                         └── user → User
```
