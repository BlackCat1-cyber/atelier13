from datetime import timedelta

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class FittingSlot(models.Model):
    STATUS_CHOICES = [
        ("free", "Свободен"),
        ("booked", "Записан"),
        ("completed", "Состоялся"),
        ("cancelled", "Отменён"),
    ]
    RESULT_CHOICES = [
        ("fitted", "Подошёл"),
        ("not_fitted", "Не подошёл"),
    ]

    slot_datetime = models.DateTimeField(verbose_name="Дата и время слота")
    consultant = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name="consultant_slots",
        limit_choices_to={"profile__role": "consultant"},
        verbose_name="Консультант"
    )
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="client_slots",
        limit_choices_to={"profile__role": "client"},
        verbose_name="Клиент"
    )
    costumes = models.ManyToManyField(
        "app_catalog.Costume", through="FittingCostume",
        related_name="fitting_slots", verbose_name="Наряды"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="free", verbose_name="Статус")
    result = models.CharField(max_length=20, choices=RESULT_CHOICES, blank=True, null=True, verbose_name="Результат")

    class Meta:
        verbose_name = "Слот примерки"
        verbose_name_plural = "Слоты примерок"
        ordering = ["slot_datetime"]
        constraints = [
            models.UniqueConstraint(
                fields=["slot_datetime", "consultant"], name="uniq_slot_consultant"
            ),
        ]

    def __str__(self):
        return f"{self.slot_datetime:%d.%m.%Y %H:%M} — {self.consultant}"


class FittingCostume(models.Model):
    slot = models.ForeignKey(FittingSlot, on_delete=models.CASCADE)
    costume = models.ForeignKey("app_catalog.Costume", on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["slot", "costume"], name="uniq_slot_costume"),
        ]


class Booking(models.Model):
    STATUS_CHOICES = [
        ("pending", "Ожидает выдачи"),
        ("issued", "Выдан"),
        ("returned", "Возвращён"),
        ("cancelled", "Отменён"),
    ]

    client = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name="bookings",
        limit_choices_to={"profile__role": "client"},
        verbose_name="Клиент"
    )
    costume = models.ForeignKey(
        "app_catalog.Costume", on_delete=models.PROTECT,
        related_name="bookings", verbose_name="Костюм"
    )
    date_start = models.DateField(verbose_name="Дата начала аренды")
    date_end = models.DateField(verbose_name="Дата возврата")
    blocked_until = models.DateField(verbose_name="Дата окончания блокировки (+2 дня)")
    actual_return_date = models.DateField(null=True, blank=True, verbose_name="Фактическая дата возврата")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Стоимость аренды")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending", verbose_name="Статус")
    terms_accepted = models.BooleanField(default=False, verbose_name="Условия приняты")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Бронирование"
        verbose_name_plural = "Бронирования"
        ordering = ["-date_start"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(date_end__gt=models.F("date_start")),
                name="booking_end_after_start",
            ),
        ]

    def clean(self):
        if self.date_start and self.date_start < timezone.localdate():
            raise ValidationError("Дата начала не может быть в прошлом.")
        if self.blocked_until != self.date_end + timedelta(days=2):
            raise ValidationError("Буфер +2 дня рассчитан неверно.")

    def __str__(self):
        return f"Бронь #{self.id}: {self.costume.article} ({self.date_start} — {self.date_end})"