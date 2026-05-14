from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect

from catalog.forms import ProductForm
from catalog.models import Product, Contact


def home(request):
    products = Product.objects.all()

    paginator = Paginator(products, 2)

    page_number = request.GET.get('page')

    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj
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


def product_create(request):

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            return redirect('catalog:home')

    else:
        form = ProductForm()

    context = {
        'form': form
    }

    return render(request, 'catalog/product_form.html', context)
