pip3 install pandas
pip3 install numpy
pip3 install matplotlib
pip3 install wikipedia
gunicorn --bind=0.0.0.0 --timeout 1800 --chdir "pairtradeaptml/web-application" main:app