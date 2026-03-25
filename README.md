# Vault Times 

A role-based news publishing platform built with Django and Django REST Framework.

## Features

* Roles: Reader, Journalist, Editor, Publisher
* Article approval system
* Newsletter system
* Publisher dashboard
* REST API with permissions

## Setup

```bash
git clone https://github.com/giavassallo/vault-times
cd vault-times
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Run Tests

```bash
python manage.py test
```

## Admin Access

```bash
python manage.py createsuperuser
```

Go to:
http://127.0.0.1:8000/admin/

## Documentation

Open:
docs/build/html/index.html

## Docker

```bash
docker build -t vault-times .
docker run -p 8000:8000 vault-times
```
