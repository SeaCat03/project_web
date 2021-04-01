from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import datetime
import json

import db.models.offers as Offers
import db.models.users as Users
import db.models.orders as Orders

# app = Flask(__name__, static_folder="assets")
# app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/base.sqlite3'
# db = SQLAlchemy(app)
# db.create_all()


def add_offer_to_offers_table(db, table):
    call = input()
    actually_cost_is = int(input())
    always_cost = int(input())
    about = input()
    amount = 100
    json_offer = {'size': ['big', 'small'],
                  'color': ['red', 'blue', 'black']
                  }
    can_be = json.dumps(json_offer)
    user_str = table(call=call, actually_cost=actually_cost_is, always_cost=always_cost, amount=amount,
                     about=about, can_be=can_be)
    db.session.add(user_str)
    db.session.commit()


def add_user_to_user(db, table):
    print(f'name = input() email = input() phone = input()')
    name = input()
    email = input()
    phone = input()
    user_str = table(name=name, email=email, phone=phone)
    db.session.add(user_str)
    db.session.commit()


def add_order_to_orders(db, table):
    print(f'id who and id what')
    who = int(input())
    when = datetime.date.today()
    what = int(input())
    user_str = table(who_id=who, when=when, what_offer=what)
    db.session.add(user_str)
    db.session.commit()


def add_picture_to_offer(db, table):
    id = int(input())
    pict = input()
    offer_pict = db.session.query(table.call).filter_by(offer_id=id).scalar
    path = f"assets/img/{pict}"
    if path:
        path_to = f"{offer_pict}?{path}"
    else:
        path_to = path
    db.session.query(table).filter_by(offer_id=id).update({'picture': path_to})
    db.session.commit()


def add_user_to_user_table(db, table, name, phone):
    user_str = table(name=name, phone=phone)
    db.session.add(user_str)
    db.session.commit()


def add_email_to_user_table(db, table, name, phone, email):
    db.session.query(table).filter_by(name=name, phone=phone).update({'email': email})
    db.session.commit()


def get_info_about_offer(db, table, offer_id):
    offer_call = db.session.query(table.call).filter_by(offer_id=offer_id).first()
    offer_actually = db.session.query(table.actually_cost).filter_by(offer_id=offer_id).first()
    offer_always = db.session.query(table.always_cost).filter_by(offer_id=offer_id).first()
    offer_about_str = db.session.query(table.about).filter_by(offer_id=offer_id).first()
    offer_can_be = db.session.query(table.can_be).filter_by(offer_id=offer_id).first()
    db.session.commit()
    if bool([offer_always, offer_actually, offer_about_str, offer_can_be]):
        answer_json = {
            'call': offer_call,
            'actually_cost': offer_actually,
            'always_cost': offer_always,
            'about': offer_about_str,
            'can_be': offer_can_be
        }
        return answer_json


def add_order_from_user(db, table_ord, table_us, who_add, what_add):
    date_to_save = datetime.date.today()
    str_to_save = table_ord(who_id=who_add, order_status='в пути', when=date_to_save, what_offer=what_add)
    db.session.add(str_to_save)
    db.session.commit()
    order_id_to_later = db.session.query(table_ord.order_id).filter_by(who_id=who_add, when=date_to_save,
                                                                         what_offer=what_add).scalar()
    if order_id_to_later != None:
        what_user_has = db.session.query(table_us.orders).filter_by(person_id=who_add).scalar()
        if what_user_has != None:
            add_what = f"{what_user_has},{order_id_to_later}"
            db.session.query(table_us).filter_by(person_id=who_add).update({'orders': add_what})
            db.session.commit()


def add_offer_to_person_favorites(db, table, who_id, what_id):
    what_user_has = db.session.query(table.favorites).filter_by(person_id=who_id).scalar()
    if what_user_has != None:
        add_what = f"{what_user_has},{what_id}"
        db.session.query(table).filter_by(user_id=who_id).update({'favorites': add_what})
        db.session.commit()


def change_offer_status(db, table, order_id):
    order_is = db.session.query(table.order_status).filter_by(order_id=order_id).scalar()
    if order_is == 'доставлено':
        db.session.query(table).filter_by(order_id=order_id).update({'order_status': True})
        db.session.commit()


def change_offer_amount(db, table, offer_id):
    now_amount = db.session.query(table).filter_by(offer_id=offer_id).scalar()
    if now_amount - 1 > 0:
        db.session.query(table).filter_by(offer_id=id).update({'amount': now_amount - 1})
        db.session.commit()
    else:
        return 'подушки на складе закончились'


# Функции для проверки заполнения
def check_us(db, table):
    save = db.session.query(table).all()
    if save != None:
        for x in save:
            print(x)


def check_of(db, table):
    save = db.session.query(table).all()
    if save != None:
        for x in save:
            print(x.actually_cost)
        print(len(save))


def check_ord(db, table):
    save = db.session.query(table).all()
    if save != None:
        for x in save:
            print(x)
