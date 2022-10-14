from django.contrib import admin
from .models import Listing, User, Bid, Comment

# Register your models here.

class ListingAdmin(admin.ModelAdmin):
    list_display = ("owner", "title", "category", 
                    "description", "pub_time", "active")


class BidAdmin(admin.ModelAdmin):
    list_display = ("listing", "bidder", "amount")


admin.site.register(Listing, ListingAdmin)
admin.site.register(Bid, BidAdmin)
admin.site.register(User)
admin.site.register(Comment)