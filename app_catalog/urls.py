from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("catalog/", views.catalog, name="catalog"),
    path("catalog/<int:pk>/", views.costume, name="costume"),
    path("terms/", views.terms, name="terms"),
    path("fitting/", views.fitting, name="fitting"),
    path("booking/", views.booking, name="booking"),
    path("account/", views.account, name="account"),
]