from django.db import models
from django.contrib.auth.models import User

class Transaction(models.Model):

	from_user = models.CharField('From', max_length=120)
	to_user = models.CharField('To', max_length=120)
	amount = models.CharField('Amount', max_length=120)
	is_validated = models.BooleanField('Tranzactie validata', default = False)
	attemps = models.IntegerField(blank=True, null=True, default=3)
	#pin = models.CharField('PIN', max_length=120, blank=True)
	pin = models.TextField('PIN', blank=True)

	def __str__(self):
		return self.to_user


class AppUser(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	funds = models.IntegerField(blank=True, null=True, default=5000)
	phone = models.CharField('Phone', max_length=120, default='0752019203')
	locked = models.BooleanField('Cont blocat', default = False)
	#unlock_pin = models.CharField('PIN', max_length=120, blank=True)
	unlock_pin = models.TextField('PIN', blank=True)
	rsa_public = models.TextField('RSA Public', blank=True)
	rsa_private = models.TextField('RSA Private', blank=True)

	def __str__(self):
		return self.user.username

class TrustContact(models.Model):
	user = models.ForeignKey(AppUser, blank=True, null=True, on_delete=models.CASCADE, related_name='trust_contact_user')
	trust_user = models.ForeignKey(AppUser, blank=True, null=True, on_delete=models.CASCADE, related_name='trust_contact_trust_user')

	def __str__(self):
		return self.user.user.username