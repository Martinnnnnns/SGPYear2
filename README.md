# Team Fox Small Group project

## Team members
The members of the team are:
- Bernardo Martins Lopes de Oliveira Guterres
- Omar Al-Mizan
- Saleh Alsubaie
- Ricky Gordon
- Mohammed Miah

## Project structure
The project is called `code_tutors`. It currently consists of a single app `tutorials` which provides a comprehensive tutoring management system with features for students, tutors, and administrators.

## Deployed version of the application
The deployed version of the application can be found at [arifm1ah.pythonanywhere.com](arifm1ah.pythonanywhere.com).

## The administrative interfaces can be found at:
[arifm1ah.pythonanywhere.com/dashboard](arifm1ah.pythonanywhere.com/dashboard) -while logged in as a user with admin privileges such as @johndoe.

## Installation instructions
To install the software and use it in your local development environment, you must first set up and activate a local development environment.  From the root of the project:

```
$ virtualenv venv
$ source venv/bin/activate
```

Install all required packages:

```
$ pip3 install -r requirements.txt
```

Migrate the database:

```
$ python3 manage.py migrate
```

Seed the development database with:

```
$ python3 manage.py seed
```

Run all tests with:
```
$ python3 manage.py test
```

## Sources
The packages used by this application are specified in `requirements.txt`
