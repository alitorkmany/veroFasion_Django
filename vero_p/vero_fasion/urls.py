from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name='vero-home'),
    path('search/', views.get_items_queryset, name='vero-search'),

    path('women-products/', views.women_page, name='vero-woman'),
    path('women-products/<variety>/', views.women_catagory, name='vero-woman'),

    path('men-products/', views.men_page, name='vero-man'),
    path('men-products/<variety>/', views.men_catagory, name='vero-man'),

    path('kid-products/', views.kid_page, name='vero-kid'),

    path('sale-products/', views.sale_page, name='vero-sale'),
    path('sale-products/<variety>/', views.sale_catagory, name='vero-sale'),

    path('whole-sale-products/<location>/', views.whole_sale_page, name='vero-whole-sale'),

    path('privacy/', views.privacy, name='vero-privacy'),
    path('regulation/', views.regulation, name='vero-regulation'),

    ##################### Sub Routes ###########################
   	path('detail/<id>/', views.detail, name='vero-detail'),
    path('detail-h/<id>/', views.whole_detail, name='vero-whole-detail'),
   	path('product-detail/', views.getDetail, name='vero-ajax'),
    path('subscription/', views.subscription, name='vero-subscription'),
    path('login_required/', views.required_login, name='vero-required'),
] 
