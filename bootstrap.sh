#!/usr/bin/env bash

apt-get update > /dev/null
apt-get install -y git-core mongodb python-pip vim

# Upgrade Pip before installing anything with it.
sudo pip install -U pip
sudo pip install -U virtualenvwrapper

# Make virtualenvwrapper available to vagrant
echo "source /usr/local/bin/virtualenvwrapper.sh" >> /home/vagrant/.bashrc

# Set up a virtualenv. Make sure to use vagrant's home, otherwise it will be
# created in /root.
export WORKON_HOME=/home/vagrant/.virtualenvs
mkdir $WORKON_HOME
source /usr/local/bin/virtualenvwrapper.sh
mkvirtualenv -a /vagrant wheretomeetup
workon wheretomeetup

# Install the requirements. Without the `--pre` flag Pip would see pytz's
# releases as pre-release versions and fail.
pip install --upgrade --pre --requirement /vagrant/requirements.txt
