from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from .forms import RegisterUserForm
from mac.models import AppUser
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from base64 import b64encode, b64decode


def login_user(request):
	if request.method == "POST":
		username = request.POST["username"]
		password = request.POST["password"]
		user = authenticate(request, username=username, password=password)
		if user is not None:
			login(request, user)
			return redirect('home')
		else:
			messages.error(request, ("A intervenit o problema, incearca din nou..."))
			return redirect('login')
	else:
		return render(request, 'authenticate/login.html', {})


def logout_user(request):
	logout(request)
	messages.success(request, ("Te-ai deconectat cu success!"))
	return redirect('home')


def register_user(request):
	if request.method == "POST":
		form = RegisterUserForm(request.POST)
		if form.is_valid():
			form.save()
			username = form.cleaned_data['username']
			password = form.cleaned_data['password1']
			user = authenticate(username = username, password = password)
			login(request, user)
			messages.success(request, ("Cont inregistrat cu succes!"))
			
			private_key, public_key = generate_key_pair()
			publicKey = publicKeyObjectToText(public_key)
			privateKey = privateKeyObjectToText(private_key)

			new_Appuser = AppUser.objects.create(user=user)

			new_Appuser.rsa_public=publicKey
			new_Appuser.rsa_private=privateKey
			new_Appuser.save()
			
			return redirect('home')

	else:
		form = RegisterUserForm()

	return render(request, 'authenticate/register_user.html', {
		'form':form,
		})




def generate_key_pair():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    public_key = private_key.public_key()

    return private_key, public_key




def privateKeyObjectToText(private_key):
    private_key_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    )

    # Transform private_key_bytes in a string
    private_key_string = private_key_bytes.decode('utf-8')
    return private_key_string



def publicKeyObjectToText(public_key):
    public_key_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    # Transform private_key_bytes in a string
    public_key_string = public_key_bytes.decode('utf-8')
    return public_key_string




