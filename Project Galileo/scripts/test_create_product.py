import os, django, json
os.environ.setdefault('DJANGO_SETTINGS_MODULE','galileo_project.settings')
django.setup()
from sales.models import Product
from django.test import Client

def run_test():
    Product.objects.filter(name='InvProdTest').delete()
    client = Client()
    payload = {'name':'InvProdTest','price':15.5,'stock':12,'reorder_point':3}
    resp = client.post('/api/products/', data=json.dumps(payload), content_type='application/json')
    print('status', resp.status_code)
    try:
        p = Product.objects.get(name='InvProdTest')
        print('Created product:', p.id, p.name, p.price, p.stock, p.reorder_point)
    except Product.DoesNotExist:
        print('Product not created')

if __name__ == '__main__':
    run_test()
