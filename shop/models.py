from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class Category(models.Model):
    """Модель для категорий товаров"""
    name = models.CharField('Название категории', max_length=100)
    slug = models.SlugField('URL', max_length=100, unique=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        """Получить абсолютный URL категории"""
        return reverse('shop:product_list_by_category', args=[self.slug])


class Product(models.Model):
    """Модель для товаров"""
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', verbose_name='Категория')
    name = models.CharField('Название товара', max_length=200)
    slug = models.SlugField('URL', max_length=200, unique=True)
    image = models.ImageField('Изображение', upload_to='products/%Y/%m/%d')
    description = models.TextField('Описание', blank=True)
    price = models.DecimalField('Цена', max_digits=10, decimal_places=2)
    available = models.BooleanField('Доступен', default=True)
    created = models.DateTimeField('Дата создания', auto_now_add=True)
    updated = models.DateTimeField('Дата обновления', auto_now=True)

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ('name',)
        indexes = [
            models.Index(fields=['id', 'slug']),
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        """Получить абсолютный URL товара"""
        return reverse('shop:product_detail', args=[self.id, self.slug])


class Order(models.Model):
    """Модель для заказов"""
    STATUS_CHOICES = (
        ('new', 'Новый'),
        ('completed', 'Завершен'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', verbose_name='Пользователь')
    full_name = models.CharField('ФИО', max_length=100)
    email = models.EmailField('Email')
    address = models.CharField('Адрес', max_length=250)
    city = models.CharField('Город', max_length=100)
    postal_code = models.CharField('Почтовый индекс', max_length=20)
    created = models.DateTimeField('Дата создания', auto_now_add=True)
    updated = models.DateTimeField('Дата обновления', auto_now=True)
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default='new')

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ('-created',)

    def __str__(self):
        return f'Заказ {self.id}'

    def get_total_cost(self):
        """Получить общую стоимость заказа"""
        return sum(item.get_cost() for item in self.items.all())


class OrderItem(models.Model):
    """Модель для товаров в заказе"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name='Заказ')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='order_items', verbose_name='Товар')
    price = models.DecimalField('Цена', max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField('Количество', default=1)

    class Meta:
        verbose_name = 'Товар в заказе'
        verbose_name_plural = 'Товары в заказе'

    def __str__(self):
        return f'{self.product.name} - {self.quantity} шт.'

    def get_cost(self):
        """Получить стоимость товара в заказе"""
        return self.price * self.quantity