from django.contrib import admin
from .models import Item, Color, Exchange, Subscription

class MemebershipInline(admin.StackedInline):
	model = Item.color.through
	extra = 0
	list_display = ['produc_color', 'stock']


class ColorAdmin(admin.ModelAdmin):
    inlines = [MemebershipInline,]


class ItemAdmin(admin.ModelAdmin):
	list_display = ['title', 'price', 'sale_price']
	
	inlines = [MemebershipInline,]
	exclude = ('color',)

	def get_queryset(self, request):
		queryset = super(ItemAdmin, self).get_queryset(request)
		queryset = queryset.order_by('title')
		return queryset

# Register your models here.
admin.site.register(Item, ItemAdmin)
admin.site.register(Color)
admin.site.register(Exchange)
admin.site.register(Subscription)


