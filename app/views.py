from PIL import Image
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from .models import *


def login_(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.is_superuser:
                messages.info(request, f'У вас есть права администратора, {request.user.fio}')
            elif user.is_staff:
                messages.info(request, f'У вас есть права менеджера, {request.user.fio}')
            else:
                messages.success(request, f'Вы успешно вошли, {request.user.fio}!')
            return redirect('home')
        else:
            messages.error(request, 'Неверный логин или пароль')
            return redirect('login_')
    return render(request, 'login.html')


def logout_(request):
    logout(request)
    messages.success(request, 'Вы успешно вышли!')
    return redirect('login_')


def filter_books(request):
    """
    Фильтрация книг:
    - поиск по названию книги или описанию
    - фильтр по категории
    - сортировка по цене (возрастание/убывание)
    """
    books = Book.objects.all()

    # Параметры из GET-запроса
    search = request.GET.get('search', '')
    filter_category = request.GET.get('filter', '')
    sort = request.GET.get('sort', '')

    # ПОИСК: по названию книги ИЛИ по описанию
    if search:
        books = books.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search)
        )

    # ФИЛЬТР ПО КАТЕГОРИИ
    if filter_category:
        books = books.filter(category__id=filter_category)

    # СОРТИРОВКА ПО ЦЕНЕ
    if sort == 'price_asc':
        books = books.order_by('price')
    elif sort == 'price_desc':
        books = books.order_by('-price')

    context = {
        'books': books,
        'categories': Category.objects.all(),           # для выпадающего списка категорий
        'search': search,
        'filter': filter_category,
        'sort': sort,
        'bookorders': BookOrder.objects.all(),          # для страницы заказов
        'suppliers': Supplier.objects.all(),
        'manufacturers': Manufacturer.objects.all(),
        'statuses': Status.objects.all(),
        'pvz_list': Pvz.objects.all(),
    }
    return context


def home(request):
    """Главная страница со списком книг и фильтрацией"""
    context = filter_books(request)
    return render(request, 'home.html', context)


def order(request):
    """Страница со списком заказов"""
    context = filter_books(request)
    return render(request, 'order.html', context)


def add_book(request):
    """Добавление новой книги (только для админа)"""
    if request.method == 'POST':
        # Обработка изображения
        image = request.FILES.get('image')
        if image:
            img = Image.open(image)
            if img.width > 600 or img.height > 600:
                messages.error(request, 'Изображение больше чем 600x600 пикселей!')
                return redirect('home')

        # Получаем или создаем поставщика
        supplier_name = request.POST.get('supplier', '')
        supplier, created = Supplier.objects.get_or_create(name=supplier_name)

        # Получаем изготовителя и категорию по ID
        manufacturer = Manufacturer.objects.get(id=request.POST.get('manufacturer'))
        category = Category.objects.get(id=request.POST.get('category'))

        # Создаем книгу
        Book.objects.create(
            article=request.POST.get('article'),
            name=request.POST.get('name'),
            unit=request.POST.get('unit'),
            price=request.POST.get('price'),
            category=category,
            supplier=supplier,
            manufacturer=manufacturer,
            discount=request.POST.get('discount'),
            description=request.POST.get('description'),
            unit_on_stock=request.POST.get('unit_on_stock'),
            image=image,
        )
        messages.success(request, 'Книга успешно добавлена!')
    return redirect('home')


def edit_book(request, id):
    """Редактирование книги"""
    if request.method == 'POST':
        book = Book.objects.get(id=id)

        # Обработка изображения
        image = request.FILES.get('image')
        if image:
            with Image.open(image) as img:
                if img.width > 600 or img.height > 600:
                    messages.error(request, 'Изображение больше чем 600x600 пикселей!')
                    return redirect('home')
            if book.image:
                book.image.delete()
            book.image = image

        # Получаем или создаем поставщика
        supplier_name = request.POST.get('supplier', '')
        supplier, created = Supplier.objects.get_or_create(name=supplier_name)

        # Получаем изготовителя и категорию по ID
        manufacturer = Manufacturer.objects.get(id=request.POST.get('manufacturer'))
        category = Category.objects.get(id=request.POST.get('category'))

        # Обновляем поля
        book.article = request.POST.get('article')
        book.name = request.POST.get('name')
        book.unit = request.POST.get('unit')
        book.price = request.POST.get('price')
        book.category = category
        book.supplier = supplier
        book.manufacturer = manufacturer
        book.discount = request.POST.get('discount')
        book.description = request.POST.get('description')
        book.unit_on_stock = request.POST.get('unit_on_stock')
        book.save()

        messages.success(request, 'Книга успешно обновлена!')
    return redirect('home')

def book_detail(request, id):
    """Детальная страница книги"""
    book = get_object_or_404(Book, id=id)
    context = {
        'book': book,
        'categories': Category.objects.all(),
        'manufacturers': Manufacturer.objects.all(),
    }
    return render(request, 'detail.html', context)

def delete_book(request, id):
    """Удаление книги (только если нет связанных заказов)"""
    book = Book.objects.get(id=id)

    # Проверяем, есть ли книга в заказах
    if BookOrder.objects.filter(book=book):
        messages.error(request, 'Книга находится в заказе! Удаление невозможно.')
    else:
        if book.image:
            book.image.delete()
        book.delete()
        messages.success(request, 'Книга успешно удалена!')
    return redirect('home')


def add_order(request):
    """Добавление нового заказа"""
    if request.method == 'POST':
        book_id = request.POST.get('book')
        status_id = request.POST.get('status')
        pvz_id = request.POST.get('pvz')
        amount = request.POST.get('amount')

        # Создаем заказ
        order = Order.objects.create(
            date_order=request.POST.get('date_order'),
            date_delivery=request.POST.get('date_delivery'),
            pvz=Pvz.objects.get(id=pvz_id),
            client=request.user,  # текущий пользователь — клиент
            status=Status.objects.get(id=status_id),
            code=request.POST.get('code'),
        )

        # Связываем книгу с заказом
        BookOrder.objects.create(
            book=Book.objects.get(id=book_id),
            order=order,
            amount=amount,
        )
        messages.success(request, 'Заказ успешно добавлен!')
    return redirect('order')


def edit_order(request, id):
    """Редактирование заказа (через BookOrder)"""
    if request.method == 'POST':
        book_order = BookOrder.objects.get(id=id)
        order = book_order.order

        # Обновляем заказ
        order.date_order = request.POST.get('date_order')
        order.date_delivery = request.POST.get('date_delivery')
        order.pvz = Pvz.objects.get(id=request.POST.get('pvz'))
        order.status = Status.objects.get(id=request.POST.get('status'))
        order.code = request.POST.get('code')
        order.save()

        # Обновляем книгу в заказе
        book_order.book = Book.objects.get(id=request.POST.get('book'))
        book_order.amount = request.POST.get('amount')
        book_order.save()

        messages.success(request, 'Заказ успешно обновлен!')
    return redirect('order')


def delete_order(request, id):
    """Удаление заказа"""
    order = Order.objects.get(id=id)
    order.delete()
    messages.success(request, 'Заказ успешно удален!')
    return redirect('order')