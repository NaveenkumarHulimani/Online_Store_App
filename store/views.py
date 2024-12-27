from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from .models import Product, Category
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Order, OrderItem
from .forms import OrderCreateForm
from cart.cart import Cart
from django.contrib import messages
import stripe
from django.conf import settings
from django.http import JsonResponse

# Create your views here.

def index(request):
    """
    Home page that displays signup and login options and product list.
    """
    products = Product.objects.all()
    return render(request, 'store/index.html', {'products': products})

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()  # Save the new user to the database
            login(request, user)  # Log the user in automatically
            return redirect('store:product_list')  # Redirect to the product list page or home page
    else:
        form = UserCreationForm()
    return render(request, 'store/signup.html', {'form': form})

def contact_view(request):
    print("Contact view accessed!")
    return render(request, 'store/contact.html')

def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)  # Show only available products

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)

    return render(request, 'store/product_list.html', {'category': category, 'categories': categories, 'products': products})

# Display product detail
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'store/product_detail.html', {'product': product})

def cart_detail(request):
    # Create an instance of the cart
    cart = Cart(request)
    return render(request, 'cart/cart_detail.html', {'cart': cart})

@login_required
def add_to_cart(request, product_id):
    """
    Add a product to the shopping cart.
    If the user is not logged in, redirect to login.
    """
    if not request.user.is_authenticated:
        return redirect('store:login')  # Redirect to login if not authenticated
    
    product = get_object_or_404(Product, id=product_id)
    cart = Cart(request)
    cart.add(product)
    messages.success(request, f'{product.name} has been added to your cart.')
    return redirect('store:product_list')

def remove_from_cart(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('cart:cart_detail')


# Step 1: Show Checkout Form
@login_required
def checkout(request):
    cart = Cart(request)
    if cart.get_total_price() == 0:
        return redirect('store:cart_detail')  # Redirect if cart is empty

    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            # Create order object
            order = form.save(commit=False)
            order.user = request.user
            order.total = cart.get_total_price()
            order.save()

            # Add order items to the order
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    quantity=item['quantity'],
                    price=item['product'].price
                )

            # Clear the cart after the order is created
            cart.clear()

            # Redirect to payment page or confirmation page
            return redirect('store:order_confirmation', order_id=order.id)
    else:
        form = OrderCreateForm()

    return render(request, 'store/checkout.html', {'form': form, 'cart': cart})

# Step 2: Order Confirmation (After Order is Created)
def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'store/order_confirmation.html', {'order': order})

# Step 3: Payment Processing (this is a placeholder)
def process_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    # Here you would integrate with a payment gateway like Stripe or PayPal
    # For simplicity, we'll assume payment is successful
    order.paid = True
    order.save()

    messages.success(request, "Payment successful! Your order is confirmed.")
    return redirect('store:order_confirmation', order_id=order.id)

# Set the Stripe API key from settings
stripe.api_key = settings.STRIPE_SECRET_KEY

def process_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    # Check if the order belongs to the logged-in user (if you have user authentication)
    if order.user != request.user:
        return redirect('store:product_list')

    # Create a Stripe PaymentIntent
    try:
        intent = stripe.PaymentIntent.create(
            amount=int(order.total * 100),  # amount in cents
            currency='usd',
            metadata={'order_id': order.id},
        )
        
        # Send the client secret of the PaymentIntent to the front end for the payment form
        return render(request, 'store/payment.html', {
            'intent': intent,
            'stripe_public_key': settings.STRIPE_TEST_PUBLIC_KEY
        })
    except stripe.error.StripeError as e:
        return JsonResponse({'error': str(e)})

def confirm_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    if order.user != request.user:
        return redirect('store:product_list')
    
    # Confirm the payment intent with the payment method on the frontend
    payment_intent_id = request.POST.get('payment_intent_id')
    try:
        payment_intent = stripe.PaymentIntent.confirm(payment_intent_id)

        # Update order status to 'Paid'
        order.status = 'Paid'
        order.save()

        # Redirect to a success page
        return redirect('store:order_confirmation', order_id=order.id)
    except stripe.error.StripeError as e:
        return JsonResponse({'error': str(e)})

