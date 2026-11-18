from django.db.models import Count, Sum, Avg, Q
from app_catalog.models import Costume
from app_bookings.models import Booking

print("=== Запрос 1. Фильтрация по условию + сортировка ===")
q1 = Costume.objects.filter(category__name="Вечернее платье", daily_price__lte=4000, status="available").order_by("daily_price")
print(str(q1.query))
for c in q1:
    print(c.article, c.name, c.daily_price)

print()
print("=== Запрос 2. Агрегация Count/Avg/Sum по категориям ===")
q2 = Costume.objects.values("category__name").annotate(total=Count("id"), avg_price=Avg("daily_price"), sum_deposit=Sum("deposit_amount")).order_by("category__name")
print(str(q2.query))
for row in q2:
    print(row)

print()
print("=== Запрос 3. Связь один-ко-многим через select_related ===")
q3 = Booking.objects.filter(client__username="ivanov", status__in=["pending", "issued"]).select_related("costume", "costume__category").order_by("date_start")
print(str(q3.query))
for b in q3:
    print(b.id, b.costume.article, b.costume.category.name, b.total_price)

print()
print("=== Запрос 4. Связь многие-ко-многим через prefetch_related ===")
q4 = Costume.objects.filter(category__name="Смокинг").prefetch_related("themes").order_by("article")
for c in q4:
    print(c.article, "-", ", ".join(t.name for t in c.themes.all()))

print()
print("=== Запрос 5. Аннотация + фильтрация по агрегату (HAVING) ===")
q5 = Booking.objects.values("costume__category__name").annotate(bookings_count=Count("id"), revenue=Sum("total_price", filter=Q(status__in=["issued", "returned"]))).filter(bookings_count__gte=2).order_by("-revenue")
print(str(q5.query))
for row in q5:
    print(row)