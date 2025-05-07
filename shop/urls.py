from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    # Аутентификация
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),

    # Каталог товаров
    path('', views.product_list, name='product_list'),
    path('category/<slug:category_slug>/', views.product_list, name='product_list_by_category'),
    path('product/<int:id>/<slug:slug>/', views.product_detail, name='product_detail'),

    # Корзина
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/remove/<int:product_id>/', views.cart_remove, name='cart_remove'),
    path('cart/update/<int:product_id>/', views.cart_update, name='cart_update'),

    # Заказы
    path('order/create/', views.order_create, name='order_create'),
    path('order/list/', views.order_list, name='order_list'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),

    # Админ-панель
    path('admin/orders/', views.admin_order_list, name='admin_order_list'),
    path('admin/order/<int:order_id>/update/', views.admin_order_update, name='admin_order_update'),
]