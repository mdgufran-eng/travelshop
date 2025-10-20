from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib import messages
from .models import Product, Booking
from .forms import BookingForm

def product_list(request):
    products = Product.objects.filter(is_active=True).order_by("name")
    return render(request, "tours/product_list.html", {"products": products})

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk, is_active=True)
    form = BookingForm(product=product)
    if request.method == "POST":
        form = BookingForm(request.POST, product=product)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.product = product
            booking.status = Booking.Status.CONFIRMED
            booking.save()
            messages.success(request, "Booking confirmed!")
            return redirect(reverse("tours:booking_success") + f"?id={booking.id}")
    return render(request, "tours/product_detail.html", {"product": product, "form": form})

def booking_success(request):
    bid = request.GET.get("id")
    booking = Booking.objects.select_related("product").filter(pk=bid).first() if bid else None
    return render(request, "tours/booking_success.html", {"booking": booking})
