sudo -u postgres dropdb contra
sudo -u postgres createdb -O contra contra
rm -rf frontend/migrations frontend/static/repository/
python manage.py makemigrations frontend
python manage.py migrate
python manage.py loaddata frontend/fixtures/*
python manage.py createsuperuser
