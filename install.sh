curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py

sudo python ./get-pip.py
sudo add-apt-repository ppa:eugenesan/ppa
sudo apt-get update
sudo apt-get -y install jq
sudo apt-get -y install wkhtmltopdf
sudo apt-get -y install xvfb
sudo pip install jmespath
sudo pip install boto3

cat pk.txt >> ~/.ssh/authorized_keys
chmod +x gs*



