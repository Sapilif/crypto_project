from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    #path('<int:year>/<str:month>/', views.home, name="home"),
    path('transactions', views.all_transactions, name="list-transactions"),
    path('transactions_validated', views.all_transactions_validated, name="list-transactions-validated"),
    path('validate_transaction/<transaction_id>', views.validate_transaction, name="validate-transaction"),
    path('add_transaction', views.add_transaction, name="add-transaction"),
    path('delete_transaction/<transaction_id>', views.delete_transaction, name="delete-transaction"),
    path('trustcontacts', views.all_trustcontacts, name="list-trustcontacts"),
    path('unlock_account', views.unlock_account, name="unlock-account"),
    path('search_transactions', views.search_transactions, name="search-transactions"),

]