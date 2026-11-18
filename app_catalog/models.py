from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Название категории")
    description = models.TextField(blank=True, verbose_name="Описание")

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Theme(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Тематика")
    description = models.TextField(blank=True, verbose_name="Описание")

    class Meta:
        verbose_name = "Тематика"
        verbose_name_plural = "Тематики"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Costume(models.Model):
    STATUS_CHOICES = [
        ("available", "Доступен"),
        ("in_repair", "В ремонте"),
        ("written_off", "Списан"),
    ]

    article = models.CharField(max_length=20, unique=True, verbose_name="Артикул")
    name = models.CharField(max_length=150, verbose_name="Название")
    description = models.TextField(blank=True, verbose_name="Описание")
    photo = models.ImageField(upload_to="costumes/", blank=True, verbose_name="Фото")
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name="costumes", verbose_name="Категория"
    )
    themes = models.ManyToManyField(
        Theme, through="CostumeTheme", related_name="costumes", verbose_name="Тематики"
    )
    daily_price = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Цена за сутки"
    )
    deposit_amount = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Сумма залога"
    )
    completeness = models.CharField(max_length=500, verbose_name="Комплектность")
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="available", verbose_name="Статус"
    )

    class Meta:
        verbose_name = "Костюм"
        verbose_name_plural = "Костюмы"
        ordering = ["article"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(daily_price__gte=0, deposit_amount__gte=0),
                name="costume_prices_non_negative",
            ),
        ]

    def __str__(self):
        return f"{self.article} — {self.name}"


class CostumeTheme(models.Model):
    costume = models.ForeignKey(Costume, on_delete=models.CASCADE)
    theme = models.ForeignKey(Theme, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Тематика костюма"
        verbose_name_plural = "Тематики костюмов"
        constraints = [
            models.UniqueConstraint(fields=["costume", "theme"], name="uniq_costume_theme"),
        ]

    def __str__(self):
        return f"{self.costume} → {self.theme}"


class SizeParams(models.Model):
    costume = models.OneToOneField(
        Costume, on_delete=models.CASCADE, related_name="size_params", verbose_name="Костюм"
    )
    size = models.IntegerField(
        validators=[MinValueValidator(38), MaxValueValidator(62)], verbose_name="Размер"
    )
    height_from = models.IntegerField(
        validators=[MinValueValidator(140), MaxValueValidator(220)], verbose_name="Рост от, см"
    )
    height_to = models.IntegerField(
        validators=[MinValueValidator(140), MaxValueValidator(220)], verbose_name="Рост до, см"
    )
    bust_girth = models.IntegerField(
        validators=[MinValueValidator(70), MaxValueValidator(140)], verbose_name="Обхват груди"
    )
    waist_girth = models.IntegerField(
        validators=[MinValueValidator(60), MaxValueValidator(120)], verbose_name="Обхват талии"
    )
    hips_girth = models.IntegerField(
        validators=[MinValueValidator(70), MaxValueValidator(140)], verbose_name="Обхват бёдер"
    )
    item_length = models.IntegerField(
        blank=True, null=True,
        validators=[MinValueValidator(50), MaxValueValidator(180)],
        verbose_name="Длина изделия"
    )

    class Meta:
        verbose_name = "Размер и параметры"
        verbose_name_plural = "Размеры и параметры"

    def __str__(self):
        return f"{self.costume.article}: р.{self.size}, рост {self.height_from}-{self.height_to}"