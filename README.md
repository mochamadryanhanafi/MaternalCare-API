# MaternalCare API

MaternalCare is a Flask-based web application providing services for maternal health during pregnancy. It allows users to register, log in, reset passwords, and access relevant health information via a variety of endpoints. This project integrates Firebase Firestore for storing user data and uses the NewsAPI to fetch health-related articles.

## Features

- **User Registration**: Users can register with email, username, full name, password, date of birth, and phone number.
- **Login**: Users can log in with their credentials (email and password).
- **Password Reset**: Allows users to reset their password via a token-based mechanism.
- **Articles**: Fetches health-related articles from NewsAPI.

## Requirements

To run this project, you need the following:

- Python 3.x
- Flask
- Firebase Admin SDK
- `requests` library
- `werkzeug` library

Install the required dependencies using the following command:

```bash
pip install -r requirements.txt
