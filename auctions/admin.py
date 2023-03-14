from django.contrib import admin

from.models import *

class BidAdmin(admin.ModelAdmin):
    list_display = ("id", "listing", "user", "bid", "date")

# Register your models here.
admin.site.register(User)
admin.site.register(Category)
admin.site.register(Listing)
admin.site.register(Bid, BidAdmin)
admin.site.register(Comment)
