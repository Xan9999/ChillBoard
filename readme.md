## Run Locally (No Docker)
1. Install Python 3.12
2. `pip install -r requirements.txt`
3. `python manage.py migrate`
4. `python manage.py runserver`

## Run with Docker
1. Install Docker
2. `docker-compose up --build`
3. Open http://localhost:8000