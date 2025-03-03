from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    pass

class Listing(models.Model):
    CATEGORY_CHOICES = [
        ('FASHION', 'Fashion'),
        ('TOYS', 'Toys'),
        ('ELECTRONICS', 'Electronics'),
        ('HOME', 'Home'),
        ('OTHER', 'Other'),
    ]
    
    title = models.CharField(max_length=64)
    description = models.TextField()
    starting_bid = models.DecimalField(max_digits=10, decimal_places=2)
    image_url = models.URLField(blank=True)  # Optional field
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, blank=True)  # Optional field
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
    
    def __str__(self):
        return f"{self.title} (${self.starting_bid})"

class Bid(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"${self.amount} bid by {self.bidder.username} on {self.listing.title}"

class Comment(models.Model):
    text = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Comment by {self.author.username} on {self.listing.title}"