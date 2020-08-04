from django.contrib import admin
from .models import OrderItem, Order, Coupon, BillingAddress, ShippingAddress

class OrderAdmin(admin.ModelAdmin):
	list_display = ['customer', 'ordered', 'delivered']


admin.site.register(OrderItem)
admin.site.register(Order, OrderAdmin)
admin.site.register(Coupon)
admin.site.register(BillingAddress)
admin.site.register(ShippingAddress)
