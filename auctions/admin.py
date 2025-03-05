from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Category, Listing, Bid, Comment, Watchlist

class ListingAdmin(admin.ModelAdmin):
    list_display = ('title', 'creator', 'category', 'starting_bid', 'current_price', 'active', 'created_at')
    list_filter = ('active', 'category', 'created_at')
    search_fields = ('title', 'description', 'creator__username')
    readonly_fields = ('created_at', 'current_price')

class BidAdmin(admin.ModelAdmin):
    list_display = ('listing', 'bidder', 'amount', 'timestamp')
    list_filter = ('timestamp', 'listing', 'bidder')
    search_fields = ('listing__title', 'bidder__username')

class CommentAdmin(admin.ModelAdmin):
    list_display = ('listing', 'commenter', 'timestamp')
    list_filter = ('timestamp', 'listing', 'commenter')
    search_fields = ('text', 'listing__title', 'commenter__username')

class WatchlistAdmin(admin.ModelAdmin):
    list_display = ('user',)
    search_fields = ('user__username',)

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'listing_count')
    
    def listing_count(self, obj):
        return obj.listings.count()
    listing_count.short_description = 'Number of Listings'

# Extend the default UserAdmin to include more details
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'is_staff', 'listing_count', 'bid_count')
    
    def listing_count(self, obj):
        return obj.listings.count()
    listing_count.short_description = 'Listings Created'
    
    def bid_count(self, obj):
        return obj.bids.count()
    bid_count.short_description = 'Bids Placed'

# Re-register models with custom admin classes
admin.site.register(Listing, ListingAdmin)
admin.site.register(Bid, BidAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Watchlist, WatchlistAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(User, CustomUserAdmin)