# Flask AWS Scaffolding

install [Docker](https://docs.docker.com/)

install [Nginx](http://nginx.org/en/docs/install.html)

add this entry to your host machine's /etc/hosts file

    127.0.0.1	entropealabs.dev auth.entropealabs.dev

install fig, not in a virtualenv, it needs sudo to talk to Docker (If you know how to give sudo access to a module installed in virtualenv, I would love to hear it)

    sudo pip install fig==1.0.1

Edit config/nginx.conf, change this line

    alias /app/views/static;

to point to the static directory in the `flask-aws-scaffolding` git checkout (you may need to adjust the permissions of the static files, as well as their parent directories, so that nginx has access to open/read the files)

    alias /home/entropealabs/dev/flask-aws-scaffolding/flaskaws/views/static;

copy the nginx.conf file to the nginx conf directory

    sudo cp ./config/nginx.conf /etc/nginx/sites-enabled

remove the default conf file (don't worry, it's just a symlink, the file still exists in sites-available)

    sudo rm /etc/nginx/sites-enabled/default

restart nginx

    sudo service nginx restart

make sure docker is running...

    ps aux | grep docker

you should seee somthing like this

    root     25919  0.0  0.2 2174776 32720 ?       Ssl  Feb18   5:55 /usr/bin/docker -d

from within the base directory of flask-aws-scaffolding run

    sudo fig up

grab some coffee... it's going to download a few hundred MB of image files, but everything should be working when you get back...

assuming everything ran ok, you should be able to see some log files

    INFO:root:Running
    web_1           | [2015-02-25 02:05:24 +0000] [8] [INFO] Starting gunicorn 19.1.1
    web_1           | [2015-02-25 02:05:24 +0000] [8] [DEBUG] Arbiter booted
    web_1           | [2015-02-25 02:05:24 +0000] [8] [INFO] Listening at: http://0.0.0.0:8000 (8)
    web_1           | [2015-02-25 02:05:24 +0000] [8] [INFO] Using worker: gevent
    web_1           | [2015-02-25 02:05:24 +0000] [19] [INFO] Booting worker with pid: 19
    mongodb_1       | 2015-02-25T02:05:24.784+0000 [conn1] end connection 172.17.8.210:59764 (1 connection now open)
    web_1           | 2015-02-25 02:05:24,784 INFO exited: init_dbs (exit status 0; expected)

you may see some errors as the databases are coming up and the app is waiting for them to be available.

you should now be able to point your browser to http://entropealabs.dev

we will be creating another readme for using the included terraform configurations to deploy to a AWS VPC (Amazon Web Service | Virtual Private Cloud)
