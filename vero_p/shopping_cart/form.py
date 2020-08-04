from django import forms

class CouponForm(forms.Form):
	code = forms.CharField(widget=forms.TextInput(attrs={
		'class': 'form-control mb-2 mr-sm-2'
		}))