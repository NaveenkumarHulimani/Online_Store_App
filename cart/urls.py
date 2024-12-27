from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.cart_detail, name='cart_detail'),  # View Cart
    path('add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),  # Add Product to Cart
    path('remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),  # Remove Product from Cart
]
