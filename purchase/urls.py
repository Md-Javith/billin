from django.contrib import admin
from django.urls import path, include
from purchase.Views.Purchase import CreatePurchaseOrderAPIView


urlpatterns = [
   
    path('purchase', CreatePurchaseOrderAPIView.as_view(), name='purchase')

]