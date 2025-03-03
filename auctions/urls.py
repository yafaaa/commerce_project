from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("listings/<int:listing_id>", views.listing_detail, name="listing"),
    path("create", views.create_listing, name="create"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("watchlist/<int:listing_id>/toggle", views.toggle_watchlist, name="toggle_watchlist"),
    path("listings/<int:listing_id>/bid", views.place_bid, name="place_bid"),
    path("listings/<int:listing_id>/close", views.close_auction, name="close_auction"),
    path("listings/<int:listing_id>/comment", views.add_comment, name="add_comment"),
    path("categories", views.categories, name="categories"),
    path("categories/<int:category_id>", views.category, name="category")
]