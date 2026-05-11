

Projekt v okviru podatkovnih baz 1.
Spletna stran na kateri lahko vsak uporabnik na lastno 'tablo' prilepi slike in naredi kolaž, ki ga drugi uporabniki lahko vidijo.

## Run Locally (No Docker)
1. Install Python 3.12
2. `pip install -r requirements.txt`
3. `python manage.py migrate`
4. `python manage.py runserver`

## Run with Docker
1. Install Docker
2. `docker-compose up --build`
3. Open http://localhost:8000

## Example Database
To use pre-made examples rename the Example_Database.sqlite3 to db.sqlite3.
Test profile passwords are 'X12341234', where X is the initial of the username.