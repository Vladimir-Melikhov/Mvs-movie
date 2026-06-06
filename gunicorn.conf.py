import multiprocessing
import os

bind = "0.0.0.0:8000"
backlog = 2048

workers = 4
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
timeout = 120
keepalive = 5

accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

proc_name = "videohub_gunicorn"

daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None
