sudo -u postgres dropdb contra
sudo -u postgres createdb -O contra contra
rm -rf Contra/frontend/migrations
rm -rf Contra/frontend/static/repository/
rm -rf Contra/backend/static/artifacts/ghost
rm -rf Contra/backend/static/artifacts/thug
#mkdir -p Contra/backend/static/artifacts
sudo chown -R 1000.100 Contra/backend/static/artifacts && sudo chmod -R 2775 Contra/backend/static/artifacts
python manage.py makemigrations frontend
python manage.py migrate
python manage.py loaddata Contra/frontend/fixtures/*
python manage.py createsuperuser
