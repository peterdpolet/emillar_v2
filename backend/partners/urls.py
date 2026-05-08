from django.urls import path
from . import views

urlpatterns = [
    path('suppliers/', views.BusinessPartnerListCreateAPIView.as_view()),
    path('customers/', views.CustomerListCreateAPIView.as_view()),
]
