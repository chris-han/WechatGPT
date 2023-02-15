# Gunicorn configuration file
# Use 9 workers to serve requests (default: 1 worker)
workers = 9
# Sets the number of threads for handling requests (default: 1 thread)
threads = 1
# An address to bind the Gunicorn server to
bind = '0.0.0.0:5000'
# Specify worker class
worker_class = 'gevent'
keepalive = 2
timeout = 30