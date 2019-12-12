# -*- coding: utf-8 -*-

from datetime import datetime
from fabric.api import *
from fabvenv import virtualenv

# 登录用户和主机名：
env.user = 'ubuntu'
env.password = 'Cmx170904'
env.hosts = ['106.54.217.74']
pack_name = 'deploypack_river_ball.tar.gz'


def pack():
    ' 定义一个pack任务 '
    # 打一个tar包：
    local('del %s' % pack_name)
    local('md ..\pack_tmp')
    local('xcopy /e /s .\* ..\pack_tmp')
    with lcd('..\pack_tmp'):
        local('tar -czvf ../river_ball/%s --exclude *.pyc --exclude fabfile.py '
              '--exclude 00* --exclude *.tar.gz --exclude README.md --exclude all_devices_info.txt '
              '--exclude __pycache__/ '
              '--exclude static/ --exclude .idea/ --exclude .git/ --exclude *.rar  ./*' % pack_name)
    local('rd /s /q ..\pack_tmp')


def deploy():
    ' 定义一个部署任务 '
    tag = datetime.now().strftime('%y.%m.%d_%H.%M.%S')
    print(env.host)
    remote_work_dir = ''
    if env.host == '106.54.217.74':
        remote_work_dir = '/home/ubuntu/river_ball/'
    else:
        exit(1)

    remote_tmp_tar = '/tmp/%s' % pack_name
    run('rm -f %s' % remote_tmp_tar)
    # 上传tar文件至远程服务器：
    put(pack_name, remote_tmp_tar)
    # 备份远程服务器工程
    # back_tar_name = '/home/ubuntu/www/backup/cmxsite_backup_%s.tar.gz' % tag
    # run('tar -czvf %s /home/ubuntu/www/cmxsite/*' % back_tar_name)
    # 删除原有工程
    # run('rm -rf /home/ubuntu/www/cmxsite/*')
    # 解压：
    run('tar -xzvf %s -C %s' % (remote_tmp_tar, remote_work_dir))
    run('mv %sother/settings.py %s/river_ball/settings.py' % (remote_work_dir, remote_work_dir))
    run('mv %sother/ball_nginx.conf %s/river_ball_nginx.conf' % (remote_work_dir, remote_work_dir))
    run('mv %sother/ball_uwsgi.ini %s/river_ball_uwsgi.ini' % (remote_work_dir, remote_work_dir))
    run('mv %sother/uwsgi_params %s/uwsgi_params' % (remote_work_dir, remote_work_dir))
    run('rm -rf %sother' % remote_work_dir)
    with cd(remote_work_dir):
        with virtualenv('/home/ubuntu/river_ball/kkwork'):
            run('python manage.py makemigrations')
            run('python manage.py migrate')
            run('chmod a+x ./restart.sh')
            run('sh ./restart.sh', pty=False)
            # run('sudo service nginx restart')
            run('sleep 5')
