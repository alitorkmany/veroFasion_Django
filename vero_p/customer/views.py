from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.mail import BadHeaderError, send_mail
from django.contrib import messages
from django.conf import settings

# Create your views here.
def login_view(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return redirect('/')
    else:
        messages.warning(request, 'Nazwa użytkownika lub hasło jest niepoprawne')
        return redirect('/')

def logout_view(request):
    logout(request)
    return render(request, 'customer/logout.html')

def send_email(request):
    subject = request.POST.get('subject', '')
    message = request.POST.get('message', '')
    from_email = request.POST.get('from_email', '')
    if subject and message and from_email:
        try:
            send_mail(subject, message, from_email, [settings.EMAIL_HOST_USER])
        except BadHeaderError:
            return HttpResponse('Invalid header found.')
        messages.info(request, 'Nie masz aktywnego zamówienia')
        return redirect('/')
    else:
    	return HttpResponse('Proszę wypełnić wszystkie pola')

def reset_password_view(request):
	username = request.POST.get('username', '')
	password = request.POST.get('old_password', '')
	new_password = request.POST.get('new_password', '')

	user = User.objects.filter(username=username).first()
	if user.check_password(password):
		user.set_password(new_password)
		user.save()
		messages.info(request, 'Twoje hasło zostało zresetowane')
		return redirect('/')
	else:
		messages.warning(request, 'Nazwa użytkownika lub hasło jest niepoprawne')
		return redirect('/')

