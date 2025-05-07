# My Bank App

## Setup Instructions (venv)

```bash
1. python -m venv venv
2. source venv/bin/activate
3. pip install -r requirements.txt
4. python manage.py runserver

## Setup Instructions for Secrets

SECRET_KEY=m&7hh0fvdl9h(9zlew*v2pp50%g(5-g73^84u6dln(k#s@+lwz
DEBUG=True

##  Build the Docker image

---bash
1.docker build -t my-bank-app .
2.docker run -d -p 8000:8000 --env-file .env my-bank-app
3. Access the app http://localhost:8000
