pip3 install -r "pairtradeaptml/web-application"/requirements.txt
gunicorn --bind=0.0.0.0 --timeout 1800 --chdir "pairtradeaptml/web-application" main:app