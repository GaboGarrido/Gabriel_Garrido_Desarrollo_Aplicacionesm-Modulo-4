import os, django, json
os.environ.setdefault('DJANGO_SETTINGS_MODULE','galileo_project.settings')
django.setup()
from django.test import Client

client = Client()
res = client.get('/api/dashboard/')
print('status', res.status_code)
print(res.content.decode())
