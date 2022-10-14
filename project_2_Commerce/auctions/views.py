from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models import F
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _
from django.urls import reverse

from .models import Bid, User, Listing, Watchlist, Comment
from .forms import AddListing, BidForm

def index(request):
    items = Listing.objects.filter(active=True)
    return render(request, "auctions/index.html", {
        "items": items,
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


@login_required
def add_listing(request):
    """Render page for addinng new listing"""
    if request.method == "POST":
        form = AddListing(request.POST)
        if form.is_valid():
            owner = request.user
            title = form.cleaned_data['title']
            category = form.cleaned_data['category']
            bid = form.cleaned_data['starting_bid']
            url = form.cleaned_data['url']
            description = form.cleaned_data['description']
            listing = Listing(owner=owner, title=title, category=category,
                              starting_bid=bid, url=url, description=description)
            listing.save()    
            return redirect('index')
        else:
            render(request, 'auctions/add_listing.html', {
                "form": form
            })

    else:
        form = AddListing()

    return render(request, "auctions/add_listing.html", {
        "form": form
    })


def listing(request, lst_id):
    # get active user
    user = request.user

    # query requested listing or error page
    listing = get_object_or_404(Listing, pk=lst_id)

    # get the lattest bid on listing or none if no bids placed
    bids = Bid.objects.filter(listing=listing)
    bid = bids.last()

    # define the initial value for bid to display
    init_bid = bid.amount if bid else listing.starting_bid
    form = BidForm(initial={'last_bid': init_bid})

    # get all comments for this listing, most recent first  
    comments = Comment.objects.filter(listing=listing).order_by('-pub_time')
    
    # get user watchlist, 'check' checks for listing in favorites
    if user.is_authenticated:
        wl = Watchlist.objects.filter(person=user).first()
        if wl is not None:
            check = listing in wl.items.all()
        else:
            wl = Watchlist.objects.create(person=user)
            check = False

    else:
        check = False

    # close listing button behavior
    if request.method == "POST" and "close" in request.POST:
        if listing.active:
            listing.active = False
        else:
            listing.active = True
        listing.save()
        return redirect("index")
    
    # favorite icon changing logic
    if request.method == "POST" and "favorite" in request.POST:
            if check:
                wl.items.remove(listing)
            else:
                wl.items.add(listing)
            return redirect("listing", lst_id)

    # 'place bid' button behavior
    if request.method =="POST" and  "last_bid" in request.POST:
        form = BidForm(request.POST)
        
        if float(request.POST['last_bid']) <= float(init_bid):
            form.add_error('last_bid', 
                            ValidationError(_('Your bid must by greater than $%(value)s'),
                                            params={'value': init_bid}))  

        if form.is_valid():
            last_bid = form.cleaned_data["last_bid"]

            Bid.objects.create(bidder=user, listing=listing,
                                amount=last_bid)
           
            return redirect('listing', lst_id)

    return render(request, "auctions/listing.html", {
        "listing": listing, "check": check, "form": form, 
        "bid": bid, "count": bids.count(), "comments": comments,
    })


@login_required
def watchlist(request):
    user = request.user
    watchlist = Watchlist.objects.filter(person=user).first()
    items = watchlist.items.all()
    return render(request, 'auctions/watchlist.html', {
        'items': items,
    })


def comments(request, lst_id):
    listing = Listing.objects.get(pk=lst_id)
    user = request.user
    if request.method == "POST":
        text = request.POST['comment']
        Comment.objects.create(listing=listing, author=user, text=text)
        return redirect('listing', lst_id)


def categories(request):
    categories = Listing.objects.values('category').distinct()
    return render(request, 'auctions/index.html', {
        "categories": categories,
    })


def category(request, category):
    items = Listing.objects.filter(category=category)
    return render(request, 'auctions/index.html', {
        "category": category,
        "items": items,
    })