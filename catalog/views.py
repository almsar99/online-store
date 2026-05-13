from django.shortcuts import render, get_object_or_404

from catalog.models import Product, Contact


def home(request):
    products = Product.objects.all()

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


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)

    context = {
        'product': product
    }

    return render(request, 'catalog/product_detail.html', context)
