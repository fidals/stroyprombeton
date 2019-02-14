import multiprocessing
import os
import subprocess


default_workers = multiprocessing.cpu_count() * 2 + 1
workers = os.environ.get('WEB_CONCURRENCY', default_workers)
worker_class = 'sync'
max_requests = 300
max_requests_jitter = 300
errorlog = '-'


def on_starting(server):
    subprocess.run(['python', 'manage.py', 'check'], check=True)
