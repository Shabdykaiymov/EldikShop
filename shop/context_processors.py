def cart(request):
    """
    Процессор контекста для корзины.
    Добавляет словарь 'cart' в контекст шаблона, позволяя получить доступ к корзине из любого шаблона.
    """
    cart = request.session.get('cart', {})

    # Получаем количество товаров в корзине
    cart_count = sum(cart.values())

    return {
        'cart_count': cart_count,
    }