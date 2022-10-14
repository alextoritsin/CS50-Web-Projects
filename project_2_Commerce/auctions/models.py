from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.deletion import CASCADE
from django.utils import timezone


class User(AbstractUser):
    pass


class Listing(models.Model):
    owner = models.ForeignKey(User, on_delete=CASCADE, related_name="listings")
    title = models.CharField(max_length=30)
    category = models.CharField(max_length=30)
    starting_bid = models.DecimalField(max_digits=8, decimal_places=2)
    url = models.URLField(default="https://live.staticflickr.com/5166/5281085826_aa97209986_z.jpg")
    description = models.TextField()
    pub_time = models.DateTimeField(default=timezone.now)
    active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return f'Title: {self.title}, categoty: {self.category}'


class Bid(models.Model):
    bidder = models.ForeignKey(User, on_delete=CASCADE, blank=True)
    listing = models.ForeignKey(Listing, on_delete=CASCADE)
    amount = models.DecimalField(max_digits=8, decimal_places=2, blank=True)

    def __str__(self) -> str:
        return f"by {self.bidder} of {self.amount} on {self.listing.title}"


class Watchlist(models.Model):
    person = models.ForeignKey(User, on_delete=CASCADE, related_name="watchlist")
    items = models.ManyToManyField(Listing, blank=True)  

    def __str__(self) -> str:
        return f"User: {self.person.username}"


class Comment(models.Model):
    listing = models.ForeignKey(Listing, on_delete=CASCADE, related_name="comments")
    author = models.ForeignKey(User, on_delete=CASCADE, related_name="comments")
    text = models.TextField()
    pub_time = models.DateTimeField(default=timezone.now)

    def __str__(self) -> str:
        return f"by {self.author} at {self.pub_time}"