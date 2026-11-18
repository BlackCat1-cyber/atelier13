import datetime as dt
from django.contrib.auth.models import User
from app_accounts.models import Profile
from app_catalog.models import Category, Theme, Costume, CostumeTheme, SizeParams
from app_bookings.models import Booking, FittingSlot, FittingCostume
from app_inspections.models import Deposit, DamagePrice, Inspection, Damage
from app_care.models import CareTask

# очистка, чтобы скрипт можно было запускать повторно
for m in (Damage, Inspection, Deposit, CareTask, FittingCostume, FittingSlot,
          Booking, SizeParams, CostumeTheme, Costume, Theme, Category,
          DamagePrice, Profile):
    m.objects.all().delete()
User.objects.all().delete()

# пользователи 5 ролей
for u, e, p, r, ph, h, s in [
    ("admin", "admin@rental.ru", "admin123", "admin", "+79001111111", None, None),
    ("ivanov", "ivanov@mail.ru", "client123", "client", "+79002222222", 175, 48),
    ("smirnova", "smirnova@mail.ru", "client123", "client", "+79005555555", 168, 44),
    ("petrova", "petrova@rental.ru", "consult123", "consultant", "+79003333333", None, None),
    ("sidorov", "sidorov@rental.ru", "master123", "master", "+79004444444", None, None),
]:
    user = User.objects.create_user(username=u, email=e, password=p)
    Profile.objects.create(user=user, role=r, phone=ph, height_cm=h, clothing_size=s)

ivanov = User.objects.get(username="ivanov")
smirnova = User.objects.get(username="smirnova")
petrova = User.objects.get(username="petrova")
sidorov = User.objects.get(username="sidorov")

cats = [
    Category.objects.create(name="Вечернее платье", description="Платья для торжеств"),
    Category.objects.create(name="Смокинг", description="Мужские смокинги"),
    Category.objects.create(name="Карнавальный костюм", description="Карнавальные и исторические"),
    Category.objects.create(name="Коктейльное платье", description="Коктейльные платья"),
]
themes = [
    Theme.objects.create(name="Свадьба"), Theme.objects.create(name="Выпускной"),
    Theme.objects.create(name="Хэллоуин"), Theme.objects.create(name="Ретро"),
    Theme.objects.create(name="Новогодний"), Theme.objects.create(name="Тематическая вечеринка"),
]

# артикул, название, категория, цена, залог, комплектность, размер, рост от, рост до, грудь, талия, бёдра, длина, тематики
COSTUMES = [
    ("PL-2026-001", "Платье «Аврора»", 0, 3500, 15000, "Платье, пояс, перчатки", 44, 165, 175, 88, 68, 94, 140, [0, 1]),
    ("PL-2026-002", "Платье «Виктория»", 0, 3200, 14000, "Платье", 46, 165, 175, 92, 72, 98, 135, [0]),
    ("PL-2026-003", "Платье «Беатрис»", 0, 2800, 12000, "Платье, боа", 48, 160, 170, 96, 76, 102, 130, [1]),
    ("PL-2026-004", "Платье «Селена»", 0, 4000, 18000, "Платье, колье", 44, 170, 180, 88, 68, 94, 150, [0]),
    ("PL-2026-005", "Платье «Диана»", 0, 2500, 10000, "Платье", 42, 160, 170, 84, 64, 90, 90, [5]),
    ("PL-2026-006", "Платье «Ева»", 0, 3900, 16000, "Платье, шлейф", 46, 165, 175, 92, 72, 98, 145, [0]),
    ("PL-2026-007", "Платье «Флора»", 0, 3700, 15000, "Платье", 48, 165, 175, 96, 76, 102, 140, [1]),
    ("PL-2026-008", "Платье «Грация»", 0, 4500, 20000, "Платье, перчатки, диадема", 50, 170, 180, 100, 80, 106, 150, [0]),
    ("PL-2026-009", "Платье «Изабелла»", 0, 3600, 15000, "Платье", 44, 160, 170, 88, 68, 94, 135, [0]),
    ("PL-2026-010", "Платье «Лилия»", 0, 3300, 14000, "Платье, юбка", 46, 165, 175, 92, 72, 98, 140, [1]),
    ("PL-2026-011", "Платье «Мелоди»", 0, 3100, 13000, "Платье", 48, 160, 170, 96, 76, 102, 130, [5]),
    ("PL-2026-012", "Платье «Николь»", 0, 2900, 12000, "Платье, палантин", 44, 165, 175, 88, 68, 94, 135, [1]),
    ("SM-2026-001", "Смокинг «Классик»", 1, 4200, 18000, "Пиджак, брюки, бабочка", 50, 175, 185, 100, 86, 102, None, [0]),
    ("SM-2026-002", "Смокинг «Премиум»", 1, 5000, 22000, "Полный комплект", 52, 180, 190, 104, 90, 106, None, [0]),
    ("SM-2026-003", "Смокинг «Модерн»", 1, 4500, 20000, "Пиджак, брюки, запонки", 48, 175, 185, 96, 82, 100, None, [5]),
    ("SM-2026-004", "Смокинг «Элегант»", 1, 4300, 19000, "Полный комплект", 50, 175, 185, 100, 86, 102, None, [0]),
    ("SM-2026-005", "Смокинг «Блэк»", 1, 5500, 25000, "Полный комплект", 54, 180, 190, 108, 94, 110, None, [0]),
    ("SM-2026-006", "Смокинг «Стандарт»", 1, 3800, 16000, "Пиджак, брюки", 48, 170, 180, 96, 82, 100, None, [3]),
    ("SM-2026-007", "Смокинг «Люкс»", 1, 6000, 28000, "Полный комплект", 52, 180, 190, 104, 90, 106, None, [0]),
    ("SM-2026-008", "Смокинг «Винтаж»", 1, 4100, 18000, "Полный комплект", 50, 175, 185, 100, 86, 102, None, [5]),
    ("SM-2026-009", "Смокинг «Оксфорд»", 1, 4700, 21000, "Полный комплект", 52, 180, 190, 104, 90, 106, None, [0]),
    ("SM-2026-010", "Смокинг «Монако»", 1, 4400, 19000, "Полный комплект", 50, 175, 185, 100, 86, 102, None, [5]),
    ("CR-2026-001", "Костюм «Пират»", 2, 2800, 12000, "Рубашка, жилет, брюки, шляпа", 50, 175, 185, 100, 86, 102, None, [5]),
    ("CR-2026-002", "Костюм «Мушкетёр»", 2, 3000, 13000, "Полный комплект со шпагой", 52, 175, 185, 104, 90, 106, None, [5]),
    ("CR-2026-003", "Костюм «Ведьма»", 2, 2500, 10000, "Платье, шляпа, метла", 46, 165, 175, 92, 72, 98, 120, [2]),
    ("CR-2026-004", "Костюм «Дед Мороз»", 2, 3200, 14000, "Шуба, шапка, мешок", 54, 175, 185, 108, 94, 110, None, [4]),
    ("CR-2026-005", "Костюм «Снегурочка»", 2, 2900, 12000, "Шубка, шапка", 44, 160, 170, 88, 68, 94, 110, [4]),
    ("CR-2026-006", "Костюм «Гарем»", 2, 2700, 11000, "Топ, шаровары, украшения", 46, 160, 170, 92, 72, 98, 115, [5]),
    ("CR-2026-007", "Костюм «Ковбой»", 2, 2600, 11000, "Рубашка, жилет, брюки, шляпа", 50, 175, 185, 100, 86, 102, None, [5]),
    ("CR-2026-008", "Костюм «Матрос»", 2, 2400, 10000, "Тельняшка, брюки, бескозырка", 48, 170, 180, 96, 82, 100, None, [5]),
    ("CK-2026-001", "Платье «Мини-блэк»", 3, 2900, 12000, "Платье", 42, 160, 170, 84, 64, 90, 85, [5]),
    ("CK-2026-002", "Платье «Роза»", 3, 3100, 13000, "Платье", 44, 160, 170, 88, 68, 94, 85, [5]),
    ("CK-2026-003", "Платье «Сапфир»", 3, 2800, 12000, "Платье", 46, 165, 175, 92, 72, 98, 90, [1]),
    ("CK-2026-004", "Платье «Изумруд»", 3, 3000, 13000, "Платье", 48, 165, 175, 96, 76, 102, 90, [5]),
    ("CK-2026-005", "Платье «Рубин»", 3, 2700, 11000, "Платье", 44, 160, 170, 88, 68, 94, 85, [1]),
]
costumes = []
for row in COSTUMES:
    c = Costume.objects.create(
        article=row[0], name=row[1], description="Демонстрационное описание",
        category=cats[row[2]], daily_price=row[3], deposit_amount=row[4],
        completeness=row[5], status="available",
    )
    SizeParams.objects.create(
        costume=c, size=row[6], height_from=row[7], height_to=row[8],
        bust_girth=row[9], waist_girth=row[10], hips_girth=row[11], item_length=row[12],
    )
    for t in row[13]:
        CostumeTheme.objects.create(costume=c, theme=themes[t])
    costumes.append(c)

prices = [
    DamagePrice.objects.create(damage_type="Пятно", severity="Лёгкое", repair_cost=500),
    DamagePrice.objects.create(damage_type="Пятно", severity="Среднее", repair_cost=1500),
    DamagePrice.objects.create(damage_type="Пятно", severity="Сложное", repair_cost=3000),
    DamagePrice.objects.create(damage_type="Разрыв", severity="До 5 см", repair_cost=1000),
    DamagePrice.objects.create(damage_type="Разрыв", severity="Более 5 см", repair_cost=2500),
    DamagePrice.objects.create(damage_type="Порез", severity="Лёгкий", repair_cost=800),
    DamagePrice.objects.create(damage_type="Порез", severity="Средний", repair_cost=2000),
    DamagePrice.objects.create(damage_type="Утеря детали", severity="Пуговица", repair_cost=300),
    DamagePrice.objects.create(damage_type="Утеря детали", severity="Молния", repair_cost=1500),
    DamagePrice.objects.create(damage_type="Прожог", severity="Лёгкий", repair_cost=2000),
    DamagePrice.objects.create(damage_type="Прожог", severity="Сильный", repair_cost=5000),
    DamagePrice.objects.create(damage_type="Запах", severity="Табак", repair_cost=1200),
]

D = dt.date
# клиент, костюм(номер), начало, конец, статус, факт.возврат
BOOKINGS = [
    (ivanov, 0, D(2026, 12, 5), D(2026, 12, 7), "pending", None),
    (ivanov, 12, D(2026, 12, 20), D(2026, 12, 22), "pending", None),
    (smirnova, 4, D(2026, 11, 25), D(2026, 11, 27), "issued", None),
    (smirnova, 22, D(2026, 10, 30), D(2026, 11, 1), "returned", D(2026, 11, 1)),
    (ivanov, 30, D(2026, 11, 15), D(2026, 11, 17), "issued", None),
    (smirnova, 13, D(2026, 12, 31), D(2027, 1, 2), "pending", None),
    (ivanov, 24, D(2026, 10, 28), D(2026, 10, 31), "returned", D(2026, 10, 31)),
    (smirnova, 1, D(2026, 11, 20), D(2026, 11, 22), "issued", None),
    (ivanov, 25, D(2026, 12, 25), D(2026, 12, 27), "pending", None),
    (smirnova, 31, D(2026, 11, 10), D(2026, 11, 12), "returned", D(2026, 11, 12)),
]
bookings = []
for client, ci, start, end, status, actual in BOOKINGS:
    c = costumes[ci]
    days = (end - start).days
    b = Booking.objects.create(
        client=client, costume=c, date_start=start, date_end=end,
        blocked_until=end + dt.timedelta(days=2), actual_return_date=actual,
        total_price=c.daily_price * days, status=status, terms_accepted=True,
    )
    bookings.append(b)

# залоги: для возвращённых удержание проставим ниже после актов
deposits = []
for b in bookings:
    dep = Deposit.objects.create(
        booking=b, amount=b.costume.deposit_amount, withheld=0,
        to_return=b.costume.deposit_amount, status="paid",
    )
    deposits.append(dep)

# акты осмотра и повреждения по возвращённым броням (номера броней: 3, 6, 9)
insp_data = [
    (3, "damaged", "Пятно от вина на подоле", [0]),
    (6, "damaged", "Разрыв рукава, утеряна пуговица, сломана молния, порез", [3, 7, 8, 5]),
    (9, "damaged", "Лёгкое пятно, запах табака, прожог", [0, 11, 9]),
]
for bi, concl, cond, dmg_idxs in insp_data:
    b = bookings[bi]
    ins = Inspection.objects.create(
        booking=b, inspector=petrova, general_condition=cond, conclusion=concl,
    )
    total = 0
    for pi in dmg_idxs:
        dp = prices[pi]
        Damage.objects.create(inspection=ins, price_item=dp,
                              description=f"{dp.damage_type}, {dp.severity}", cost=dp.repair_cost)
        total += dp.repair_cost
    dep = deposits[bi]
    dep.withheld = total
    dep.to_return = dep.amount - total
    dep.status = "partially_withheld"
    dep.save()

# задачи по уходу
for i, b in enumerate(bookings):
    prep_status = "done" if b.status in ("issued", "returned") else "pending"
    actual = b.date_start - dt.timedelta(days=1) if prep_status == "done" else None
    CareTask.objects.create(
        booking=b, costume=b.costume, master=sidorov, work_type="steaming",
        planned_date=b.date_start - dt.timedelta(days=1), actual_date=actual,
        status=prep_status, comment="Отпаривание перед выдачей",
    )
    if b.status == "returned":
        CareTask.objects.create(
            booking=b, costume=b.costume, master=sidorov, work_type="washing",
            planned_date=b.actual_return_date + dt.timedelta(days=1),
            actual_date=b.actual_return_date + dt.timedelta(days=1),
            status="done", comment="Стирка после возврата",
        )
CareTask.objects.create(
    booking=bookings[6], costume=bookings[6].costume, master=sidorov,
    work_type="repair", planned_date=D(2026, 11, 2), actual_date=None,
    status="in_progress", comment="Замена молнии",
)

# слоты примерки
slots = [
    FittingSlot.objects.create(slot_datetime=dt.datetime(2026, 11, 20, 14, 0), consultant=petrova, client=ivanov, status="booked"),
    FittingSlot.objects.create(slot_datetime=dt.datetime(2026, 11, 20, 15, 0), consultant=petrova, client=smirnova, status="booked"),
    FittingSlot.objects.create(slot_datetime=dt.datetime(2026, 11, 21, 14, 0), consultant=petrova, status="free"),
    FittingSlot.objects.create(slot_datetime=dt.datetime(2026, 11, 21, 15, 0), consultant=petrova, status="free"),
    FittingSlot.objects.create(slot_datetime=dt.datetime(2026, 11, 22, 14, 0), consultant=petrova, status="free"),
    FittingSlot.objects.create(slot_datetime=dt.datetime(2026, 11, 22, 15, 0), consultant=petrova, status="free"),
]
for si, ci in [(0, 0), (0, 1), (0, 2), (1, 30), (1, 31), (2, 12), (2, 13), (3, 4), (4, 24), (5, 25)]:
    FittingCostume.objects.create(slot=slots[si], costume=costumes[ci])

print("Костюмов:", Costume.objects.count())
print("Броней:", Booking.objects.count())
print("Залогов:", Deposit.objects.count())
print("Актов:", Inspection.objects.count())
print("Повреждений:", Damage.objects.count())
print("Задач по уходу:", CareTask.objects.count())
print("Слотов примерки:", FittingSlot.objects.count())