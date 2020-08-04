from django.urls import path, include
from . import views
from .views import CheckOut, Shipping_Address

urlpatterns = [
    path('add-to-cart/', views.add_to_cart, name='addtocart'),
    path('cart-item-count/', views.cart_item_counter, name='car-titem-count'),
    path('order-summary/', views.order_summary, name='order-summary'),
    path('add-item/<id>/', views.item_plus_cart, name='add-item'),
    path('remove-item/<id>/', views.item_minus_cart, name='remove-item'),
    path('delete-item/<id>/', views.item_remove_cart, name='delete-item'),
    path('add-coupon/', views.add_coupon, name='add-coupon'),
    path('check-out/', CheckOut.as_view(), name='check-out'),
    path('shipping-address/', Shipping_Address.as_view(), name='shipping-address'),
    path('stripe/webhook', views.webhook_stripe, name='stripe-webhook'),
    path('success/', views.finish, name='finish'),
] 
