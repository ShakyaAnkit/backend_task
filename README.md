# Backend Task

## Project Setup
```bash
pip install -r requirements.txt
cp backend_task/settings.py.example backend_task/settings.py
python manage.py makemigrations dashboard audit
python manage.py migrate
```

## Create superuser
```bash
python manage.py createsuperuser
```