from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import datetime
from json import dumps, loads
import requests
from time import sleep, time, strftime, localtime
from config import q_code, group_token, group_id

import db.models.offers as Offers
import db.models.users as Users
import db.models.orders as Orders



# функция добавляет пользователя
def add_user_to_user_table(db, table, name, phone):
    user_str = table(name=name, phone=phone)
    db.session.add(user_str)
    db.session.commit()


# функция добовляет почту пользователя
def add_email_to_user_table(db, table, name, phone, email):
    db.session.query(table).filter_by(name=name, phone=phone).update({'email': email})
    db.session.commit()


# функция возвращает иныормацию о товаре
def get_info_about_offer(db, table, offer_id):
    offer = db.session.query(table).filter_by(offer_id=offer_id).scalar()
    if offer != None:
        answer_json = {
            'call': offer.call,
            'actually_cost': offer.actually_cost,
            'always_cost': offer.always_cost,
            'about': offer.about,
            'can_be': offer.can_be,
            'picture': list(map(lambda x: '/' + x, offer.picture.split('?')))
        }
        return answer_json


# надо-ли сразу ставить статус 'в пути', вдруг человек ещё не оплатил
def add_order_from_user(db, table_ord, table_us, who_add, what_add):
    date_to_save = datetime.date.today()
    str_to_save = table_ord(who_id=who_add, order_status='в пути',
                            when=date_to_save, what_offer=what_add)
    db.session.add(str_to_save)
    db.session.commit()
    order_id_to_later = db.session.query(table_ord.order_id).filter_by(
        who_id=who_add, when=date_to_save,
        what_offer=what_add).scalar()
    if order_id_to_later != None:
        what_user_has = db.session.query(table_us.orders).filter_by(
            person_id=who_add).scalar()
        if what_user_has != None:
            add_what = f"{what_user_has},{order_id_to_later}"
            db.session.query(table_us).filter_by(person_id=who_add).update({'orders': add_what})
            db.session.commit()


# функция добавляет товар в избранное пользователя
def add_offer_to_person_favorites(db, table, who_id, what_id):
    what_user_has = db.session.query(table.favorites).filter_by(
        person_id=who_id).scalar()
    if what_user_has != None:
        add_what = f"{what_user_has},{what_id}"
        db.session.query(table).filter_by(user_id=who_id).update({'favorites': add_what})
        db.session.commit()


# функция меняет статус заказа
def change_offer_status(db, table, order_id):
    order_is = db.session.query(table.order_status).filter_by(
        order_id=order_id).scalar()
    if order_is == 'доставлено':
        db.session.query(table).filter_by(order_id=order_id).update({'order_status': True})
        db.session.commit()


# функция меняет количество товара
def change_offer_amount(db, table, offer_id):
    now_amount = db.session.query(table).filter_by(offer_id=offer_id).scalar()
    if now_amount - 1 > 0:
        db.session.query(table).filter_by(offer_id=id).update({'amount': now_amount - 1})
        db.session.commit()
    else:
        return 'подушки на складе закончились'



def add_cart(db, table, person_id, offer_id):
    offer = db.session.query(table.cart).filter_by(person_id=int(person_id)).first()
    if offer == None:
        db.session.add(table(person_id=int(person_id), id_vk=int(person_id), cart=offer_id, name=get_user_name(person_id), email='', phone='', orders='', favorites=''))
    else:
        db.session.query(table).filter_by(person_id=int(person_id)).update({'cart': offer.cart + ',' + offer_id})
    db.session.commit()

def get_user_name(user, group_token):
    params = {'user_ids': user, 'v': '5.130', 'access_token': group_token}
    return requests.get('https://api.vk.com/method/users.get', params=params).json()['response'][0]['first_name']


def check_bill(user, billId):
    data = requests.get(f'https://api.qiwi.com/partner/bill/v1/bills/{billId}', headers={'Authorization': q_code, 'Content-Type': 'application/json', 'Accept': 'application/json'}).json()
    try:
        return data['status']['value']
    except KeyError:
        return 'ERROR'


def set_bill(user, amount, offers):
    data = {
        "amount": {
            "currency": "RUB",
            #"value": f"{int(0.98 * amount) + 1}.00"
            "value": "1.00"
        },
        "expirationDateTime": strftime("%Y-%m-%dT%H:%M:%S+03:00", localtime(time() + 28 * 3600)),
        "customFields" : {"themeCode": "Valentyn-GqasKW7ox5"}}
    data = requests.put(f'https://api.qiwi.com/partner/bill/v1/bills/{str(int(time()))}', json=data, headers={'Authorization': q_code, 'Content-Type': 'application/json', 'Accept': 'application/json'}).json()
    return data['billId'], data['payUrl']


def send_message(user, text, tabe, **kwargs):
    keyboards = {'main': '{"buttons":[[{"action":{"type":"text","label":"Куда я попал?","payload":""},"color":"positive"}],\
              [{"action":{"type":"text","label":"Каталог","payload":""},"color":"primary"}],\
              [{"action":{"type":"text","label":"Корзина","payload":""},"color":"primary"}],\
              [{"action":{"type":"text","label":"ЧаВо","payload":""},"color":"positive"}]]}',
                 'payment': '{"buttons":[[{"action":{"type":"text","label":"Я оплатил! \n Номер счета: ' + str(kwargs.get('billId')) + '","payload":""},"color":"positive"}]],"inline":true}'}

    params = {'user_id': user, 'random_id': 0, 'message': text, 'group_id': group_id, 'v': '5.130', 'access_token': group_token,
              'keyboard': keyboards.get(kwargs.get('keyboard'))}
    if kwargs.get('template') != None and 'catalog' in kwargs.get('template'):
        carousel = {"type": "carousel", "elements": []}
        pos = 6 * int(kwargs.get('template').replace('catalog', ''))
        for i in list(db.session.query(tabe).all())[pos: pos + 6]:
            carousel['elements'].append({"title": i.call + '\n' + str(i.actually_cost) + '₽', "description": i.about[:77] + '...', "action": {"type": "open_link", "link": f"https://oblako.pythonanywhere.com/offer/{i.offer_id}"}, "buttons": [{"action": {"type": "text", "label": f"💰 Купить \n [{i.offer_id}]"}, "color": "primary"}, {
                "action": {"type": "text", "label": f"➕ Добавить в корзину \n [{i.offer_id}]"}, "color": "positive"}, {"action": {"type": "open_link", "link": f"https://oblako.pythonanywhere.com/offer/{i.offer_id}", "label": "Поподробнее"}}]})

        params['template'] = dumps(carousel)
        del params['keyboard']

    return requests.get('https://api.vk.com/method/messages.send', params=params).text


# функции для проверки работы программы с компьютера
# def add_offer_to_offers_table(db, table):
#     call = input()
#     actually_cost_is = int(input())
#     always_cost = int(input())
#     about = input()
#     amount = 100
#     json_offer = {'size': ['big', 'small'],
#                   'color': ['red', 'blue', 'black']
#                   }
#     can_be = json.dumps(json_offer)
#     user_str = table(call=call, actually_cost=actually_cost_is,
#                      always_cost=always_cost, amount=amount,
#                      about=about, can_be=can_be)
#     db.session.add(user_str)
#     db.session.commit()
#
#
# def add_user_to_user(db, table):
#     print(f'name = input() email = input() phone = input()')
#     name = input()
#     email = input()
#     phone = input()
#     user_str = table(name=name, email=email, phone=phone)
#     db.session.add(user_str)
#     db.session.commit()
#
#
# def add_order_to_orders(db, table):
#     print(f'id who and id what')
#     who = int(input())
#     when = datetime.date.today()
#     what = int(input())
#     user_str = table(who_id=who, when=when, what_offer=what)
#     db.session.add(user_str)
#     db.session.commit()
#
# def add_picture_to_offer(db, table):
#     id = int(input())
#     pict = input()
#     offer_pict = db.session.query(table.call).filter_by(offer_id=id).scalar
#     path = f"assets/img/{pict}"
#     if path:
#         path_to = f"{offer_pict}?{path}"
#     else:
#         path_to = path
#     db.session.query(table).filter_by(offer_id=id).update({'picture': path_to})
#     db.session.commit()


# Функции для проверки заполнения
# def check_us(db, table):
#     save = db.session.query(table).all()
#     if save != None:
#         for x in save:
#             print(x)
#
#
# def check_of(db, table):
#     save = db.session.query(table).all()
#     if save != None:
#         for x in save:
#             print(x.actually_cost)
#         print(len(save))
#
#
# def check_ord(db, table):
#     save = db.session.query(table).all()
#     if save != None:
#         for x in save:
#             print(x)
