from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Category, Product, Order, OrderItem
from .forms import RegistrationForm, LoginForm, OrderCreateForm
import logging

logger = logging.getLogger(__name__)


def register(request):
    """Регистрация нового пользователя"""
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация успешно завершена!')
            return redirect('shop:product_list')
    else:
        form = RegistrationForm()
    return render(request, 'auth/register.html', {'form': form})


def user_login(request):
    """Вход пользователя"""
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'Вход успешно выполнен!')
                return redirect('shop:product_list')
            else:
                messages.error(request, 'Неверное имя пользователя или пароль')
    else:
        form = LoginForm()
    return render(request, 'auth/login.html', {'form': form})


def user_logout(request):
    """Выход пользователя"""
    logout(request)
    messages.success(request, 'Выход успешно выполнен!')
    return redirect('shop:product_list')


def product_list(request, category_slug=None):
    """Список товаров с возможной фильтрацией по категориям"""
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)

    cart = request.session.get('cart', {})
    cart_count = sum(cart.values())

    return render(request, 'shop/product_list.html', {
        'category': category,
        'categories': categories,
        'products': products,
        'cart_count': cart_count
    })


def product_detail(request, id, slug):
    """Страница отдельного товара"""
    product = get_object_or_404(Product, id=id, slug=slug, available=True)
    cart = request.session.get('cart', {})
    in_cart = str(product.id) in cart

    # Добавляем количество товара в корзине для отображения
    cart_quantity = cart.get(str(product.id), 0)

    return render(request, 'shop/product_detail.html', {
        'product': product,
        'in_cart': in_cart,
        'cart_quantity': cart_quantity
    })


def cart_add(request, product_id):
    """Добавление товара в корзину"""
    product = get_object_or_404(Product, id=product_id)
    cart = request.session.get('cart', {})

    product_id_str = str(product_id)

    if product_id_str in cart:
        cart[product_id_str] += 1
    else:
        cart[product_id_str] = 1

    request.session['cart'] = cart
    request.session.modified = True
    messages.success(request, f'Товар "{product.name}" добавлен в корзину')
    return redirect(request.META.get('HTTP_REFERER', 'shop:product_list'))


def cart_remove(request, product_id):
    """Удаление товара из корзины"""
    product = get_object_or_404(Product, id=product_id)
    cart = request.session.get('cart', {})
    product_id_str = str(product_id)

    if product_id_str in cart:
        del cart[product_id_str]
        request.session['cart'] = cart
        request.session.modified = True
        messages.success(request, f'Товар "{product.name}" удален из корзины')

    return redirect('shop:cart_detail')


def cart_update(request, product_id):
    """Обновление количества товара в корзине"""
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        cart = request.session.get('cart', {})
        product_id_str = str(product_id)

        quantity = int(request.POST.get('quantity', 1))
        if quantity > 0:
            cart[product_id_str] = quantity
        else:
            if product_id_str in cart:
                del cart[product_id_str]

        request.session['cart'] = cart
        request.session.modified = True
        messages.success(request, 'Корзина обновлена')

    return redirect('shop:cart_detail')


def cart_detail(request):
    """Просмотр корзины"""
    cart = request.session.get('cart', {})
    cart_items = []
    total_price = 0

    for product_id_str, quantity in cart.items():
        try:
            product = get_object_or_404(Product, id=int(product_id_str))
            item_price = product.price * quantity
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'price': item_price,
                'id': product.id  # Добавляем ID продукта для ссылок
            })
            total_price += item_price
        except (ValueError, Product.DoesNotExist):
            # Если товар не найден, удаляем его из корзины
            del cart[product_id_str]
            request.session['cart'] = cart
            request.session.modified = True

    cart_count = sum(cart.values())

    return render(request, 'shop/cart_detail.html', {
        'cart_items': cart_items,
        'total_price': total_price,
        'cart_count': cart_count
    })


@login_required
def order_create(request):
    """Создание заказа из корзины"""
    cart = request.session.get('cart', {})

    if not cart:
        messages.warning(request, 'Ваша корзина пуста')
        return redirect('shop:product_list')

    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            try:
                # Создаем заказ
                order = form.save(commit=False)
                order.user = request.user
                order.save()

                # Добавляем товары из корзины в заказ
                for product_id_str, quantity in cart.items():
                    try:
                        product = get_object_or_404(Product, id=int(product_id_str))
                        OrderItem.objects.create(
                            order=order,
                            product=product,
                            price=product.price,
                            quantity=quantity
                        )
                    except (ValueError, Product.DoesNotExist):
                        continue

                # Очищаем корзину
                request.session['cart'] = {}
                request.session.modified = True

                messages.success(request, f'Ваш заказ №{order.id} успешно создан!')
                return redirect('shop:order_detail', order_id=order.id)

            except Exception as e:
                logger.error(f"Error creating order: {str(e)}")
                messages.error(request, 'Произошла ошибка при создании заказа')
                return redirect('shop:cart_detail')
    else:
        # Предзаполняем адрес, если пользователь уже делал заказы
        last_order = Order.objects.filter(user=request.user).last()
        initial = {
            'shipping_address': last_order.shipping_address if last_order else '',
            'comments': ''
        }
        form = OrderCreateForm(initial=initial)

    # Подготавливаем данные о корзине для отображения
    cart_items = []
    total_price = 0
    for product_id_str, quantity in cart.items():
        try:
            product = get_object_or_404(Product, id=int(product_id_str))
            item_price = product.price * quantity
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'price': item_price
            })
            total_price += item_price
        except (ValueError, Product.DoesNotExist):
            continue

    return render(request, 'shop/order_create.html', {
        'form': form,
        'cart_items': cart_items,
        'total_price': total_price,
        'cart_count': sum(cart.values())
    })


@login_required
def order_list(request):
    """Список заказов пользователя"""
    orders = Order.objects.filter(user=request.user).order_by('-created')
    return render(request, 'shop/order_list.html', {'orders': orders})


@login_required
def order_detail(request, order_id):
    """Детализация заказа"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'shop/order_detail.html', {'order': order})


@login_required
def admin_order_list(request):
    """Список всех заказов для администратора"""
    if not request.user.is_staff:
        messages.error(request, 'У вас нет прав доступа')
        return redirect('shop:product_list')

    orders = Order.objects.all().order_by('-created')
    return render(request, 'admin/order_list.html', {'orders': orders})


@login_required
def admin_order_update(request, order_id):
    """Обновление статуса заказа администратором"""
    if not request.user.is_staff:
        messages.error(request, 'У вас нет прав доступа')
        return redirect('shop:product_list')

    order = get_object_or_404(Order, id=order_id)

    if request.method == 'POST':
        status = request.POST.get('status')
        paid = request.POST.get('paid') == 'on'

        if status in dict(Order.STATUS_CHOICES).keys():
            order.status = status
            order.paid = paid
            order.save()
            messages.success(request, f'Заказ №{order.id} обновлен')
        else:
            messages.error(request, 'Неверный статус заказа')

    return redirect('shop:admin_order_list')