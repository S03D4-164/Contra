#sudo -u postgres dropdb contra
sudo -u postgres createdb -O contra contra
rm -rf Contra/frontend/migrations Contra/frontend/static/repository/
python manage.py makemigrations Contra.frontend
python manage.py migrate
python manage.py loaddata Contra/frontend/fixtures/*
python manage.py createsuperuser
