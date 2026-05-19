from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import timedelta
# Create your models here.

class EventAdd(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    type = models.CharField(max_length=100)
    date = models.DateField()
    date_end = models.DateField()
    location = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    capacity = models.IntegerField(default=0)
    image = models.ImageField(upload_to='events/')

    def __str__(self):
        return self.title
    
    def get_date(self, obj):
        return obj.date.strftime("%d-%m-%Y") if obj.date else None
    
    
    
class User(AbstractUser):
    ph_number = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return self.username
    
    

class FavouriteEvent(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey("EventAdd", on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'event')  # ensures a user can't favorite the same event twice

    def __str__(self):
        return f"{self.user.username} → {self.event.title}"



class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(EventAdd, on_delete=models.CASCADE)
    quantity = models.PositiveBigIntegerField(default=1)

    @property
    def total_price(self):
        return self.quantity * self.event.price

    def save(self, *args, **kwargs):
        # Check available capacity before saving
        if self.pk is None:  # only for new bookings
            if self.event.capacity < self.quantity:
                raise ValueError("Not enough tickets available")

            # Reduce capacity
            self.event.capacity -= self.quantity
            self.event.save()

        super().save(*args, **kwargs)

    def get_available_tickets(self, obj):
        total_booked = Booking.objects.filter(event=obj.event).aggregate(
            total=models.Sum('quantity')
        )['total'] or 0

        return obj.event.capacity - total_booked
    

    def delete(self, *args, **kwargs):
        self.event.capacity += self.quantity
        self.event.save()

        super().delete(*args, **kwargs)



class Payment(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'pending'),
        ('SUCCESS', 'success'),
        ('FAILED', 'failed')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.amount = self.booking.total_price
        super().save(*args, **kwargs)



class OTP(models.Model):
    email = models.EmailField()
    otp = models.CharField(max_length=6)
    otp_type = models.CharField(max_length=20,)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=5)
    
    def __str__(self):
        return f"{self.email} - {self.otp_type}"


