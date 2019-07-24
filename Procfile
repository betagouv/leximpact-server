web: gunicorn --chdir ./server app:app --bind 0.0.0.0:$PORT --workers=3
postdeploy: alembic upgrade head
