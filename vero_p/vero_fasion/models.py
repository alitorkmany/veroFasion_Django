from django.shortcuts import get_object_or_404
from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.core.files.uploadedfile import InMemoryUploadedFile
from rest_framework import serializers
from decimal import Decimal
from io import BytesIO
from PIL import Image
import PIL
import sys

CATAGORY_CHOICES = (
    ('KOBIETA', 'Women'),
    ('MĘŻCZYZNA', 'Men'),
    ('DZIECKO', 'Kids'),
)

VARIETY_CHOICES = (
    ('RAMIĘ', 'Shoulder Bag'),
    ('ZAKUPY', 'Tote Bag'),
    ('PAS', 'Belt Bag'),
    ('PORTMONETKA', 'Purse'),
    ('PLECAK', 'Backpack'),
    ('PORTFEL', 'Wallet'),
    ('DZIECI', 'Kids Product'),
)

LOCATION_CHOICES = (
    ('IT', 'Italy'),
    ('FR', 'France'),
    ('CH', 'China'),
)


class Color(models.Model):
	image = models.ImageField(default = 'default.jpg', upload_to = 'item_pics')
	produc_color = models.CharField(max_length=100)
	stock = models.PositiveIntegerField(default=0)

		#Resize image in models save method
	def save(self):

		#Opening the uploaded image
		im = Image.open(self.image)

		output = BytesIO()

		#Resize/modify the image
		im = im.resize((600,700), PIL.Image.ANTIALIAS)

		#after modifications, save it to the output
		im.save(output, format='JPEG', quality=75)
		output.seek(0)

		#change the imagefield value to be the newley modifed image value
		self.image = InMemoryUploadedFile(output,'ImageField', "%s.jpg" %self.image.name.split('.')[0], 'image/jpeg', sys.getsizeof(output), None)

		super(Color, self).save()

	def __str__(self):
		return self.produc_color


class Exchange(models.Model):
			euro = models.DecimalField(max_digits=10, decimal_places=2, default=0)
			def __str__(self):
				return str(self.euro)


class Item(models.Model):
	title = models.CharField(max_length=100)
	color = models.ManyToManyField(Color)
	catagory = models.CharField(max_length=20, choices=CATAGORY_CHOICES, default='KOBIETA')
	variety = models.CharField(max_length=20, choices=VARIETY_CHOICES)
	discription = models.TextField()
	price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
	sale_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(Decimal('0.01'))])
	whole_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
	location = models.CharField(max_length=2, choices=LOCATION_CHOICES, default='IT')

	def __str__(self):
		return self.title

	def get_euro_rate(self):
		return get_object_or_404(Exchange)

	def get_euro_price(self):
		return round(self.price / self.get_euro_rate().euro, 2)

	def get_euro_discount_price(self):
		return round(self.sale_price / self.get_euro_rate().euro, 2)

	def get_euro_whole_price(self):
		return round(self.whole_price / self.get_euro_rate().euro, 2)



############ serializer class ####################
class ImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField('get_image_url')

    class Meta:
        model = Color
        fields = ('id','produc_color', 'image_url') 

    def get_image_url(self, item):
       
        image_url = item.image.url
        return item.image.url


class Subscription(models.Model):
	email = models.EmailField(max_length=70, unique=True)
	def __str__(self):
		return self.email





														
