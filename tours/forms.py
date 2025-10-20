from django import forms
from .models import Booking

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ["customer_name", "customer_email", "date", "num_pax"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        self.product = kwargs.pop("product", None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned = super().clean()
        if self.product and cleaned.get("date") and cleaned.get("num_pax") is not None:
            # build a temporary instance and reuse Booking.clean() validation
            tmp = Booking(
                product=self.product,
                customer_name=cleaned.get("customer_name") or "",
                customer_email=cleaned.get("customer_email") or "",
                date=cleaned["date"],
                num_pax=cleaned["num_pax"],
                status="CONFIRMED",
            )
            tmp.clean()  # raise ValidationError on overbook
        return cleaned
