from django.db import models
from django.shortcuts import get_object_or_404
from django.core.validators import MinValueValidator
from vero_fasion.models import Item, Exchange, Color
from decimal import Decimal


class BillingAddress(models.Model):
	customer = models.CharField(max_length=100)
	first_name = models.CharField(max_length=20)
	last_name = models.CharField(max_length=20)
	address = models.CharField(max_length=100)
	city = models.CharField(max_length=20)
	postal_code = models.CharField(max_length=20)
	country = models.CharField(max_length=20, default='Poland')
	email = models.EmailField(max_length=70)
	phone_number = models.CharField(max_length=12)

	def __str__(self):
		return self.first_name + ' ' + self.last_name

	def fullname(self):
		return self.first_name + ' ' + self.last_name

	def fulladdress(self):
		return self.address + ', ' + self.postal_code + ', ' + self.city

class ShippingAddress(models.Model):
	customer = models.CharField(max_length=100)
	first_name = models.CharField(max_length=20)
	last_name = models.CharField(max_length=20)
	address = models.CharField(max_length=100)
	city = models.CharField(max_length=20)
	postal_code = models.CharField(max_length=20)
	country = models.CharField(max_length=20, default='Poland')
	email = models.EmailField(max_length=70)
	phone_number = models.CharField(max_length=12)
	def __str__(self):
		return self.first_name + ' ' + self.last_name

	def fullname(self):
		return self.first_name + ' ' + self.last_name

	def fulladdress(self):
		return self.address + ', ' + self.postal_code + ', ' + self.city

class Coupon(models.Model):
	code = models.CharField(max_length=20)
	amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])

	def __str__(self):
		return self.code

	def get_euro_amount(self):
		rate = get_object_or_404(Exchange)
		return round(self.amount / rate.euro, 2)


class OrderItem(models.Model):
	customer = models.CharField(max_length=100)
	ordered = models.BooleanField(default=False)
	item = models.ForeignKey(Color, on_delete=models.CASCADE)
	quantity = models.PositiveIntegerField(default=1)

	def __str__(self):
		return f"{self.quantity} of {self.get_detail().get('title')} - {self.item.produc_color}"

	def get_exchange_rate(self):
		return get_object_or_404(Exchange)

	def get_item_detail(self):
		return get_object_or_404(Item, color=self.item)

	def get_detail(self):
		rate = self.get_exchange_rate()
		parent = self.get_item_detail()
		sale_price = parent.sale_price
		if parent.sale_price == None:
			sale_price = 0

		return {
			'this_item': parent,
			'title': parent.title,
			'total_price': self.quantity * parent.price,
			'total_discount_price': self.quantity * sale_price,
			'euro_price': round(parent.price / rate.euro, 2),
			'euro_whole_price': round(parent.whole_price / rate.euro, 2),
			'euro_discount_price': round(sale_price / rate.euro, 2),
			'euro_total_price': round(self.quantity * parent.price / rate.euro, 2),
			'euro_total_discount_price': round(self.quantity * sale_price / rate.euro, 2)
		}

	def get_wholeSale_total(self):
		parent = self.get_item_detail()
		return self.quantity * parent.whole_price

	def get_wholeSale_euro_total(self):
		rate = self.get_exchange_rate()
		parent = self.get_item_detail()
		return round(self.quantity * parent.whole_price / rate.euro, 2)

#-------------------------------------------------------------------------------------------------
class Order(models.Model):
	ref_code = models.CharField(max_length=100, blank=True, null=True)
	customer = models.CharField(max_length=100)
	items = models.ManyToManyField(OrderItem)
	start_date = models.DateTimeField(auto_now_add=True)
	ordered_date = models.DateTimeField()
	ordered = models.BooleanField(default=False)
	delivered = models.BooleanField(default=False)
	promotion = models.ForeignKey(Coupon, on_delete=models.SET_NULL, blank=True, null=True)
	billing_address = models.ForeignKey(BillingAddress, on_delete=models.SET_NULL, blank=True, null=True)
	shipping_address = models.ForeignKey(ShippingAddress, on_delete=models.SET_NULL, blank=True, null=True)

	def __str__(self):
		return self.customer

	def get_all_total(self):
		total = Decimal(0)
		euro_total = Decimal(0)

		for order_item in self.items.all():
			if order_item.get_detail().get('this_item').sale_price:
				total += order_item.get_detail().get('total_discount_price')
				euro_total += order_item.get_detail().get('euro_total_discount_price')
			else:
				total += order_item.get_detail().get('total_price')
				euro_total += order_item.get_detail().get('euro_total_price')
	
		return {'all_total': total, 'all_total_euro': euro_total}

	#get total amount of order for whole buyer
	def get_all_whole_total(self):
		total = Decimal(0)
		euro_total = Decimal(0)
		for order_item in self.items.all():		
			total += order_item.get_wholeSale_total()
			euro_total += order_item.get_wholeSale_euro_total()
		return {'all_total': total, 'all_total_euro': euro_total}

	#minuse amount of coupon from total amount of order
	def get_coupon_total(self):
		total = self.get_all_total().get('all_total')
		euro_total = self.get_all_total().get('all_total_euro')
		if self.promotion:
			total -= self.promotion.amount
			euro_total -= self.promotion.get_euro_amount()
		return {'coupon_total': total, 'coupon_total_euro': euro_total}

	#minuse amount of coupon from total amount of order whole buyer
	def get_coupon_total_whole(self):
		total = self.get_all_whole_total().get('all_total')
		euro_total = self.get_all_whole_total().get('all_total_euro')
		if self.promotion:
			total -= self.promotion.amount
			euro_total -= self.promotion.get_euro_amount()
		return {'coupon_total': total, 'coupon_total_euro': euro_total}


		
