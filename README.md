# Policy Platform Nigeria (PPN)

Local Django project scaffold for Policy Platform Nigeria.

Quick start:

```bash
python -m venv .venv
source .venv/Scripts/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_policies
python manage.py runserver
```

Open http://127.0.0.1:8000/ after starting the server.
