from django.urls import path
from django.contrib.auth import views as auth_views
from . import views 

app_name = 'store'

urlpatterns = [
    path('', views.index, name='index'),  # Home page
    path('signup/', views.signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='store/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='store/logout.html'), name='logout'),
    path('contact/', views.contact_view, name='contact'),
     path('', views.index, name='product_list'),  # List all products
    path('category/<slug:category_slug>/', views.product_list, name='product_list_by_category'),  # Filter products by category
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('cart/', views.cart_detail, name='cart_detail'),  # Corrected path for cart
    path('add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('payment/<int:order_id>/', views.process_payment, name='process_payment'),
    path('confirm-payment/', views.confirm_payment, name='confirm_payment'),
]
