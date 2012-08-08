#!/bin/bash

# Karma Notes (Django Ver.) start/stop script Alpha 0.01 Django Ver.
#
# Copyright (C) 2012  Robert Call <bob@finalsclub.org>
# Copyright (c) 2012 Finalsclub Foundation

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


# Env. Var.

BETA_SRC=/var/www/beta
PROD_SRC=/var/www/djKarma

# Defined server ports for each instance.

BETA_PORT=7000
PROD_PORT=8000

BETA_PID=/var/www/pid/karma_beta.pid
PROD_PID=/var/www/pid/karma_prod.pid


beta() {

	$BETA_SRC/manage.py run_gunicorn 127.0.0.1:$BETA_PORT --daemon
}

prod() {

	$PROD_SRC/manage.py run_gunicorn 127.0.0.1:$PROD_PORT --daemon
}

kill_beta() {
	kill $BETA_PID
}

kill_prod() {
	kill  cat $PROD_PID
}

case "$1" in
        start)
                echo "Starting production..."
		prod
                ;;
	beta)
		echo "starting beta..."
		beta
		;;

	stop)
		echo "Killing prod server..."
		kill_prod
		;;
	stop_beta)
		echo "killing beta server..."
		kill_beta
		;;
	*)

		echo "djkarma (start|stop|beta|stop_beta)"
		;;
esac

