#!/bin/sh
cd /home/ubuntu/river_ball/
source kkwork/bin/activate
NAME="river_ball_uwsgi"
if [ ! -n "$NAME" ];then
    echo "no arguments"
    exit;
fi

echo $NAME
ID=`ps -ef | grep "$NAME" | grep -v "$0" | grep -v "grep" | awk '{print $2}'`
echo $ID
echo "################################################"
for id in $ID
do
kill -9 $id
echo "kill $id"
done
echo  "################################################"
nohup uwsgi --ini river_ball_uwsgi.ini &

cd /home/ubuntu/hydrology_mgmt/
source kkwork/bin/activate
NAME="hydrology_mgmt_uwsgi"
if [ ! -n "$NAME" ];then
    echo "no arguments"
    exit;
fi

echo $NAME
ID=`ps -ef | grep "$NAME" | grep -v "$0" | grep -v "grep" | awk '{print $2}'`
echo $ID
echo "################################################"
for id in $ID
do
kill -9 $id
echo "kill $id"
done
echo  "################################################"
nohup uwsgi --ini hydrology_mgmt_uwsgi.ini &

sudo service nginx restart