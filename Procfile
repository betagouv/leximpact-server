flasks: FLASK_ENV=production HOST=0.0.0.0 python ./server/app.py
worker: gunicorn --chdir server app:app --bind 0.0.0.0:5000 --workers=9
thread: gunicorn --chdir server app:app --bind 0.0.0.0:5000 --workers=3 --threads=3 --worker-class=gthread
gevent: gunicorn --chdir server app:app --bind 0.0.0.0:5000 --workers=3 --worker-connections=1000 --worker-class=gevent
chroot: HOST=0.0.0.0 python ./server/cherrypy.py
bjoern: HOST=0.0.0.0 python ./server/bjorn.py
tornad: HOST=0.0.0.0 python ./server/tournedo.py
