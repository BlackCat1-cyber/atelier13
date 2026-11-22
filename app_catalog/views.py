from decimal import Decimal, InvalidOperation

from django.core.paginator import Paginator
from django.db.models import Count
from django.shortcuts import get_object_or_404, render

from .models import Category, Costume, Theme

MAX_DB_INT = 2 ** 31 - 1


def _int_param(value):
    """Целое число из параметра адреса. Мусор («abc», отрицательные и слишком большие числа) -> None."""
    try:
        number = int(value)
    except (TypeError, ValueError):
        return None
    return number if 0 <= number <= MAX_DB_INT else None


def _decimal_param(value):
    """Неотрицательная конечная цена из параметра адреса или None («NaN», «abc», слишком большие)."""
    try:
        number = Decimal(value)
    except (TypeError, InvalidOperation):
        return None
    if not number.is_finite() or number < 0 or number > Decimal("99999999.99"):
        return None
    return number


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


def _search_ids(text):
    """id нарядов, у которых название, артикул или описание содержат text без учёта регистра.

    SQLite (LIKE и lower()) не различает регистр только у латиницы, поэтому «платье» не находило «Платье».
    Каталог небольшой, поэтому сравниваем в Python через casefold().
    """
    needle = text.casefold()
    return [pk for pk, *fields in Costume.objects.values_list("pk", "name", "article", "description")
            if any(needle in (f or "").casefold() for f in fields)]


def _filtered(params):
    qs = Costume.objects.select_related("category", "size_params").prefetch_related("themes")
    q = (params.get("q") or "").strip()
    if q:
        qs = qs.filter(pk__in=_search_ids(q))
    category = _int_param(params.get("category"))
    if category is not None:
        qs = qs.filter(category_id=category)
    theme = _int_param(params.get("theme"))
    if theme is not None:
        qs = qs.filter(themes__id=theme)
    size = _int_param(params.get("size"))
    if size is not None:
        qs = qs.filter(size_params__size=size)
    max_price = _decimal_param(params.get("max_price"))
    if max_price is not None:
        qs = qs.filter(daily_price__lte=max_price)
    if params.get("available") == "1":
        qs = qs.filter(status="available")
    order = {"price_asc": "daily_price", "price_desc": "-daily_price",
             "name": "name", "size": "size_params__size"}.get(params.get("sort") or "price_asc", "daily_price")
    return qs.order_by(order).distinct()


def catalog(request):
    qs = _filtered(request.GET)
    page = Paginator(qs, 20).get_page(request.GET.get("page"))
    params = request.GET.copy()
    params.pop("page", None)
    qs_str = params.urlencode()
    qs_str = qs_str + "&" if qs_str else ""
    return render(request, "catalog.html", {
        "page": page,
        "qs": qs_str,
        "categories": Category.objects.all(),
        "themes": Theme.objects.all(),
        "sizes": range(38, 63, 2),
        "cur_q": request.GET.get("q", ""),
        "cur_category": request.GET.get("category", ""),
        "cur_theme": request.GET.get("theme", ""),
        "cur_size": request.GET.get("size", ""),
        "cur_price": request.GET.get("max_price", ""),
        "cur_available": request.GET.get("available", ""),
        "cur_sort": request.GET.get("sort", "price_asc"),
    })


def costume(request, pk):
    c = get_object_or_404(
        Costume.objects.select_related("category", "size_params").prefetch_related("themes"), pk=pk)
    related = (Costume.objects.filter(category=c.category).exclude(pk=c.pk)
               .select_related("category", "size_params")[:3])
    completeness = [x.strip() for x in c.completeness.split(",") if x.strip()]
    return render(request, "costume.html", {
        "c": c,
        "related": related,
        "completeness": completeness,
    })

def terms(request):
    return render(request, "terms.html")
from django.contrib import messages
from django.shortcuts import redirect
from datetime import date, timedelta, datetime


MAX_FITTING_COSTUMES = 3


def _fitting_count(value):
    """Количество нарядов для примерки (1–3) или None, если значение некорректно."""
    try:
        number = int(value)
    except (TypeError, ValueError):
        return None
    return number if 1 <= number <= MAX_FITTING_COSTUMES else None


def fitting(request):
    if request.method == "POST":
        fitting_date = request.POST.get("fitting_date")
        fitting_time = request.POST.get("fitting_time")
        count = request.POST.get("costume_count")
        if not (fitting_date and fitting_time and count):
            messages.error(request, "Заполните все обязательные поля.")
        elif _fitting_count(count) is None:
            messages.error(request, f"Количество нарядов должно быть целым числом от 1 до {MAX_FITTING_COSTUMES}.")
        else:
            messages.success(request, f"Вы записаны на примерку {fitting_date} в {fitting_time}. Мы свяжемся с вами для подтверждения.")
            return redirect("fitting")
    today = date.today().isoformat()
    times = [f"{h:02d}:00" for h in range(10, 20)]
    return render(request, "fitting.html", {"today": today, "times": times})

def booking(request):
    costumes = Costume.objects.filter(status="available").order_by("name")
    costume = None
    total = None
    days = 0
    price = 0
    deposit = 0
    today = date.today().isoformat()

    if request.method == "POST":
        costume_id = request.POST.get("costume_id")
        start = request.POST.get("start_date")
        end = request.POST.get("end_date")
        if costume_id and start and end:
            try:
                costume = Costume.objects.get(pk=costume_id)
                d1 = date.fromisoformat(start)
                d2 = date.fromisoformat(end)
                if d2 <= d1:
                    messages.error(request, "Дата возврата должна быть позже даты начала.")
                else:
                    days = (d2 - d1).days
                    price = int(costume.daily_price)
                    deposit = int(costume.deposit_amount)
                    total = days * price + deposit
                    messages.success(request, f"Бронь оформлена: {days} сут. × {price} ₽ + залог {deposit} ₽ = {total} ₽")
            except Costume.DoesNotExist:
                messages.error(request, "Наряд не найден.")
            except ValueError:
                messages.error(request, "Неверный формат даты.")
        else:
            messages.error(request, "Заполните все обязательные поля.")
    return render(request, "booking.html", {
        "costumes": costumes,
        "costume": costume,
        "today": today,
        "total": total,
        "days": days,
        "price": price,
        "deposit": deposit,
    })
def account(request):
    user_name = "Гость"
    user_email = ""
    user_phone = ""
    bookings = []

    if request.method == "POST":
        user_name = request.POST.get("name", "Гость")
        user_email = request.POST.get("email", "")
        user_phone = request.POST.get("phone", "")
        messages.success(request, "Профиль обновлён.")

    bookings = [
        {"costume": "Платье «Аврора»", "start": "2026-11-25", "end": "2026-11-27", "days": 2, "total": 8000},
        {"costume": "Смокинг «Джеймс»", "start": "2026-12-01", "end": "2026-12-03", "days": 2, "total": 7000},
    ]

    return render(request, "account.html", {
        "user_name": user_name,
        "user_email": user_email,
        "user_phone": user_phone,
        "bookings": bookings,
    })