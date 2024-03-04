from django.contrib import admin

from .models import Transaction, AppUser, TrustContact

admin.site.register(Transaction)
admin.site.register(AppUser)
admin.site.register(TrustContact)
