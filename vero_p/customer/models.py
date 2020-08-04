from django.db import models

class Customer(models.Model):
	"""docstring for Customer"""
	name = models.CharField(max_length=100, blank=False)
	tax_number = models.IntegerField()
	phone = models.IntegerField(blank=False)
	email = models.EmailField(blank=False)
	street = models.CharField(max_length=256)
	zipcode = models.IntegerField()
	city = models.CharField(max_length=100)
	country = models.CharField(max_length=100)
