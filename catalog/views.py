from django.shortcuts import render

from catalog.models import Product, Contact



def home(request):
    products = Product.objects.order_by('-created_at')[:5]

    print(products)

    context = {
        'products': products
    }

    return render(request, 'catalog/home.html', context)



def contacts(request):
    contacts_list = Contact.objects.all()

    context = {
        'contacts_list': contacts_list
    }

    return render(request, 'catalog/contacts.html', context)
