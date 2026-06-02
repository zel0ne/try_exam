from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    fio = models.CharField()

class Category(models.Model):
    name = models.CharField(max_length=50)

class Status(models.Model):
    name = models.CharField(max_length=50)

class Pvz(models.Model):
    address = models.CharField(max_length=100)

class Supplier(models.Model):
    name = models.CharField(max_length=100)

class Manufacturer(models.Model):
    name = models.CharField(max_length=100)

class Book(models.Model):
    article = models.CharField(max_length=6)
    name = models.CharField(max_length=50)
    unit = models.CharField(max_length=10)
    price = models.DecimalField(decimal_places=2, max_digits = 10)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.CASCADE)
    discount = models.DecimalField(decimal_places=2, max_digits = 10)
    description = models.CharField(max_length=100)
    unit_on_stock = models.DecimalField(decimal_places=2, max_digits = 10)
    image = models.ImageField(upload_to='books/', null=True, blank=True)

    def calculate_discount(self):
        if self.discount > 0:
            return self.price * (100 - self.discount) / 100
        return None

class Order(models.Model):
    date_order = models.DateField()
    date_delivery = models.DateField()
    pvz = models.ForeignKey(Pvz, on_delete=models.CASCADE, default='')
    client = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    status = models.ForeignKey(Status, on_delete=models.CASCADE)
    code = models.IntegerField()

class BookOrder(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    amount = models.IntegerField()


