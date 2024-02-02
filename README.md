# Backend Assignment

This project connects to the Gmail API, reads emails from the inbox, and stores them in a PostgreSQL database. It includes functionality to apply rules defined in a `rules.json` file to mark emails as read or unread and move them to specified folders.

## Getting Started

To run the application, follow these steps:


### 1. Authenticate Google's Gmail API
Follow the below link to autheticate Google's Gmail api till creating credentias.json file.
https://developers.google.com/gmail/api/quickstart/python

### 2. Install Dependencies
1. Clone the project
2. Go to the project folder
3. Make sure python and pip are already installed
4. Create virtual environment
   python -m venv venv
5. Activate virtual environment
   .\venv\Scripts\activate
6. Install requirements
   pip install -r requirements.txt
7. Add the credentials.json file to backend_assignment
8. For installing postgres database follow the steps in the below link
   https://www.w3schools.com/postgresql/postgresql_install.php
   https://www.w3schools.com/postgresql/postgresql_getstarted.php

### 3. Run Project
To run the project execute below command in your virtual environment
  python main.py
For the first time it asks you to sign in to your mail id if not done before.
After the first run, token.json file will be created in the backend_assignment
Whenever the SCOPES inside the main.py file is changed, you need to delete the token.json file and create a new one

Note: Feel free to add or modify the rules present in config/rules.json file to test accordingly

