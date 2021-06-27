cd /var/www/personal
gunicorn --workers 3 --bind :23000 --access-logfile tmp/access.log --error-logfile tmp/error.log wsgi:app --reload
