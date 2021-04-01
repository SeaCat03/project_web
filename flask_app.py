from flask import Flask
from flask import render_template
from flask_sqlalchemy import SQLAlchemy
import requests
import datetime

import db.models.offers as Offers
import db.models.users as Users
import db.models.orders as Orders

# app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

app = Flask(__name__, static_folder="assets")

# Настраиваем базу и само приложение
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/base.sqlite3'  # Настраиваем базу и само приложение
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)
user_table = Users.config(db)
offer_table = Offers.config(db)
order_table = Orders.config(db)

db.create_all()


@app.route('/terms')
def terms():
    return render_template('terms.html')


@app.route('/')
def index():
    products = ''
    for i in db.session.query(offer_table).all():
        pictures = ''
        old_price = ''

        if i.actually_cost != i.always_cost:
            old_price = f'''<div class="col">
                    <h1 class="display-6" style="font-size: 150%;color: rgb(153,153,153);"><span style="text-decoration: line-through;">{i.always_cost}</span><strong><span style="text-decoration: line-through;">₽</span></strong><br /></h1>
                </div>'''
        active = 'active'
        for j in i.picture.split('?'):
            pictures += f'<div class="carousel-item {active}"><img class="w-100 d-block" src="{j}" alt="Slide Image" /></div>'
            active = ''
        products += f'''<div class="col" style="padding-top: 1vh;"><a href="offer/{i.offer_id}" style="text-decoration: none;color: black;">
        <div class="card" style="border-top-left-radius: 3vh;border-bottom-right-radius: 2vh;">
            <div class="card-body d-xxl-flex flex-column align-items-xxl-center">
                <div data-bs-ride="carousel" data-bs-interval="false" class="carousel slide" id="carousel-{i.offer_id}">
                    <div class="carousel-inner" style="border-top-left-radius: 2vh;border-bottom-right-radius: 2vh;">
                        {pictures}
                    </div>
                    <div><a href="#carousel-{i.offer_id}" role="button" data-bs-slide="prev" class="carousel-control-prev"><span class="carousel-control-prev-icon"></span><span class="visually-hidden">Previous</span></a><a href="#carousel-{i.offer_id}" role="button" data-bs-slide="next" class="carousel-control-next"><span class="carousel-control-next-icon"></span><span class="visually-hidden">Next</span></a></div>
                </div>
                <h1 class="display-6" style="font-size: 200%;">Подушка от LongDog<br /></h1>
            </div>
            <div class="row">
                <div class="col">
                    <h1 class="display-6" style="font-size: 150%;margin-left: 10%;">{i.actually_cost}<strong>₽</strong><br /></h1>
                </div>
                {old_price}
            </div>
        </div>
    </a></div>'''

    return render_template('index.html', products=products)
    # return render_template('index-wcopy.html')


@app.route('/query')
def query():
    # status_user.person_name = 'Vasya'
    # status_user.person_email = 'vasyapupkin@gmail.com'
    # status_user.person_phone_number = 89723861896
    return 'Сделай запрос'


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')