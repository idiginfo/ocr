# OCR Install
Following instructions here:
```
https://chriswarrick.com/blog/2016/02/10/deploying-python-web-apps-with-nginx-and-uwsgi-emperor/
```
Important files:
 - /etc/uwsgi-emperor/vassals/ocr.ini
 - chown www-data.www-data ocr.ini
 ```
 [uwsgi]
 module = nginxwsgi
 socket = /home/idiginfo/ocr.sock
 chmod-socket = 666
 master = true
 chdir = /data/web/ocr
 binary-path = /data/web/ocr/venv/bin/uwsgi
 virtualenv = /data/web/ocr/venv
 uid = www-data
 gid = www-data
 processes = 5
 threads = 1
 plugins = python3,logfile
 logger = file:/data/web/ocr/logs/uwsgi.log
 ```
 - /etc/systemd/system/emperor.uwsgi.service
 ```
 [Unit]
 Description=uWSGI Emperor
 After=syslog.target
 
 [Service]
 #ExecStart=/root/uwsgi/uwsgi --ini /etc/uwsgi/emperor.ini
 ExecStart=/usr/bin/uwsgi --ini /etc/uwsgi-emperor/emperor.ini
 # Requires systemd version 211 or newer
 RuntimeDirectory=uwsgi
 Restart=always
 KillSignal=SIGQUIT
 Type=notify
 StandardError=syslog
 NotifyAccess=all
 
 [Install]
 WantedBy=multi-user.target
 ```
