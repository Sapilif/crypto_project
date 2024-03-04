from django import forms
from django.forms import ModelForm
from django.core.validators import MinValueValidator, MaxValueValidator
from .models import Transaction


class TransactionForm(ModelForm):

	class Meta:
		model = Transaction
		fields = ('to_user', 'amount')

		labels = {
			'to_user': '',
			'amount': '',
		}

		widgets = {
			'to_user': forms.TextInput(attrs={'class':'form-control', 'placeholder':'Beneficiar'}),
			'amount': forms.TextInput(attrs={'class':'form-control', 'placeholder':'Suma'}),
		}
