from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import View
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.http import HttpResponse
from django.conf import settings
from django.template.loader import render_to_string
from vero_fasion.models import Item, Exchange, Color
from .models import Order, OrderItem, Coupon, BillingAddress, ShippingAddress
from .utils import send_email
from .form import CouponForm
import random
import string
import stripe
import json


def add_to_cart(request):
	count = 0
	if request.GET.get('count', None) != "":
		count = int(request.GET.get('count'))

	id = request.GET.get('id', None)
	item = get_object_or_404(Color, id=id) #get the item

	if not request.session.get('customer', None):
		request.session.set_expiry(60 * 60 * 24)
		customer = request.session['customer'] = ''.join(random.choice(string.ascii_lowercase) for i in range(10))
		print('age of session: ' + str(request.session.get_expiry_age()))
		order_item, create = OrderItem.objects.get_or_create(item=item, customer=customer, ordered=False) #create object of the item
		order = Order.objects.create(customer=customer, ordered_date=timezone.now())
		order.items.add(order_item)
		if count != 0:
			order_item.quantity = count
			order_item.save()
		count = 1
	else:
		customer = request.session['customer']
		order_item, create = OrderItem.objects.get_or_create(item=item, customer=customer, ordered=False) #create object of the item
		order_qs = Order.objects.filter(customer=customer, ordered=False)
		if order_qs.exists():
			order = order_qs[0]
			# check if the order item is in the order
			if order.items.filter(item__id=item.id).exists():

				if count != 0:
					order_item.quantity += count
				else:
					order_item.quantity += 1
				order_item.save()
				count = order_qs[0].items.count()
			else:
				if count != 0:
					order_item.quantity = count
					order_item.save()
				order.items.add(order_item)
				count = order_qs[0].items.count()
		else:
			order = Order.objects.create(customer=customer, ordered_date=timezone.now())
			order.items.add(order_item)
			count = 1

	data = { 'count': count }
				
	return JsonResponse(data)


def cart_item_counter(request):
	count = 0
	if request.session.get('customer', None):
		customer = request.session['customer']
		qs = Order.objects.filter(customer=customer, ordered=False)
		if qs.exists():
			count = qs[0].items.count()
	data = { 'count': count }
	return JsonResponse(data)


def order_summary(request):
	if request.session.get('customer', None):
		try:
			customer = request.session['customer']
			order = Order.objects.get(customer=customer, ordered=False)
			context = { 'order': order, 'form': CouponForm(), 'title': 'Summary' }
			return render(request, 'shopping_cart/summary.html', context)
		except ObjectDoesNotExist:
			messages.info(request, 'Nie masz aktywnego zamówienia')
			return redirect('/')
	else:
		messages.info(request, 'Nie masz aktywnego zamówienia')
		return redirect('/')


def item_plus_cart(request, id):
	item = get_object_or_404(Color, id=id) #get the item

	if request.session.get('customer', None):
		customer = request.session['customer']
		order_item, create = OrderItem.objects.get_or_create(item=item, customer=customer, ordered=False) #create object of the item
		order_qs = Order.objects.filter(customer=customer, ordered=False)
		if order_qs.exists():
			order = order_qs[0]
			# check if the order item is in the order
			if order.items.filter(item__id=item.id).exists():
				#check for quantity of stock
				if order_item.quantity == order_item.item.stock:
					messages.info(request, 'Produkt wyczerpał się w magazynie')
					return redirect('order-summary')

				order_item.quantity += 1
				order_item.save()
			else:
				order.items.add(order_item)
	return redirect('order-summary')


def item_minus_cart(request, id):
	item = get_object_or_404(Color, id=id) #get the item

	if request.session.get('customer', None):
		customer = request.session['customer']
		order_qs = Order.objects.filter(customer=customer, ordered=False)
		if order_qs.exists():
			order = order_qs[0]
			# check if the order item is in the order
			if order.items.filter(item__id=item.id).exists():
				order_item = OrderItem.objects.filter(item=item, customer=customer, ordered=False)[0]
				if order_item.quantity > 1:
					order_item.quantity -= 1
					order_item.save()
				else:
					order.items.remove(order_item)
					order_item.delete()
					messages.info(request, "Produkt został usunięty z koszyka")
	return redirect('order-summary')


def item_remove_cart(request, id):
	item = get_object_or_404(Color, id=id) #get the item

	if request.session.get('customer', None):
		customer = request.session['customer']
		order_qs = Order.objects.filter(customer=customer, ordered=False)
		if order_qs.exists():
			order = order_qs[0]
			# check if the order item is in the order
			if order.items.filter(item__id=item.id).exists():
				order_item = OrderItem.objects.filter(item=item, customer=customer, ordered=False)[0]
				order.items.remove(order_item)
				order_item.delete()
				messages.info(request, "Produkt został usunięty z koszyka")
					
	return redirect('order-summary')


def get_coupon(request, code):
	try:
		coupon = Coupon.objects.get(code=code)
		return coupon
	except ObjectDoesNotExist:
		messages.info(request, 'Ten kupon nie istnieje')
		return redirect('order-summary')


def add_coupon(request):
	if request.method == 'POST':
		form = CouponForm(request.POST or None)
		if form.is_valid():
			try:
				code = form.cleaned_data.get('code')
				customer = request.session['customer']
				order = Order.objects.get(customer=customer, ordered=False)
				order.promotion = get_coupon(request, code)
				order.save()
				return redirect('order-summary')
			except ObjectDoesNotExist:
				messages.info(request, 'Nie masz aktywnego zamówienia')
				return redirect('order-summary')


class CheckOut(View):
	def get(self, request, *args, **kwargs):
		if self.request.session.get('customer', None):
			try:
				customer = self.request.session['customer']
				order = Order.objects.get(customer=customer, ordered=False)

				amount = 0
				if request.user.is_authenticated:
					amount = int(order.get_coupon_total_whole().get('coupon_total')) * 100
				else:
					amount = int(order.get_coupon_total().get('coupon_total')) * 100

				# Set your secret key: remember to change this to your live secret key in production
				# See your keys here: https://dashboard.stripe.com/account/apikeys
				stripe.api_key = settings.STRIPE_SECRET_KEY

				intent = stripe.PaymentIntent.create(
				  amount=amount,
				  currency='PLN',
				  metadata={'customer': customer}
				)
		
				context = { 'order': order, 
				'clientSecret': intent.client_secret,
				'PUB_KEY': settings.STRIPE_PUBLISHABLE_KEY,
				'title': 'Checkout'
				}

				return render(self.request, 'shopping_cart/checkout.html', context)
			except ObjectDoesNotExist:
				messages.info(self.request, 'Nie masz aktywnego zamówienia')
				return redirect('/')
		else:
			messages.info(self.request, 'Nie masz aktywnego zamówienia')
			return redirect('/')

	def post(self, *args, **kwargs):
		if self.request.session.get('customer', None):
			try:
				customer = self.request.session['customer']
				if Order.objects.filter(customer=customer, ordered=False, billing_address__isnull=True).exists():
					order = Order.objects.get(customer=customer, ordered=False)
					firstname = self.request.POST['firstname']
					lastname = self.request.POST['lastname']
					address = self.request.POST['address']
					email = self.request.POST['email']
					phone = self.request.POST['phone']
					country = self.request.POST['country']
					postalcode = self.request.POST['postalcode']
					city = self.request.POST['city']

					billing_address = BillingAddress(
						customer = customer,
						first_name = firstname,
						last_name = lastname,
						address = address,
						email = email,
						phone_number = phone,
						country = country,
						postal_code = postalcode,
						city = city
					)
					billing_address.save()
					order.billing_address = billing_address
					order.save()
					data = {
						'fullname': order.billing_address.fullname(),
						'fulladdress': order.billing_address.fulladdress()
					}
					return JsonResponse(data)

				elif Order.objects.filter(customer=customer, ordered=False, billing_address__isnull=False).exists():
					firstname = self.request.POST['firstname']
					lastname = self.request.POST['lastname']
					address = self.request.POST['address']
					email = self.request.POST['email']
					phone = self.request.POST['phone']
					country = self.request.POST['country']
					postalcode = self.request.POST['postalcode']
					city = self.request.POST['city']
					
					billing_address = BillingAddress.objects.get(customer=customer)

					billing_address.first_name = firstname
					billing_address.last_name = lastname
					billing_address.address = address
					billing_address.email = email
					billing_address.phone_number = phone
					billing_address.country = country
					billing_address.postal_code = postalcode
					billing_address.city = city
					
					billing_address.save()
					data = {
						'fullname': billing_address.fullname(),
						'fulladdress': billing_address.fulladdress()
					}
					return JsonResponse(data)

			except ObjectDoesNotExist:
				messages.info(self.request, 'Nie udało się przesłać adresu')
				return redirect('/')
		else:
			messages.info(self.request, 'Nie masz aktywnego zamówienia')
			return redirect('/')


class Shipping_Address(View):
	def get(self, *args, **kwargs):
		customer = self.request.session['customer']
		if Order.objects.filter(customer=customer, ordered=False, shipping_address__isnull=False).exists():
			data = {'shipping_address': True}
			return JsonResponse(data)
		data = {'shipping_address': False}
		return JsonResponse(data)

	def post(self,*args, **kwargs):
		if self.request.session.get('customer', None):
			try:
				customer = self.request.session['customer']
				if Order.objects.filter(customer=customer, ordered=False, shipping_address__isnull=True).exists():
					order = Order.objects.get(customer=customer, ordered=False)
					firstname = self.request.POST['firstname']
					lastname = self.request.POST['lastname']
					address = self.request.POST['address']
					email = self.request.POST['email']
					phone = self.request.POST['phone']
					country = self.request.POST['country']
					postalcode = self.request.POST['postalcode']
					city = self.request.POST['city']

					shipping_address = ShippingAddress(
						customer = customer,
						first_name = firstname,
						last_name = lastname,
						address = address,
						email = email,
						phone_number = phone,
						country = country,
						postal_code = postalcode,
						city = city
					)
					shipping_address.save()
					order.shipping_address = shipping_address
					order.save()
					data = {
						'fullname': order.shipping_address.fullname(),
						'fulladdress': order.shipping_address.fulladdress()
					}
					return JsonResponse(data)

				elif Order.objects.filter(customer=customer, ordered=False, shipping_address__isnull=False).exists():
					firstname = self.request.POST['firstname']
					lastname = self.request.POST['lastname']
					address = self.request.POST['address']
					email = self.request.POST['email']
					phone = self.request.POST['phone']
					country = self.request.POST['country']
					postalcode = self.request.POST['postalcode']
					city = self.request.POST['city']
					
					shipping_address = ShippingAddress.objects.get(customer=customer)

					shipping_address.first_name = firstname
					shipping_address.last_name = lastname
					shipping_address.address = address
					shipping_address.email = email
					shipping_address.phone_number = phone
					shipping_address.country = country
					shipping_address.postal_code = postalcode
					shipping_address.city = city
					
					shipping_address.save()
					data = {
						'fullname': shipping_address.fullname(),
						'fulladdress': shipping_address.fulladdress()
					}
					return JsonResponse(data)

			except ObjectDoesNotExist:
				messages.info(self.request, 'Nie udało się przesłać adresu')
				return redirect('/')
		else:
			messages.info(self.request, 'Nie masz aktywnego zamówienia')
			return redirect('/')



def finish(request):
	return render(request, 'shopping_cart/finish.html')

@csrf_exempt
def webhook_stripe(request):
  payload = request.body
  event = None

  try:
    event = stripe.Event.construct_from(
      json.loads(payload), stripe.api_key
    )
  except ValueError as e:
    # Invalid payload
    return HttpResponse(status=400)

  # Handle the event
  if event.type == 'payment_intent.succeeded':
    payment_intent = event.data.object # contains a stripe.PaymentIntent
    #handle_payment_intent_succeeded(payment_intent)
    #print(payment_intent.id)
    #print(payment_intent.amount)
    #print(payment_intent.currency)
    customer = payment_intent.metadata.customer
    order = Order.objects.get(customer=customer, ordered=False)
    #substracting stock of item
    for item in order.items.all():
    	color_item = Color.objects.get(id=item.item.id)
    	color_item.stock -= item.quantity
    	color_item.save()

    order.ordered = True
    order.ref_code = payment_intent.id
    order.save()

    #deleting the promo code
    coupon = Coupon.objects.filter(code=order.promotion.code)
    if coupon.exists():
    	coupon.delete()

    send_email({'order':order}, order.billing_address.fullname(), order.billing_address.email)
    return HttpResponse(status=200)

  elif event.type == 'payment_method.attached':
    payment_method = event.data.object # contains a stripe.PaymentMethod
    #handle_payment_method_attached(payment_method)
  # ... handle other event types
  else:
    # Unexpected event type
    return HttpResponse(status=400)

  


