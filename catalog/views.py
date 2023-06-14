from django.shortcuts import render, redirect
from . import models
from . import handlers
from django.http import HttpResponse


# Create your views here.

def main_page(request):
    # получаем все данные о категориях из базы
    all_categories = models.Category.objects.all()
    all_products = models.Product.objects.all()

    # получить переменную из фронт части, если есть
    search_value_from_front = request.GET.get('search')
    if search_value_from_front:
        all_products = models.Product.objects.filter(name__contains=search_value_from_front)

    # передача переменных из бэка на фронт
    context = {'all_categories': all_categories, 'all_products': all_products}

    # обработка из html файла
    return render(request, 'index.html', context)


def about_page(request):
    # обработка из html файла
    return render(request, 'about.html')


def settings_page(request):
    return HttpResponse('Page settings')


#  Получить продукты из конкретной категории
def get_category_products(request, pk):
    #  Получить все товары из конкретной категории
    exact_category_products = models.Product.objects.filter(category_name__id=pk)
    #  Передача переменных из бэка на фронт
    context = {'category_products': exact_category_products}

    #  Указать html
    return render(request, 'category.html', context)


#  Функция получения определенного продукта
def get_exact_product(request, name, pk):
    #  Находим из базы продукт
    exact_product = models.Product.objects.get(name=name, id=pk)

    #  Передача переменных из бэка на фронт
    context = {'product': exact_product}

    #  Вывод html
    return render(request, 'product.html', context)


#  Функция добавления продукта в корзину
def add_pr_to_cart(request, pk):
    #  Получить выбранное количество продукта из front части
    quantity = request.POST.get('pr_count')

    #  Находим сам продукт
    product_to_add = models.Product.objects.get(id=pk)

    #  Добавление данных
    models.UserCart.objects.create(user_id=request.user.id,
                                   user_product=product_to_add,
                                   user_product_quantity=quantity)

    return redirect('/')


#  Получить корзину пользователя
def user_cart(request):
    products_from_cart = models.UserCart.objects.filter(user_id=request.user.id)

    context = {'cart_products': products_from_cart}

    return render(request, 'user_cart.html', context)


#  Оформление заказа
def complete_order(request):
    #  Получаем корзину пользователя
    user_cart = models.UserCart.objects.filter(user_id=request.user.id)
    #  Собираем сообщение бота для админа
    if request.method == 'POST':
        result_message = 'Новый заказ(Из сайта)\n\n'
        total = 0
        for cart in user_cart:
            result_message += f'Название товара: {cart.user_product}\n' \
                              f'Количество: {cart.user_product_quantity}'
            total += cart.user_product.product_price * cart.user_product_quantity

        result_message += f'\n\nИтог {total}'

        handlers.bot.send_message(5231311910, result_message)
        user_cart.delete()
        return redirect('/')

    return render(request, 'user_cart.html', {'user': user_cart})


def delete_from_user_cart(request, pk):
    product_to_delete = models.Product.objects.get(id=pk)
    models.UserCart.objects.filter(user_id=request.user.id, user_product=product_to_delete).delete()

    return redirect('/cart')
