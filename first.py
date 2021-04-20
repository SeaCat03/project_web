pay = 0
dishes = {
    'Кофе': 150,
    'Чай': 100,
    'Печенье имбирное': 70,
    'Мороженое': 180,
    'Штрудель': 170
}

while True:
    to_do = input("Введите команду: ")
    if to_do == 'Заказать':
        name = input("Что будете брать?:")
        if name not in dishes.keys():
            print('Такого товара нет')
        pay += dishes[name]
    elif to_do == 'Оплатить':
        if pay == 0:
            print('Покупок нет')
            break
        print(f"Итого к оплате {pay}")
        break
    else:
        print("Неизвестная команда")

