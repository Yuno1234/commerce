from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class User(AbstractUser):
    pass

class Category(models.Model):
    category = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.category}"

class Listing(models.Model):
    title = models.CharField(max_length=30)
    date = models.DateTimeField(default=timezone.now)
    image = models.URLField(max_length=2000)
    isActive = models.BooleanField(default=True)
    description = models.CharField(max_length=1000)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="similar_listings")
    startBid = models.FloatField()
    currentBid = models.FloatField(null=True, blank=True)
    seller = models.ForeignKey(User, on_delete=models.PROTECT, related_name="all_user_listings")
    buyer = models.ForeignKey(User, null=True, blank=True, on_delete=models.PROTECT)
    watchers = models.ManyToManyField(User, blank=True, related_name="watched_listings")

    def __str__(self):
        return f"{self.date}: {self.title} is {self.startBid}"

class Bid(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="listing_bids")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_bids")
    bid = models.FloatField(blank=True)
    date = models.DateTimeField(auto_now=True)

class Comment(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="get_comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now)
    text = models.CharField(blank=True, max_length=300)