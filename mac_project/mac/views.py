from django.shortcuts import render, redirect
import calendar
from calendar import HTMLCalendar
from datetime import datetime
from twilio.rest import Client
from django.contrib.auth.models import User
from .models import Transaction, AppUser, TrustContact
from django.contrib import messages
from .forms import TransactionForm
from django.http import HttpResponseRedirect
from django.db.models import Q
import random
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from base64 import b64encode, b64decode


def home(request):
	appUser = initializare_user(request)
	now=datetime.now()
	current_year = now.year

	time = now.strftime('%I:%M %p')


	return render(request, 
		'mac/home.html', {
		'appUser':appUser,
		"current_year":current_year,
		"time":time,
		})


def initializare_user(request):

	appUser = None
	if request.user.is_authenticated:
		my_user = request.user
		appUser = AppUser.objects.get(user=my_user)
	return appUser


def all_transactions(request):
	appUser = initializare_user(request)

	if appUser is not None:
		transactions_list = Transaction.objects.filter(Q(from_user=appUser.user) & Q(is_validated=False))
		return render(request, 
			'mac/transactions_list.html', {
			'appUser':appUser,
			'transactions_list': transactions_list
		})
	else:
		return render(request, 
			'mac/transactions_list.html', {
			
			})

def all_transactions_validated(request):
	appUser = initializare_user(request)

	if appUser is not None:
		transactions_list = Transaction.objects.filter(Q(from_user=appUser.user) & Q(is_validated=True))
		transactions_list2 = Transaction.objects.filter(Q(to_user=appUser.user) & Q(is_validated=True))

		return render(request, 
			'mac/transactions_list_validated.html', {
			'appUser':appUser,
			'transactions_list_validated': transactions_list,
			'transactions_list_validated2': transactions_list2
		})
	else:
		return render(request, 
			'mac/transactions_list_validated.html', {
			
			})

def validate_transaction(request, transaction_id):
	appUser = initializare_user(request)

	if request.method=="POST":
		searched = request.POST['searched']
		transaction = Transaction.objects.get(pk=transaction_id)
		
		private_key = privateKeyTextToObject(appUser.rsa_private)
		ciphertext = transaction.pin
		decrypted_pin = str(decrypt(ciphertext, private_key))
		print(decrypted_pin)


		if searched==decrypted_pin:
			transaction.is_validated=True
			user_to_receive_money = User.objects.get(username=transaction.to_user)
			appUser_to_receive_money = AppUser.objects.get(user=user_to_receive_money)
			appUser_to_receive_money.funds = appUser_to_receive_money.funds + int(transaction.amount)
			appUser_to_receive_money.save()
			transaction.save()
			messages.success(request, 'Tranzactie realizata cu succes!')
			return redirect('list-transactions')
			return render(request, 
				'mac/transactions_list.html', {
				'appUser':appUser,
				'transactions_list': transactions_list
				})
		else:
			transaction.attemps=transaction.attemps-1
			transaction.save()
			if transaction.attemps==0:

				appUser.locked = True
				transaction.delete()
				appUser.funds = appUser.funds + int(transaction.amount)

				random_number = random.randint(100000, 999999)

				#public_key = publicKeyTextToObject(appUser.rsa_public)
				#encrypt_pin = encrypt(random_number, public_key)
				#appUser.unlock_pin = encrypt_pin

				appUser.unlock_pin = str(random_number)

				appUser.save()
				messages.error(request, 'Ai introdus PIN-ul gresit de 3 ori. Contul tau a fost blocat!')
				return redirect('list-transactions')
			else:

				messages.error(request, 'PIN invalid!')
				return redirect('list-transactions')

	else:
		return render(request, 
			'mac/transactions_list.html', {
			'appUser':appUser,
			})


def add_transaction(request):

	appUser = initializare_user(request)

	submitted = False
	if request.method == "POST":
		form = TransactionForm(request.POST, request.FILES)
		if form.is_valid():

			my_user = request.user
			transaction = form.save(commit=False)
			transaction.from_user = my_user
			if any(not char.isdigit() for char in transaction.amount):
				messages.error(request, 'Valoarea trebuie sa fie un numar!')
				return redirect('add-transaction')

			if int(transaction.amount) > appUser.funds:
				messages.error(request, 'Fonduri insuficiente!')
				return redirect('add-transaction')

			try:
				to_user=User.objects.get(username=transaction.to_user)
			except User.DoesNotExist:
				to_user=None

			if to_user is None:
				messages.info(request, 'Utilizator inexistent!')
				return redirect('add-transaction')

			appUser.funds = appUser.funds - int(transaction.amount)
			appUser.save()

			random_number = random.randint(100000, 999999)
			#transaction.pin = str(random_number)

			public_key = publicKeyTextToObject(appUser.rsa_public)
			encrypt_pin = encrypt(random_number, public_key)
			transaction.pin = encrypt_pin

			transaction.save()


			account_sid = 'AC56bfa417b453614f33b7910490f47951'
			auth_token = 'c9a31e6620949109e054adb184aa3d58'

			# setează numărul de la Twilio și numărul destinatarului
			twilio_number = '+16592214646'
			to_number = '+4'+appUser.phone

			# inițializează clientul Twilio
			client = Client(account_sid, auth_token)

			# trimite mesajul SMS
			message = client.messages.create(
	    		body='Pentru a valida tranzactia catre '+ transaction.to_user + ' introdu PIN-ul: ' + str(random_number) + '.',
	    		from_=twilio_number,
	    		to=to_number
			)
			

			return HttpResponseRedirect('/add_transaction?submitted=True')
	else:
		form = TransactionForm
		if 'submitted' in request.GET:
			submitted = True
	return render(request, 
		'mac/add_transaction.html', {
		'appUser':appUser,
		'form':form,
		'submitted':submitted
		})



def delete_transaction(request, transaction_id):
	appUser = initializare_user(request)
	transaction = Transaction.objects.get(pk=transaction_id)
	appUser.funds = appUser.funds + int(transaction.amount)
	appUser.save()
	transaction.delete()
	messages.success(request, "Ai sters cu succes tranzactia catre " + transaction.to_user + " in valoare de " + str(transaction.amount) + '.' )

	return redirect('list-transactions')

def all_trustcontacts(request):
	appUser = initializare_user(request)

	if appUser is not None:
		trustcontacts_list = TrustContact.objects.filter(user=appUser)
		trustcontacts_list2 = TrustContact.objects.filter(trust_user=appUser)
		return render(request, 
				'mac/trustcontacts_list.html', {
				'appUser':appUser,
				'trustcontacts_list': trustcontacts_list,
				'trustcontacts_list2': trustcontacts_list2
		})
	else:
		return render(request, 
			'mac/trustcontacts_list.html', {
			
			})



def unlock_account(request):
	appUser = initializare_user(request)

	if request.method=="POST":
		pin = request.POST['searched']
		pin = str(pin)


		#private_key = privateKeyTextToObject(appUser.rsa_private)
		#ciphertext = appUser.unlock_pin
		#decrypted_pin = str(decrypt(ciphertext, private_key))
		#print(decrypted_pin)


		if appUser.unlock_pin == pin:
			appUser.locked = False
			appUser.unlock_pin=""
			appUser.save()
			messages.success(request, 'Contul tau a fost deblocat cu succes!')
			return redirect('list-trustcontacts')
		else:
			messages.error(request, 'PIN incorect!')
			return redirect('list-trustcontacts')



def search_transactions(request):
	appUser = initializare_user(request)

	if request.method=="POST":
		searched = request.POST['searched']


	if appUser is not None:
		transactions_list = Transaction.objects.filter(Q(to_user__contains=searched) & Q(is_validated=True))
		transactions_list = transactions_list.filter(from_user=appUser.user)
		transactions_list2 = Transaction.objects.filter(Q(from_user__contains=searched) & Q(is_validated=True))
		transactions_list2 = transactions_list2.filter(to_user=appUser.user)
		return render(request, 
			'mac/transactions_list_validated.html', {
			'appUser':appUser,
			'transactions_list_validated': transactions_list,
			'transactions_list_validated2': transactions_list2
		})
	else:
		return render(request, 
			'mac/transactions_list_validated.html', {
			
			})



def privateKeyTextToObject(private_key_string):
    private_key_bytes = private_key_string.encode('utf-8')

    # Load private key back into an RSAPrivateKey object
    loaded_private_key = serialization.load_pem_private_key(
        private_key_bytes,
        password=None,  # Put the password here if the key is encrypted
        backend=default_backend()
    )
    return loaded_private_key

def publicKeyTextToObject(public_key_string):
    # Converteste string-ul in bytes
    public_key_bytes = public_key_string.encode('utf-8')

    # Transforma bytes-ul intr-un obiect de cheie publica
    public_key = serialization.load_pem_public_key(
        public_key_bytes,
        backend=default_backend()
    )

    return public_key

def encrypt(number, public_key):
    number_bytes = str(number).encode('utf-8')
    ciphertext = public_key.encrypt(
        number_bytes,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return b64encode(ciphertext).decode('utf-8')

def decrypt(ciphertext, private_key):
    ciphertext_bytes = b64decode(ciphertext.encode('utf-8'))
    plaintext = private_key.decrypt(
        ciphertext_bytes,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return int(plaintext.decode('utf-8'))