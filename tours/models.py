from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import Sum
from django.utils import timezone

class Product(models.Model):
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    price_per_person = models.DecimalField(max_digits=10, decimal_places=2)
    capacity_per_day = models.PositiveIntegerField(default=20)

    class Meta:
        indexes = [
            models.Index(fields=["is_active", "name"]),
        ]

    def __str__(self):
        return self.name

    def available_capacity_on(self, date):
        """Return remaining seats for a specific date considering confirmed bookings."""
        booked = self.bookings.filter(
            date=date, status=Booking.Status.CONFIRMED
        ).aggregate(total=Sum("num_pax"))["total"] or 0
        return max(0, self.capacity_per_day - booked)

class Booking(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        CONFIRMED = "CONFIRMED", "Confirmed"
        CANCELLED = "CANCELLED", "Cancelled"

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="bookings")
    customer_name = models.CharField(max_length=120)
    customer_email = models.EmailField()
    date = models.DateField(default=timezone.now)
    num_pax = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.CONFIRMED)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["product", "date"]),
            models.Index(fields=["status"]),
        ]
        # Example constraint: at least 1 pax
        constraints = [
            models.CheckConstraint(check=models.Q(num_pax__gte=1), name="num_pax_at_least_1")
        ]

    def clean(self):
        """Business rule validation called by forms/admin before saving."""
        # This runs even before DB save — good for business rules.
        if self.status == Booking.Status.CONFIRMED and self.product_id and self.date:
            # compute remaining capacity excluding "self" on updates
            qs = self.product.bookings.filter(date=self.date, status=Booking.Status.CONFIRMED)
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            already = qs.aggregate(total=Sum("num_pax"))["total"] or 0
            remaining = max(0, self.product.capacity_per_day - already)
            if self.num_pax > remaining:
                raise ValidationError(f"Only {remaining} pax left for {self.product.name} on {self.date}.")

    def __str__(self):
        return f"{self.customer_name} · {self.product.name} · {self.date} ({self.num_pax} pax)"
