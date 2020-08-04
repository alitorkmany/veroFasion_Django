from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from .models import Item, ImageSerializer, Exchange, Subscription, Color
from django.contrib.postgres.search import SearchVector
from django.db.models import Case, When
from shopping_cart.models import Coupon
from django.core.paginator import Paginator
from django.views.generic import View
from django.core import serializers
from django.contrib import messages
from django.conf import settings
import random
from .utils import send_email


# Create your views here.
#def home(request):
	#items = Item.objects.all()
	#return render(request, 'vero_fasion/home.html', {'items': items})

def home(request):
	if request.GET.get('order'):
		items = Item.objects.filter(sale_price__isnull=False)
	else:
		items = Item.objects.all()

	paginator = Paginator(items, 12)
	page = request.GET.get('page')
	items = paginator.get_page(page)

	return render(request, 'vero_fasion/home.html', {'items': items})

def get_items_queryset(request):
	queryset = None
	context = {}

	#if color was passed
	if request.GET.get('query') and request.GET.get('color') and request.GET.get('sort'):
		color = request.GET.get('color')
		sort = request.GET.get('sort')
		q = request.GET.get('query')
		queryset = Color.objects.filter(
			Q(item__title__icontains=q, produc_color=color) |
			Q(item__catagory__icontains=q, produc_color=color) |
			Q(item__variety__icontains=q, produc_color=color)
			).distinct().order_by(sort)
		context = {'color': color}
		#if order by price was passed
	elif request.GET.get('query') and request.GET.get('color'):
		q = request.GET.get('query')
		color = request.GET.get('color')
		queryset = Color.objects.filter(
			Q(item__title__icontains=q, produc_color=color) |
			Q(item__catagory__icontains=q, produc_color=color) |
			Q(item__variety__icontains=q, produc_color=color)
			).distinct()	
		context = {'color': color}

	elif request.GET.get('query') and request.GET.get('sort'): 
		q = request.GET.get('query') #splitting query by space
		sort = request.GET.get('sort')
		queryset = Color.objects.filter(
			Q(item__title__icontains=q) |
			Q(item__catagory__icontains=q) |
			Q(item__variety__icontains=q)
			).distinct().order_by(sort)

	elif request.GET.get('query'): 
		q = request.GET.get('query')
		queryset = Color.objects.filter(
			Q(item__title__icontains=q) |
			Q(item__catagory__icontains=q) |
			Q(item__variety__icontains=q)
			).distinct()
		
	context['items'] = queryset
	context['query'] = request.GET.get('query')
	context['count'] = len(queryset)
	context['title'] = 'Search'
	return render(request, 'vero_fasion/search.html', context)

#---------------------------Women-----------------------------------
def women_page(request):
	items = None
	context = {}
	if request.GET.get('order') and request.GET.get('color'):
		order = request.GET.get('order')
		color = request.GET.get('color')
		items = Color.objects.filter(produc_color=color, item__catagory='KOBIETA').order_by(order)
		context = {'color': color}

	elif request.GET.get('color'):
		color = request.GET.get('color')
		items = Color.objects.filter(produc_color=color, item__catagory='KOBIETA')
		context = {'color': color}

	elif request.GET.get('order'):
		order = request.GET.get('order')
		items = Color.objects.filter(item__catagory='KOBIETA').order_by(order)
	else:
		items = Color.objects.filter(item__catagory='KOBIETA')

	paginator = Paginator(items, 16)
	page = request.GET.get('page')
	items = paginator.get_page(page)
	context['items'] = items
	context['title'] = 'Women'
	return render(request, 'vero_fasion/product_w.html', context)


def women_catagory(request, variety):
	items = None
	context = {}
	if request.GET.get('order') and request.GET.get('color'):
		order = request.GET.get('order')
		color = request.GET.get('color')
		items = Color.objects.filter(produc_color=color, item__catagory='KOBIETA', item__variety=variety).order_by(order)
		context = {'color': color}

	elif request.GET.get('color'):
		color = request.GET.get('color')
		items = Color.objects.filter(produc_color=color, item__catagory='KOBIETA', item__variety=variety)
		context = {'color': color}

	elif request.GET.get('order'):
		order = request.GET.get('order')
		items = Color.objects.filter(item__catagory='KOBIETA', item__variety=variety).order_by(order)
	else:
		items = Color.objects.filter(item__catagory='KOBIETA', item__variety=variety)

	paginator = Paginator(items, 16)
	page = request.GET.get('page')
	items = paginator.get_page(page)
	context['items'] = items
	context['variety'] = variety
	context['title'] = 'Women'
	return render(request, 'vero_fasion/product_w.html', context)

#-----------------------------Men------------------------------------
def men_page(request):
	items = None
	context = {}
	if request.GET.get('order') and request.GET.get('color'):
		order = request.GET.get('order')
		color = request.GET.get('color')
		items = Color.objects.filter(produc_color=color, item__catagory='MĘŻCZYZNA').order_by(order)
		context = {'color': color}

	elif request.GET.get('color'):
		color = request.GET.get('color')
		items = Color.objects.filter(produc_color=color, item__catagory='MĘŻCZYZNA')
		context = {'color': color}

	elif request.GET.get('order'):
		order = request.GET.get('order')
		items = Color.objects.filter(item__catagory='MĘŻCZYZNA').order_by(order)
	else:
		items = Color.objects.filter(item__catagory='MĘŻCZYZNA')

	paginator = Paginator(items, 16)
	page = request.GET.get('page')
	items = paginator.get_page(page)
	context['items'] = items
	context['title'] = 'Men'
	return render(request, 'vero_fasion/product_m.html', context)


def men_catagory(request, variety):
	items = None
	context = {}
	if request.GET.get('order') and request.GET.get('color'):
		order = request.GET.get('order')
		color = request.GET.get('color')
		items = Color.objects.filter(produc_color=color, item__catagory='MĘŻCZYZNA', item__variety=variety).order_by(order)
		context = {'color': color}

	elif request.GET.get('color'):
		color = request.GET.get('color')
		items = Color.objects.filter(produc_color=color, item__catagory='MĘŻCZYZNA', item__variety=variety)
		context = {'color': color}

	elif request.GET.get('order'):
		order = request.GET.get('order')
		items = Color.objects.filter(item__catagory='MĘŻCZYZNA', item__variety=variety).order_by(order)
	else:
		items = Color.objects.filter(item__catagory='MĘŻCZYZNA', item__variety=variety)

	paginator = Paginator(items, 16)
	page = request.GET.get('page')
	items = paginator.get_page(page)
	context['items'] = items
	context['variety'] = variety
	context['title'] = 'Men'
	return render(request, 'vero_fasion/product_m.html', context)

#-----------------------------Kid------------------------------------
def kid_page(request):
	items = None
	context = {}
	if request.GET.get('order') and request.GET.get('color'):
		order = request.GET.get('order')
		color = request.GET.get('color')
		items = Color.objects.filter(produc_color=color, item__catagory='DZIECKO').order_by(order)
		context = {'color': color}

	elif request.GET.get('color'):
		color = request.GET.get('color')
		items = Color.objects.filter(produc_color=color, item__catagory='DZIECKO')
		context = {'color': color}

	elif request.GET.get('order'):
		order = request.GET.get('order')
		items = Color.objects.filter(item__catagory='DZIECKO').order_by(order)
	else:
		items = Color.objects.filter(item__catagory='DZIECKO')

	paginator = Paginator(items, 16)
	page = request.GET.get('page')
	items = paginator.get_page(page)
	context['items'] = items
	context['title'] = 'Kids'
	return render(request, 'vero_fasion/product_kid.html', context)

#-----------------------------Sale------------------------------------	
def sale_page(request):
	items = None
	context = {}
	if request.GET.get('order') and request.GET.get('color'):
		order = request.GET.get('order')
		color = request.GET.get('color')
		items = Color.objects.filter(produc_color=color, item__sale_price__isnull=False).order_by(order)
		context = {'color': color}

	elif request.GET.get('color'):
		color = request.GET.get('color')
		items = Color.objects.filter(produc_color=color, item__sale_price__isnull=False)
		context = {'color': color}

	elif request.GET.get('order'):
		order = request.GET.get('order')
		items = Color.objects.filter(item__sale_price__isnull=False).order_by(order)
	else:
		items = Color.objects.filter(item__sale_price__isnull=False)

	paginator = Paginator(items, 16)
	page = request.GET.get('page')
	items = paginator.get_page(page)
	context['items'] = items
	context['title'] = 'Sale'
	return render(request, 'vero_fasion/sale.html', context)

def sale_catagory(request, variety):
	items = None
	context = {}
	if request.GET.get('order') and request.GET.get('color'):
		order = request.GET.get('order')
		color = request.GET.get('color')
		items = Color.objects.filter(produc_color=color, item__sale_price__isnull=False, item__catagory=variety).order_by(order)
		context = {'color': color}

	elif request.GET.get('color'):
		color = request.GET.get('color')
		items = Color.objects.filter(produc_color=color, item__sale_price__isnull=False, item__catagory=variety)
		context = {'color': color}

	elif request.GET.get('order'):
		order = request.GET.get('order')
		items = Color.objects.filter(item__sale_price__isnull=False, item__catagory=variety).order_by(order)
	else:
		items = Color.objects.filter(item__sale_price__isnull=False, item__catagory=variety)

	paginator = Paginator(items, 16)
	page = request.GET.get('page')
	items = paginator.get_page(page)
	context['items'] = items
	context['variety'] = variety
	context['title'] = 'Sale'
	return render(request, 'vero_fasion/sale.html', context)


def privacy(request):
	return render(request, 'vero_fasion/privacy.html', {'title': 'privacy'})

def regulation(request):
	return render(request, 'vero_fasion/regulation.html', {'title': 'Terms & Condition'})


#-----------------------------Whole Sale------------------------------------
@login_required
def whole_sale_page(request, location):
	items = None
	context = {}
	if request.GET.get('order') and request.GET.get('color'):
		order = request.GET.get('order')
		color = request.GET.get('color')
		items = Color.objects.filter(produc_color=color, item__location=location).order_by(order)
		context = {'color': color}

	elif request.GET.get('color'):
		color = request.GET.get('color')
		items = Color.objects.filter(produc_color=color, item__location=location)
		context = {'color': color}

	elif request.GET.get('order'):
		order = request.GET.get('order')
		items = Color.objects.filter(item__location=location).order_by(order)
	else:
		items = Color.objects.filter(item__location=location)

	paginator = Paginator(items, 16)
	page = request.GET.get('page')
	items = paginator.get_page(page)
	context['items'] = items
	context['location'] = location
	context['title'] = 'Whole Sale'
	return render(request, 'vero_fasion/whole_sale.html', context)

######################### Sub Views #######################################
def getDetail(request):
	rate = get_object_or_404(Exchange)
	id = request.GET.get('id', None)
	item = Item.objects.get(color__id = id)
	product_color = item.color.get(id=id)
	price_euro = None
	sale_euro = None
	if rate and item.sale_price:
		sale_euro = round(item.sale_price / rate.euro, 2)
	if rate and item.price:
		price_euro = round(item.price / rate.euro, 2)

	serializer = ImageSerializer(product_color)

	data = {
		'id': serializer.data['id'],
		'color': serializer.data['produc_color'],
		'title': item.title,
		'price': item.price,
		'sale_price': item.sale_price,
		'price_euro': price_euro,
		'sale_euro': sale_euro,
		'image_url': serializer.data['image_url']
	}
	return JsonResponse(data)

		
def detail(request, id):
	product = Item.objects.get(color__id=id)
	product_color = product.color.all().order_by(Case(When(id=id, then=0), default=1))
	return render(request, 'vero_fasion/detail.html', {'item': product, 'products': product_color})

@login_required
def whole_detail(request, id):
	product = Item.objects.get(color__id=id)
	product_color = product.color.all().order_by(Case(When(id=id, then=0), default=1))
	return render(request, 'vero_fasion/whole_detail.html', {'item': product, 'products': product_color})


def required_login(request):
	return render(request, 'vero_fasion/login_required.html')


def subscription(request):
	if request.method == 'POST':
		email = request.POST['email']
		qs = Subscription.objects.filter(email=email)
		if qs.exists():
			data = {'message': 'Ten email jest już w użyciu.'}
			return JsonResponse(data)
		else:
			reg = Subscription(email=email)
			reg.save()
			#generating promo code
			promo = 'WELCOME' + str(random.randint(10, 10000))
			#saving promo to db
			coupon = Coupon(code=promo, amount=10.00)
			coupon.save()
			ctx = {'side': settings.SITE_URL, 'promo': promo}
			send_email(email, 'vero_fasion/mail.html', ctx)
			data = {'message': 'Dziękujemy, subskrypcja zakończyła się powodzeniem.'}
			return JsonResponse(data)





