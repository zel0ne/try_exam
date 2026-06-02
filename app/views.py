from PIL import Image
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q
from django.shortcuts import render, redirect
from .models import *


# ============================================================
# АВТОРИЗАЦИЯ
# ============================================================

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


# ============================================================
# ВСПОМОГАТЕЛЬНАЯ ФУНКЦИЯ ФИЛЬТРАЦИИ (как в твоем коде)
# ============================================================

def filter_books(request):
    """
    Фильтрация книг:
    - поиск по названию книги или автору (ФИО)
    - фильтр по жанру
    - сортировка по цене (возрастание/убывание)
    """
    books = Book.objects.all()

    # Параметры из GET-запроса
    search = request.GET.get('search', '')
    filter_genre = request.GET.get('filter', '')
    sort = request.GET.get('sort', '')

    # ПОИСК: по названию книги ИЛИ по ФИО автора
    if search:
        books = books.filter(
            Q(name__icontains=search) |
            Q(author__fio__icontains=search)
        )

    # ФИЛЬТР ПО ЖАНРУ
    if filter_genre:
        books = books.filter(genre__id=filter_genre)

    # СОРТИРОВКА ПО ЦЕНЕ
    if sort == 'price_asc':
        books = books.order_by('price')
    elif sort == 'price_desc':
        books = books.order_by('-price')

    context = {
        'books': books,
        'genres': Genre.objects.all(),           # для выпадающего списка жанров
        'search': search,
        'filter': filter_genre,
        'sort': sort,
        'bookorders': BookOrder.objects.all(),   # для страницы заказов
        'authors': Author.objects.all(),
        'statuses': Status.objects.all(),
    }
    return context


# ============================================================
# ГЛАВНАЯ (СПИСОК КНИГ)
# ============================================================

def home(request):
    """Главная страница со списком книг и фильтрацией"""
    context = filter_books(request)
    return render(request, 'home.html', context)


# ============================================================
# ЗАКАЗЫ
# ============================================================

def order(request):
    """Страница со списком заказов"""
    context = filter_books(request)
    return render(request, 'order.html', context)


# ============================================================
# ДОБАВЛЕНИЕ КНИГИ
# ============================================================

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

        # Получаем или создаем автора (как в твоем коде с Producer)
        author_name = request.POST.get('author', '')
        author, created = Author.objects.get_or_create(fio=author_name)

        # Получаем жанр по ID
        genre = Genre.objects.get(id=request.POST.get('genre'))

        # Создаем книгу
        Book.objects.create(
            article=request.POST.get('article'),
            name=request.POST.get('name'),
            genre=genre,
            author=author,
            price=request.POST.get('price'),
            discount=request.POST.get('discount'),
            description=request.POST.get('description'),
            unit_on_stock=request.POST.get('unit_on_stock'),
            image=image,
        )
        messages.success(request, 'Книга успешно добавлена!')
    return redirect('home')


# ============================================================
# РЕДАКТИРОВАНИЕ КНИГИ
# ============================================================

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

        # Получаем или создаем автора
        author_name = request.POST.get('author', '')
        author, created = Author.objects.get_or_create(fio=author_name)

        # Обновляем поля
        book.article = request.POST.get('article')
        book.name = request.POST.get('name')
        book.genre = Genre.objects.get(id=request.POST.get('genre'))
        book.author = author
        book.price = request.POST.get('price')
        book.discount = request.POST.get('discount')
        book.description = request.POST.get('description')
        book.unit_on_stock = request.POST.get('unit_on_stock')
        book.save()

        messages.success(request, 'Книга успешно обновлена!')
    return redirect('home')


# ============================================================
# УДАЛЕНИЕ КНИГИ
# ============================================================

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


# ============================================================
# ДОБАВЛЕНИЕ ЗАКАЗА
# ============================================================

def add_order(request):
    """Добавление нового заказа"""
    if request.method == 'POST':
        book_id = request.POST.get('book')
        status_id = request.POST.get('status')
        amount = request.POST.get('amount')

        # Создаем заказ
        order = Order.objects.create(
            date_order=request.POST.get('date_order'),
            date_delivery=request.POST.get('date_delivery'),
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


# ============================================================
# РЕДАКТИРОВАНИЕ ЗАКАЗА
# ============================================================

def edit_order(request, id):
    """Редактирование заказа (через BookOrder)"""
    if request.method == 'POST':
        book_order = BookOrder.objects.get(id=id)
        order = book_order.order

        # Обновляем заказ
        order.date_order = request.POST.get('date_order')
        order.date_delivery = request.POST.get('date_delivery')
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