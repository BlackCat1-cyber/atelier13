from django.conf import settings
from django.db import models


class CareTask(models.Model):
    WORK_CHOICES = [
        ("washing", "Стирка"),
        ("steaming", "Отпаривание"),
        ("repair", "Ремонт"),
    ]
    STATUS_CHOICES = [
        ("pending", "Ожидает"),
        ("in_progress", "В работе"),
        ("done", "Выполнено"),
        ("failed", "Не удалось / в ремонте"),
    ]

    booking = models.ForeignKey(
        "app_bookings.Booking", on_delete=models.CASCADE,
        related_name="care_tasks", verbose_name="Бронирование"
    )
    costume = models.ForeignKey(
        "app_catalog.Costume", on_delete=models.PROTECT,
        related_name="care_tasks", verbose_name="Костюм"
    )
    master = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="care_tasks",
        limit_choices_to={"profile__role": "master"},
        verbose_name="Мастер"
    )
    work_type = models.CharField(max_length=20, choices=WORK_CHOICES, verbose_name="Вид работы")
    planned_date = models.DateField(verbose_name="Плановая дата")
    actual_date = models.DateField(null=True, blank=True, verbose_name="Фактическая дата")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending", verbose_name="Статус")
    comment = models.CharField(max_length=500, blank=True, verbose_name="Комментарий")

    class Meta:
        verbose_name = "Задача по уходу"
        verbose_name_plural = "Задачи по уходу"
        ordering = ["planned_date"]

    def __str__(self):
        return f"{self.get_work_type_display()} — {self.costume.article} ({self.planned_date})"