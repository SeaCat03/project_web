from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import datetime
import json

import db.models.offers as Offers
import db.models.users as Users
import db.models.orders as Orders

app = Flask(__name__, static_folder="assets")
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/base.sqlite3'
db = SQLAlchemy(app)
user_table = Users.config(db)  # Поменять имя файла и таблицы (status_t)
offer_table = Offers.config(db)
order_table = Orders.config(db)
db.create_all()


def add_offer_to_offers_table():
    call = input()
    actually_cost_is = int(input())
    always_cost = int(input())
    about = input()
    json_offer = {'size': ['big', 'small'],
                  'color': ['red', 'blue', 'black']
                  }
    can_be = json.dumps(json_offer)
    user_str = offer_table(call=call, actually_cost=actually_cost_is, always_cost=always_cost, about=about, can_be=can_be)
    db.session.add(user_str)
    db.session.commit()


def add_user_to_user():
    print(f'name = input() email = input() phone = input()')
    name = input()
    email = input()
    phone = input()
    user_str = user_table(name=name, email=email, phone=phone)
    db.session.add(user_str)
    db.session.commit()


def add_order_to_orders():
    print(f'id who and id what')
    who = int(input())
    when = datetime.date.today()
    what = int(input())
    user_str = order_table(who_id=who, when=when, what_offer=what)
    db.session.add(user_str)
    db.session.commit()


def check_us():
    save = db.session.query(user_table).all()
    if save != None:
        for x in save:
            print(x)


def check_of():
    save = db.session.query(offer_table).all()
    if save != None:
        for x in save:
            print(x.actually_cost)
        print(len(save))


def check_ord():
    save = db.session.query(order_table).all()
    if save != None:
        for x in save:
            print(x)


if __name__ == '__main__':
    check_us()
    print('------------------------')
