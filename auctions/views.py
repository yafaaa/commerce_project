from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.contrib import messages

from .models import User, Listing, Category, Bid, Comment, Watchlist


def index(request):
    active_listings = Listing.objects.filter(active=True)
    return render(request, "auctions/index.html", {
        "listings": active_listings
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


def listing_detail(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    comments = listing.comments.all().order_by('-timestamp')
    
    in_watchlist = False
    if request.user.is_authenticated:
        watchlist, created = Watchlist.objects.get_or_create(user=request.user)
        in_watchlist = listing in watchlist.listings.all()
    
    return render(request, "auctions/listing_detail.html", {
        "listing": listing,
        "in_watchlist": in_watchlist,
        "comments": comments,
        "is_owner": request.user == listing.creator if request.user.is_authenticated else False,
        "is_winner": request.user == listing.winner if request.user.is_authenticated and listing.winner else False
    })


@login_required
def create_listing(request):
    if request.method == "POST":
        title = request.POST["title"]
        description = request.POST["description"]
        starting_bid = request.POST["starting_bid"]
        image_url = request.POST.get("image_url", "")
        
        category_name = request.POST.get("category", "")
        category = None
        if category_name:
            category, _ = Category.objects.get_or_create(name=category_name)
        
        listing = Listing(
            title=title,
            description=description,
            starting_bid=starting_bid,
            image_url=image_url,
            category=category,
            creator=request.user
        )
        listing.save()
        
        return HttpResponseRedirect(reverse("index"))
    else:
        categories = [
            {"id": "FASHION", "name": "Fashion"},
            {"id": "TOYS", "name": "Toys"},
            {"id": "ELECTRONICS", "name": "Electronics"},
            {"id": "HOME", "name": "Home"},
            {"id": "OTHER", "name": "Other"}
        ]
        return render(request, "auctions/create_listing.html", {
            "categories": categories
        })
    
@login_required
def watchlist(request):
    watchlist, created = Watchlist.objects.get_or_create(user=request.user)
    return render(request, "auctions/watchlist.html", {
        "listings": watchlist.listings.all()
    })


@login_required
def toggle_watchlist(request, listing_id):
    if request.method == "POST":
        listing = get_object_or_404(Listing, pk=listing_id)
        watchlist, created = Watchlist.objects.get_or_create(user=request.user)
        
        if listing in watchlist.listings.all():
            watchlist.listings.remove(listing)
            messages.success(request, "Removed from watchlist")
        else:
            watchlist.listings.add(listing)
            messages.success(request, "Added to watchlist")
        
        return HttpResponseRedirect(reverse("listing", args=[listing_id]))


@login_required
def place_bid(request, listing_id):
    if request.method == "POST":
        listing = get_object_or_404(Listing, pk=listing_id)
        
        try:
            amount = float(request.POST["amount"])
        except ValueError:
            messages.error(request, "Invalid bid amount")
            return HttpResponseRedirect(reverse("listing", args=[listing_id]))
        
        current_price = listing.current_price()
        
        if amount < float(current_price):
            messages.error(request, "Bid must be greater than the current price")
        else:
            bid = Bid(listing=listing, bidder=request.user, amount=amount)
            bid.save()
            messages.success(request, "Bid placed successfully")
        
        return HttpResponseRedirect(reverse("listing", args=[listing_id]))


@login_required
def close_auction(request, listing_id):
    if request.method == "POST":
        listing = get_object_or_404(Listing, pk=listing_id)
        
        if request.user != listing.creator:
            messages.error(request, "Only the creator can close the auction")
            return HttpResponseRedirect(reverse("listing", args=[listing_id]))
        
        bids = listing.bids.all()
        if bids:
            highest_bid = max(bids, key=lambda x: x.amount)
            listing.winner = highest_bid.bidder
        
        listing.active = False
        listing.save()
        
        messages.success(request, "Auction closed successfully")
        return HttpResponseRedirect(reverse("listing", args=[listing_id]))


@login_required
def add_comment(request, listing_id):
    if request.method == "POST":
        listing = get_object_or_404(Listing, pk=listing_id)
        text = request.POST["comment"]
        
        comment = Comment(listing=listing, commenter=request.user, text=text)
        comment.save()
        
        return HttpResponseRedirect(reverse("listing", args=[listing_id]))


def categories(request):
    return render(request, "auctions/categories.html", {
        "categories": Category.objects.all()
    })


def category(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    listings = category.listings.filter(active=True)
    
    return render(request, "auctions/category_detail.html", {
        "category": category,
        "listings": listings
    })