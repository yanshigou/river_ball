#!/bin/sh

./restart.sh
sudo service nginx restart
uwsgi --ini river_ball_uwsgi.ini &