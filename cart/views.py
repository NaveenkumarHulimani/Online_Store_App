from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from store.models import Product
from .cart import Cart

@require_POST
def add_to_cart(request, product_id):
    """Add a product to the cart."""
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.add(product)
    return redirect('cart:cart_detail')

def cart_detail(request):
    """Display the cart details."""
    cart = Cart(request)
    return render(request, 'cart/cart_detail.html', {'cart': cart})

def remove_from_cart(request, product_id):
    """Remove a product from the cart."""
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('cart:cart_detail')
