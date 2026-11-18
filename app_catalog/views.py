from django.db.models import Count
from django.shortcuts import render

from .models import Category, Costume, Theme


def home(request):
    categories = Category.objects.annotate(n=Count("costumes"))
    popular = (Costume.objects.filter(status="available")
               .select_related("category", "size_params")
               .order_by("daily_price")[:4])
    stats = [
        (Costume.objects.count(), "нарядов в каталоге"),
        (Category.objects.count(), "категории нарядов"),
        (Theme.objects.count(), "тематик мероприятий"),
        (Costume.objects.filter(status="available").count(), "свободны сейчас"),
    ]
    return render(request, "home.html", {
        "categories": categories,
        "popular": popular,
        "stats": stats,
    })