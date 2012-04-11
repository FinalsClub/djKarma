#!/bin/bash
# Karma Notes (Django Ver.) dev. env deployment script Alpha 0.03a Django Ver.
# Finals Club MongoDB backup script
#
# Copyright (C) 2012  Robert Call
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


DJANGO_VER=1.4
SETUP_DIR=/tmp/fc_dev_env
KARMA_HOME=/var/www/djKarma
WEB_APP_ROOT=/var/www
GIT_REPO=https://github.com/FinalsClub/djKarma.git

install_django() {
	cd $SETUP_DIR
	wget http://www.djangoproject.com/download/$DJANGO_VER/tarball/
	mv index.html django-$DJANGO_VER.tar.gz
	tar fxzv django-$DJANGO_VER.tar.gz
	cd Django-$DJANGO_VER
	python setup.py install
}

setup_env() {
	mkdir $WEB_APP_ROOT
	mkdir $SETUP_DIR
}

get_knotes() {
	cd $WEB_ROOT
	git clone $GIT_REPO

}

clean_up() {
	echo "Cleaning up $SETUP_DIR ...\n"
	rm -fr $SETUP_DIR
}

apt-get install git-core g++ python-pip libssl-dev curl make haproxy ruby rubygems mongodb-server # Will be replaced with OS Ver / check for Fedora, Deb, OS X and BSD.
setup_env
install_django
get_knotes
clean_up

echo 'Please run $KARMA_HOME /manage.py runserver&'
