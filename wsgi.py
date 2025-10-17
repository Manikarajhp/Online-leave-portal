from app import app
# Import routes so endpoints are registered when WSGI servers import this module
import routes  # noqa: F401

# Expose 'app' for WSGI servers (gunicorn, uwsgi, etc.) to use as 'wsgi:app'
