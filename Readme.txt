Steps to get the program running
1. Install redis server.
2. pip install requirements.txt
3. python manage.py makemigrations
4. python manage.py migrate
5. python manage.py runserver

Start celery
1. celery -A FileCompare worker --loglevel=info

