import os
import django
from datetime import date, timedelta
from decimal import Decimal
import random

# Настройка окружения Django (поменяй 'project.settings' на имя своего проекта)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from app.models import (
    CustomUser, Category, Status, Pvz, Supplier,
    Manufacturer, Book, Order, BookOrder
)


def fill_database():
    print("=" * 50)
    print("Заполняю базу данных...")
    print("=" * 50)

    # ==================================================
    # 1. КАТЕГОРИИ (Category)
    # ==================================================
    categories_data = [
        "Роман", "Детектив", "Фантастика", "Научная литература",
        "Поэзия", "Биография", "История", "Философия", "Ужасы", "Приключения"
    ]
    for cat_name in categories_data:
        Category.objects.get_or_create(name=cat_name)
    print(f"✅ Категории: {Category.objects.count()}")

    # ==================================================
    # 2. СТАТУСЫ (Status)
    # ==================================================
    statuses_data = ["Новый", "В обработке", "Оплачен", "Отправлен", "Доставлен", "Отменен"]
    for status_name in statuses_data:
        Status.objects.get_or_create(name=status_name)
    print(f"✅ Статусы: {Status.objects.count()}")

    # ==================================================
    # 3. ПВЗ (Pvz)
    # ==================================================
    pvz_data = [
        "г. Москва, ул. Тверская, д. 1",
        "г. Санкт-Петербург, Невский пр-т, д. 25",
        "г. Новосибирск, ул. Ленина, д. 10",
        "г. Екатеринбург, ул. Малышева, д. 5",
        "г. Казань, ул. Баумана, д. 15",
        "г. Нижний Новгород, ул. Большая Покровская, д. 8",
    ]
    for address in pvz_data:
        Pvz.objects.get_or_create(address=address)
    print(f"✅ ПВЗ: {Pvz.objects.count()}")

    # ==================================================
    # 4. ПОСТАВЩИКИ (Supplier)
    # ==================================================
    suppliers_data = [
        "ООО КнижныйМир",
        "ИП Иванов",
        "ООО МегаКнига",
        "ЗАО Литера",
        "ООО Букинист",
    ]
    for supplier_name in suppliers_data:
        Supplier.objects.get_or_create(name=supplier_name)
    print(f"✅ Поставщики: {Supplier.objects.count()}")

    # ==================================================
    # 5. ИЗГОТОВИТЕЛИ (Manufacturer)
    # ==================================================
    manufacturers_data = [
        "Эксмо",
        "АСТ",
        "Питер",
        "Манн, Иванов и Фербер",
        "Азбука-Аттикус",
        "Альпина Паблишер",
    ]
    for manufacturer_name in manufacturers_data:
        Manufacturer.objects.get_or_create(name=manufacturer_name)
    print(f"✅ Изготовители: {Manufacturer.objects.count()}")

    # ==================================================
    # 6. ПОЛЬЗОВАТЕЛИ (CustomUser)
    # ==================================================
    users_data = [
        {"username": "ivanov", "fio": "Иван Иванов", "password": "123456", "is_staff": False},
        {"username": "petrov", "fio": "Петр Петров", "password": "123456", "is_staff": False},
        {"username": "sidorov", "fio": "Сидор Сидоров", "password": "123456", "is_staff": False},
        {"username": "kuznetsov", "fio": "Алексей Кузнецов", "password": "123456", "is_staff": False},
        {"username": "smirnova", "fio": "Мария Смирнова", "password": "123456", "is_staff": False},
        {"username": "manager", "fio": "Анна Менеджер", "password": "123456", "is_staff": True},
        {"username": "admin", "fio": "Админ Админов", "password": "admin123", "is_staff": True, "is_superuser": True},
    ]

    users = []
    for user_data in users_data:
        user, created = CustomUser.objects.get_or_create(
            username=user_data["username"],
            defaults={
                "fio": user_data["fio"],
                "is_staff": user_data.get("is_staff", False),
                "is_superuser": user_data.get("is_superuser", False),
            }
        )
        if created:
            user.set_password(user_data["password"])
            user.save()
        users.append(user)
    print(f"✅ Пользователи: {CustomUser.objects.count()}")

    # ==================================================
    # 7. КНИГИ (Book)
    # ==================================================
    # Получаем все нужные объекты для связей
    category_romantic = Category.objects.get(name="Роман")
    category_detective = Category.objects.get(name="Детектив")
    category_fantasy = Category.objects.get(name="Фантастика")
    category_poetry = Category.objects.get(name="Поэзия")
    category_horror = Category.objects.get(name="Ужасы")
    category_history = Category.objects.get(name="История")
    category_biography = Category.objects.get(name="Биография")

    supplier_knizhny = Supplier.objects.get(name="ООО КнижныйМир")
    supplier_ivanov = Supplier.objects.get(name="ИП Иванов")
    supplier_mega = Supplier.objects.get(name="ООО МегаКнига")
    supplier_litera = Supplier.objects.get(name="ЗАО Литера")

    manufacturer_eksmo = Manufacturer.objects.get(name="Эксмо")
    manufacturer_ast = Manufacturer.objects.get(name="АСТ")
    manufacturer_piter = Manufacturer.objects.get(name="Питер")
    manufacturer_mif = Manufacturer.objects.get(name="Манн, Иванов и Фербер")
    manufacturer_azbuka = Manufacturer.objects.get(name="Азбука-Аттикус")

    books_data = [
        # article, name, unit, price, category, supplier, manufacturer, discount, description, stock
        ("BK001", "Преступление и наказание", "шт", 450, category_romantic, supplier_knizhny, manufacturer_eksmo, 10, "Классический роман о преступлении и раскаянии", 25),
        ("BK002", "Война и мир", "шт", 890, category_romantic, supplier_knizhny, manufacturer_ast, 15, "Эпопея о наполеоновских войнах", 12),
        ("BK003", "Человек в футляре", "шт", 230, category_history, supplier_ivanov, manufacturer_ast, 0, "Рассказ о замкнутом человеке", 45),
        ("BK004", "Мастер и Маргарита", "шт", 670, category_romantic, supplier_mega, manufacturer_eksmo, 20, "Мистический роман о дьяволе в Москве", 8),
        ("BK005", "Евгений Онегин", "шт", 340, category_poetry, supplier_litera, manufacturer_azbuka, 5, "Роман в стихах", 30),
        ("BK006", "Мёртвые души", "шт", 420, category_romantic, supplier_knizhny, manufacturer_ast, 0, "Поэма о покупке мёртвых крестьян", 18),
        ("BK007", "Сияние", "шт", 560, category_horror, supplier_mega, manufacturer_eksmo, 12, "Отель с привидениями", 7),
        ("BK008", "1984", "шт", 520, category_fantasy, supplier_litera, manufacturer_azbuka, 10, "Антиутопия о тоталитаризме", 15),
        ("BK009", "Три товарища", "шт", 600, category_romantic, supplier_knizhny, manufacturer_piter, 8, "Роман о дружбе и любви", 10),
        ("BK010", "Идиот", "шт", 480, category_romantic, supplier_ivanov, manufacturer_eksmo, 12, "Роман о князе Мышкине", 20),
        ("BK011", "Анна Каренина", "шт", 750, category_romantic, supplier_knizhny, manufacturer_ast, 18, "Трагическая история любви", 9),
        ("BK012", "Собачье сердце", "шт", 290, category_fantasy, supplier_mega, manufacturer_ast, 0, "Повесть об эксперименте", 35),
        ("BK013", "Мцыри", "шт", 180, category_poetry, supplier_litera, manufacturer_azbuka, 0, "Поэма о свободном юноше", 50),
        ("BK014", "Двенадцать стульев", "шт", 380, category_romantic, supplier_knizhny, manufacturer_piter, 5, "Сатирический роман", 22),
    ]

    books = []
    for data in books_data:
        (article, name, unit, price, category, supplier,
         manufacturer, discount, description, stock) = data

        book, created = Book.objects.get_or_create(
            article=article,
            defaults={
                "name": name,
                "unit": unit,
                "price": Decimal(price),
                "category": category,
                "supplier": supplier,
                "manufacturer": manufacturer,
                "discount": Decimal(discount),
                "description": description,
                "unit_on_stock": Decimal(stock),
                "image": "books/default.jpg",  # путь к картинке
            }
        )
        books.append(book)
    print(f"✅ Книги: {Book.objects.count()}")

    # ==================================================
    # 8. ЗАКАЗЫ (Order) и BookOrder
    # ==================================================
    all_statuses = list(Status.objects.all())
    all_pvz = list(Pvz.objects.all())

    start_date = date(2024, 1, 1)
    end_date = date(2024, 12, 31)
    delta_days = (end_date - start_date).days

    orders_created = 0
    book_orders_created = 0

    for i in range(35):  # 35 заказов
        random_days = random.randint(0, delta_days)
        order_date = start_date + timedelta(days=random_days)
        delivery_date = order_date + timedelta(days=random.randint(3, 14))

        client = random.choice(users)
        status = random.choice(all_statuses)
        pvz = random.choice(all_pvz)
        code = 10000 + i

        order, created = Order.objects.get_or_create(
            code=code,
            defaults={
                "date_order": order_date,
                "date_delivery": delivery_date,
                "pvz": pvz,
                "client": client,
                "status": status,
            }
        )
        if created:
            orders_created += 1

        # В каждый заказ добавляем от 1 до 5 книг
        num_books = random.randint(1, 5)
        selected_books = random.sample(books, min(num_books, len(books)))

        for book in selected_books:
            amount = random.randint(1, 3)
            book_order, created = BookOrder.objects.get_or_create(
                book=book,
                order=order,
                defaults={"amount": amount}
            )
            if created:
                book_orders_created += 1

    print(f"✅ Заказов создано: {Order.objects.count()}")
    print(f"✅ Связей BookOrder создано: {BookOrder.objects.count()}")

    # ==================================================
    # ИТОГОВАЯ СТАТИСТИКА
    # ==================================================
    print("\n" + "=" * 50)
    print("🎉 БАЗА ДАННЫХ УСПЕШНО ЗАПОЛНЕНА!")
    print("=" * 50)
    print(f"\n📊 Статистика:")
    print(f"   Категорий:      {Category.objects.count()}")
    print(f"   Статусов:       {Status.objects.count()}")
    print(f"   ПВЗ:            {Pvz.objects.count()}")
    print(f"   Поставщиков:    {Supplier.objects.count()}")
    print(f"   Изготовителей:  {Manufacturer.objects.count()}")
    print(f"   Пользователей:  {CustomUser.objects.count()}")
    print(f"   Книг:           {Book.objects.count()}")
    print(f"   Заказов:        {Order.objects.count()}")
    print(f"   BookOrder:      {BookOrder.objects.count()}")

    # Пример для проверки
    print("\n📖 Примеры книг:")
    for book in Book.objects.all()[:5]:
        price_with_discount = book.calculate_discount()
        if price_with_discount:
            print(f"   - {book.article}: {book.name} — {book.price} ₽ (со скидкой: {price_with_discount:.2f} ₽)")
        else:
            print(f"   - {book.article}: {book.name} — {book.price} ₽")


if __name__ == "__main__":
    fill_database()