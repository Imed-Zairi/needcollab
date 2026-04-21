# NeedCollab

Application web avec un backend Django et un frontend Flask.

## Structure

```
needcollab/
├── backend/      # API Django (port 8000)
├── frontend/     # App Flask (port 5000)
├── requirements.txt
└── venv/
```

## Installation

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Lancement

```bash
# Backend Django
cd backend && python manage.py runserver

# Frontend Flask
cd frontend && python app.py
```
