git clone https://github.com/S03D4-164/thug.git
cp -r ./thug/src/Logging files
git clone -b debug https://github.com/S03D4-164/Ghost.py.git
cp -r ./Ghost.py/ghost files
docker build  -t "contra:latest" . 
