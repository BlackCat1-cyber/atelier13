import datetime as dt
from django.contrib.auth.models import User
from app_bookings.models import Booking
from app_care.models import CareTask

sidorov = User.objects.get(username="sidorov")

CareTask.objects.all().delete()

bookings = list(Booking.objects.all().order_by("id"))

for b in bookings:
    prep_status = "done" if b.status in ("issued", "returned") else "pending"
    actual = b.date_start - dt.timedelta(days=1) if prep_status == "done" else None
    CareTask.objects.create(booking=b, costume=b.costume, master=sidorov, work_type="steaming", planned_date=b.date_start - dt.timedelta(days=1), actual_date=actual, status=prep_status, comment="Отпаривание перед выдачей")

for b in bookings:
    if b.status == "returned":
        CareTask.objects.create(booking=b, costume=b.costume, master=sidorov, work_type="washing", planned_date=b.actual_return_date + dt.timedelta(days=1), actual_date=b.actual_return_date + dt.timedelta(days=1), status="done", comment="Стирка после возврата")

b7 = bookings[6]

CareTask.objects.create(booking=b7, costume=b7.costume, master=sidorov, work_type="repair", planned_date=dt.date(2026, 11, 2), actual_date=None, status="in_progress", comment="Замена молнии")

print("Задач по уходу:", CareTask.objects.count())