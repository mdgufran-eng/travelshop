from django.urls import path
from . import views

urlpatterns = [
    path("", views.product_list, name="product_list"),
    path("p/<int:pk>/", views.product_detail, name="product_detail"),
    path("success/", views.booking_success, name="booking_success"),
]
