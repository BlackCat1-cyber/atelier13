from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class Deposit(models.Model):
    STATUS_CHOICES = [
        ("paid", "Внесён"),
        ("partially_withheld", "Частично удержан"),
        ("returned", "Возвращён"),
    ]

    booking = models.OneToOneField(
        "app_bookings.Booking", on_delete=models.CASCADE,
        related_name="deposit", verbose_name="Бронирование"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма залога")
    withheld = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Удержано")
    to_return = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="К возврату")
    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default="paid", verbose_name="Статус")

    class Meta:
        verbose_name = "Залог"
        verbose_name_plural = "Залоги"

    def __str__(self):
        return f"Залог по брони #{self.booking_id}: {self.amount} ₽"


class DamagePrice(models.Model):
    damage_type = models.CharField(max_length=50, verbose_name="Тип повреждения")
    severity = models.CharField(max_length=50, verbose_name="Степень")
    repair_cost = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Стоимость ремонта"
    )
    is_archived = models.BooleanField(default=False, verbose_name="В архиве")

    class Meta:
        verbose_name = "Позиция прайса повреждений"
        verbose_name_plural = "Прайс повреждений"
        ordering = ["damage_type", "severity"]

    def __str__(self):
        return f"{self.damage_type} ({self.severity}) — {self.repair_cost} ₽"


class Inspection(models.Model):
    CONCLUSION_CHOICES = [
        ("good", "Без повреждений"),
        ("damaged", "Есть повреждения"),
    ]

    booking = models.OneToOneField(
        "app_bookings.Booking", on_delete=models.CASCADE,
        related_name="inspection", verbose_name="Бронирование"
    )
    inspector = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name="inspections",
        limit_choices_to={"profile__role": "consultant"},
        verbose_name="Принимающий сотрудник"
    )
    inspection_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата осмотра")
    general_condition = models.TextField(verbose_name="Общее состояние")
    conclusion = models.CharField(max_length=20, choices=CONCLUSION_CHOICES, verbose_name="Заключение")

    class Meta:
        verbose_name = "Акт осмотра"
        verbose_name_plural = "Акты осмотра"

    def __str__(self):
        return f"Акт #{self.id} по брони #{self.booking_id}"


class Damage(models.Model):
    inspection = models.ForeignKey(
        Inspection, on_delete=models.CASCADE,
        related_name="damages", verbose_name="Акт осмотра"
    )
    price_item = models.ForeignKey(
        DamagePrice, on_delete=models.PROTECT,
        related_name="damages", verbose_name="Позиция прайса"
    )
    description = models.CharField(max_length=500, blank=True, verbose_name="Описание")
    photo = models.ImageField(upload_to="damages/", blank=True, verbose_name="Фото")
    cost = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма")

    class Meta:
        verbose_name = "Повреждение"
        verbose_name_plural = "Повреждения"

    def __str__(self):
        return f"{self.price_item.damage_type}: {self.cost} ₽"