#!/bin/bash

DIR=`echo $(cd "$(dirname "$0")"; pwd)`
LOGDIR="${DIR}/logs"

sourcelogpath="${DIR}/river_ball_uwsgi.log"
touchfile="${DIR}/.touchforlogrotate"


DATE=`date +"%Y%m%d_%H%M%S"`
echo $DATE
destlogpath="${LOGDIR}/river_ball_uwsgi_${DATE}.log"

mv $sourcelogpath $destlogpath
touch $touchfile