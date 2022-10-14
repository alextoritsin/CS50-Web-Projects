from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("add_listing", views.add_listing, name="add_listing"),
    path("listing/<int:lst_id>", views.listing, name="listing"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("listing/<int:lst_id>/comment", views.comments, name="comment" ),
    path("categories", views.categories, name="categories"),
    path("category/<str:category>", views.category, name="category"),
]
