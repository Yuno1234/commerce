from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from .models import *
from django import forms
from django.db.models import Max

class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ['title', 'description', 'startBid', 'category', 'image']
        widgets = {
            "title": forms.TextInput(attrs={'class': 'form-control col-md-8 col-lg-8 m-2'}),
            "description": forms.Textarea(attrs={'class': 'form-control col-md-8 col-lg-8 m-2'}),
            "startBid": forms.NumberInput(attrs={'class': 'form-control col-md-8 col-lg-8 m-2', 'step': 0.01}),
            "category": forms.Select(attrs={'class': 'form-control col-md-8 col-lg-8 m-2'}),
            "image": forms.URLInput(attrs={'class': 'form-control col-md-8 col-lg-8 m-2'})
        }

class BidForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ["bid"]
        widgets = {
            "bid": forms.NumberInput(attrs={'class': 'form-control col-md-8 col-lg-8 m-1', 'step': 0.01})
        }
        

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["text"]
        widgets = {
            "text": forms.Textarea(attrs={'class': 'form-control col-md-8 col-lg-8 m-2', 'rows': 3}),
        }
        labels = {
            "text": ""
        }

def index(request):
    if "filter" in request.GET:
        listings = Listing.objects.all()
        
        if request.GET.get('category') != "all":
            category = Category.objects.get(category=request.GET.get('category'))
            listings = listings.filter(category=category)

        if request.GET.get('isActive') != "all":
            listings = listings.filter(isActive=request.GET.get('isActive'))

        if request.GET.get('watchlist') == "on":
            listings = listings.filter(watchers = request.user)

        return render(request, "auctions/index.html", {
            "listings": listings,
            "categories": Category.objects.all(),
        })
    else:
        return render(request, "auctions/index.html", {
            "listings": Listing.objects.all(),
            "categories": Category.objects.all(),
        })


def createListing(request):
    if request.method =="POST":
        form = ListingForm(request.POST)
        if form.is_valid():
            newListing = form.save(commit=False)
            newListing.seller = request.user
            newListing.save()
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/createListing.html", {
                "form": form,
                "message": "Input was invalid"
            })
    else:
        return render(request, "auctions/createListing.html", {
            "form": ListingForm()
        })


def listing(request, listing_id):
    if not request.user.is_authenticated:
        return render(request, 'auctions/login.html')

    listing = Listing.objects.get(id=listing_id)
    comments = listing.get_comments.all().order_by('-date')
    isWatched = request.user in listing.watchers.all()

    if request.method == "POST":
        bidform = BidForm(request.POST)
        commentform = CommentForm(request.POST)

        if "bid_sub" in request.POST:
            bid = float(request.POST["bid"])
            if (bidform.is_valid() and (bid > listing.startBid) and (bid > (listing.currentBid or 0.0))):
                newBid = bidform.save(commit=False)
                newBid.user = request.user
                newBid.listing = listing
                newBid.save()
                listing.currentBid = bid
                listing.save()
                return render(request, "auctions/listing.html", {
                    "listing": listing,
                    "isWatched": isWatched,
                    "bidForm": BidForm(),
                    "success_message": "Your bid was succcessfully placed.",
                    "currentUser": request.user,
                    "commentForm": commentform,
                    "comments": comments
                })
            else:
                return render(request, "auctions/listing.html", {
                    "listing": listing,
                    "isWatched": isWatched,
                    "bidForm": bidform,
                    "danger_message": "Input was invalid",
                    "currentUser": request.user,
                    "commentForm": commentform,
                    "comments": comments
                })
        elif "close_sub" in request.POST:
            listing.isActive = False
            listing.buyer = Bid.objects.filter(listing=listing).order_by('-bid')[0].user
            listing.save()
            return render(request, "auctions/listing.html", {
                    "listing": listing,
                    "isWatched": isWatched,
                    "success_message": "You have successfully closed this auction.",
                    "currentUser": request.user,
                    "commentForm": commentform,
                    "comments": comments
                })
        elif "watchlist_sub" in request.POST:
            if request.user in listing.watchers.all():
                isWatched = False
                listing.watchers.remove(request.user)
            else:
                isWatched = True
                listing.watchers.add(request.user)
            return render(request, "auctions/listing.html", {
                    "listing": listing,
                    "isWatched": isWatched,
                    "bidForm": bidform,
                    "currentUser": request.user,
                    "commentForm": commentform,
                    "comments": comments
                })
        else:
            newComment = commentform.save(commit=False)
            newComment.user = request.user
            newComment.listing = listing
            newComment.save()
            return render(request, "auctions/listing.html", {
                "listing": listing,
                "isWatched": isWatched,
                "currentUser": request.user,
                "bidForm": BidForm(),
                "commentForm": CommentForm(),
                "comments": comments
            })
    else:
        return render(request, "auctions/listing.html", {
            "listing": listing,
            "isWatched": isWatched,
            "currentUser": request.user,
            "bidForm": BidForm(),
            "commentForm": CommentForm(),
            "comments": comments
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