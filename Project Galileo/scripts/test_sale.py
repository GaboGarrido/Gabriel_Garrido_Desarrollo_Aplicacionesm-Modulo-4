import os, django, json
os.environ.setdefault('DJANGO_SETTINGS_MODULE','galileo_project.settings')
django.setup()
from sales.models import Product, Customer, Sale
from django.test import Client

def run_test():
    # Clean up existing test records
    Sale.objects.filter(product__name='TestProd').delete()
    Customer.objects.filter(name='TestCust').delete()
    Product.objects.filter(name='TestProd').delete()

    p = Product.objects.create(name='TestProd', price=10.0, stock=5)
    Customer.objects.create(name='TestCust', email='c@test')
    client = Client()
    payload = {'customer': {'name': 'TestCust', 'email': 'c@test'}, 'product': {'name': 'TestProd', 'price':10.0}, 'quantity':2}
    resp = client.post('/api/sales/', data=json.dumps(payload), content_type='application/json')
    print('status', resp.status_code)
    print('resp', resp.content.decode())
    print('Sales in DB:', Sale.objects.filter(product__name='TestProd').count())
    s = Sale.objects.filter(product__name='TestProd').first()
    if s:
        print('Sale:', s.id, s.customer.name, s.product.name, s.quantity, float(s.total))
    else:
        print('No sale object created')
    p.refresh_from_db()
    print('Product stock after sale:', p.stock)

if __name__ == '__main__':
    run_test()
