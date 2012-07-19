#!/bin/bash
DATE=`date +%Y-%m-%d`
ERROR_LOG=/var/www/log/djkarma-error-$DATE.log
ACCESS_LOG=/var/www/log/djkarma-access-$DATE.log
./manage.py run_gunicorn --daemon --access-logfile $ACCESS_LOG --error-logfile $ERROR_LOG
