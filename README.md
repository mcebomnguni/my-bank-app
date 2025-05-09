# Capestone Bank

Capestone Bank is an online banking platform designed to simplify financial management. It allows users to easily open bank accounts, perform secure transactions, and access various banking and insurance services — all from a user-friendly digital interface.

## Table of Contents

- [Project Description](#project-description)
- [Features](#features)
- [Usage](#usage)
- [Tools and Technology Used](#tools-and-technology-used)
- [Credits](#credits)
- [Setup Instructions](#setup-instructions)

---

## Project Description

Capestone Bank is a modern internet banking solution. It enables users to:

- Register and manage a digital bank account.
- Perform secure transactions with ease.
- Apply for services such as car loans, funeral cover, and insurance policies.
- Access 24/7 support with real-time assistance.

This project was built using Django and aims to provide a comprehensive and user-friendly digital banking experience.

## Features

- **Login Page**: Prompts users to enter their login credentials.
- **Signup Page**: Allows new users to register with a username and password.
- **Complete Profile Page**: Users can fill in personal information for identity verification.
- **Dashboard**: Displays a digital card, account number, balance, and options to transfer or reserve funds.
- **Services Section**:
  - Car loan application
  - Home loan application
  - Funeral cover
  - Car, home, and life insurance
- **Support Page**:
  - Head office address
  - Contact number and email
  - Social media links
  - Virtual video assistant for support

---

## Usage
After installation:

Sign Up: Create an account by filling out the registration form.

Login: Enter your credentials to access your dashboard.

Complete Profile: Provide required personal details.

Explore Features:

View account balance and digital card

Transfer or reserve funds

Apply for loans or insurance

Support: Visit the support page to contact customer service or use the virtual assistant.

---

## Tools and Technology Used

- Backend
Django – High-level Python web framework used for rapid development and clean, pragmatic design.

Python 3 – Primary programming language used throughout the project.

- Containerization
Docker – Used to containerize the application for consistent development and deployment environments.

Docker Compose – Manages multi-container setups (e.g., web server + database).

- Database
SQLite – Lightweight, file-based database for local development.

- Dependency & Environment Management
requirements.txt – Lists all Python dependencies.

Python Virtual Environment (venv) – Isolates project dependencies.

.env file – Stores sensitive environment variables such as SECRET_KEY and database credentials.

- Documentation
Sphinx – Auto-generates project documentation using reStructuredText (.rst) and outputs HTML.

reStructuredText (.rst) – Lightweight markup language used for writing documentation pages.

- Frontend (Static Assets)
HTML Templates – Django's template engine for rendering dynamic pages.

CSS / JavaScript / Images – Stored in a structured static/ directory, following Django’s static files best practices.

- Version Control & Hosting
Git – Distributed version control system.

GitHub – Used for hosting the project repository and collaboration.

---

## Credits
This project was created by:

Mcebo Mnguni

---

## Setup Instructions

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

---