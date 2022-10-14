from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("random", views.random_entry, name="random"),
    path("search", views.search, name="search"),
    path("wiki/<str:entry_name>", views.entry, name="entry"),
    path("newpage", views.newpage, name="newpage"),
    path("edit/<str:entry_name>", views.edit_entry, name="edit_entry")
]