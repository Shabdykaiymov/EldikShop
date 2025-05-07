import os
import sys
import django
from django.contrib.auth.models import User
from django.core.files.images import ImageFile

# Настраиваем Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eldikshop_project.settings')
django.setup()

# Импортируем модели
from shop.models import Category, Product


def create_superuser():
    """Создание суперпользователя, если его нет"""
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123'
        )
        print('Суперпользователь успешно создан')
    else:
        print('Суперпользователь уже существует')


def create_sample_images():
    """Создание примеров изображений для товаров"""
    # Создаем директорию для изображений, если ее нет
    os.makedirs('media/products', exist_ok=True)

    # Список файлов для создания
    image_files = [
        'smartphone.jpg', 'laptop.jpg', 'jeans.jpg', 'tshirt.jpg',
        'book1.jpg', 'book2.jpg', 'dinnerware.jpg', 'bed-linen.jpg'
    ]

    # Создаем пустые изображения для примера (в реальном проекте здесь будут настоящие изображения)
    for filename in image_files:
        image_path = os.path.join('media/products', filename)
        if not os.path.exists(image_path):
            # Создаем пустой файл
            with open(image_path, 'wb') as f:
                f.write(
                    b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82')
            print(f'Создано изображение: {filename}')


def main():
    """Главная функция для настройки проекта"""
    create_superuser()
    create_sample_images()
    print('Настройка проекта завершена!')


if __name__ == '__main__':
    main()