from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from json import dumps, loads
from service import *

import db.models.offers as Offers
import db.models.users as Users
import db.models.orders as Orders


app = Flask(__name__, static_folder="assets")

# Настраиваем базу и само приложение
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/base.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)
user_table = Users.config(db)
offer_table = Offers.config(db)
order_table = Orders.config(db)

db.create_all()




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
            <h1 class="display-6" style="font-size: 200%;">{i.call}<br /></h1>
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


@app.route('/terms')
def terms():
    return render_template('terms.html')

@app.route('/offer/<offer_id>')
def product(offer_id):
    old_price = ''
    data = get_info_about_offer(db, offer_table, offer_id)

    pictures = ''
    active = 'active'
    for j in data['picture']:
        pictures += f'<div class="carousel-item {active}"><img class="w-100 d-block" src="{j}" alt="Slide Image" /></div>'
        active = ''
    if data['actually_cost'] != data['always_cost']:
        old_price = f'''<div class="col d-md-flex d-xxl-flex align-items-md-center align-items-xxl-center">
            <h1 class="display-6" style="font-size: 280%;"><span style="text-decoration: line-through;">{data["always_cost"]}₽</span><br></h1>
            </div>'''
    return render_template('product.html', offer_id=offer_id, call=data['call'], about=data['call'], price=data['actually_cost'], old_price=old_price, pictures=pictures)


@app.route('/bot', methods=['POST'])
def bot():
    data = dict(request.get_json())
    if data['type'] == 'confirmation':
        return '8cdc87db'
    if data['type'] == 'message_new':
        message = data['object']['message']
        if message['text'] == 'Начать':
            send_message(message['peer_id'], 'Привет! Продолжая общение с ботом Вы подтверждаете, что согласны с нашим пользовательским соглашением: http://oblako.pythonanywhere.com/terms', table=offer_table, keyboard='main')
            return 'ok'
        elif message['text'] == 'Куда я попал?':
            send_message(
                message['peer_id'], f'Сейчас вы общаетесь с ботом самого технологичного интернет-магазина подушек "ОблакО"', table=offer_table, keyboard='main')
            return 'ok'

        elif message['text'] in ['ЧаВо', 'ЧАВО', 'ЧаВО', 'ЧЗВ', 'frequently asked questions', 'FAQ', 'F.A.Q']:
            send_message(message['peer_id'], f'Часто задаваемые вопросы:\n\n\
                     1. Как общаться с ботом?\n - Вы можете общаться с ботом при помощи виртуальной клавиатуры.\n\n\
                     2. Какими способами я могу оплатить товар?\n - Вы можете оплатить товар Банковской картой или воспользоваться Qiwi кошельком.\n\n\
                     3. Могу ли я оплатить товар через VK Pay?\n - Да, можете, в разделе католога "Товары" нашего сообщества можно оплатить через VK Pay.', table=offer_table, keyboard='main')
            return 'ok'

        elif message['text'] == 'Каталог':
            send_message(message['peer_id'], f'Вот наш каталог:', table=offer_table, template='catalog0')
            for i in range(1, len(list(db.session.query(offer_table).all())) // 9 + 1):
                sleep(1)
                send_message(message['peer_id'], '.', table=offer_table, template=f'catalog{i}')
            return 'ok'

        elif 'Купить' in message['text'] and '[' in message['text']:
            send_message(message['peer_id'], 'Секунду...', table=offer_table)
            offer = db.session.query(offer_table).filter_by(offer_id=int(message['text'].split('[')[1].split(']')[0])).first()
            billId, Url = set_bill(message['peer_id'], offer.actually_cost, [offer.actually_cost])
            send_message(message['peer_id'], 'Перейдите по ссылке, оплатите и нажмите на кнопку "Я оплатил". Будьте внимательны, ссылка действует лишь сутки! \n' + Url, table=offer_table, keyboard='payment', billId=billId)
            return 'ok'

        elif 'Добавить в корзину' in message['text'] and '[' in message['text']:
            offer = message['text'].split('[')[1].split(']')[0]
            send_message(message['peer_id'], 'Секунду...', table=offer_table)
            user = db.session.query(user_table).filter_by(person_id=int(message['peer_id'])).first()
            if user == None:
                db.session.add(user_table(person_id=message['peer_id'], id_vk=message['peer_id'], cart=offer, name=get_user_name(message['peer_id']), email='', phone='', orders='', favorites=''))
            else:
                db.session.query(user_table).filter_by(person_id=int(message['peer_id'])).update({'cart': user.cart + ',' + offer})
            send_message(message['peer_id'], 'Добавили в корзину!', table=offer_table)
            db.session.commit()
            return 'ok'

        elif message['text'] == 'Корзина':
            send_message(message['peer_id'], 'Секунду...', table=offer_table)
            user = db.session.query(user_table).filter_by(person_id=int(message['peer_id'])).first()
            if user == None:
                send_message(message['peer_id'], 'Пока что корзина пуста', table=offer_table)
                db.session.add(user_table(person_id=message['peer_id'], id_vk=message['peer_id'], cart='', name=get_user_name(message['peer_id']), email='', phone='', orders='', favorites=''))
            else:
                res = ''
                for i in user.cart.split(','):
                    now = db.session.query(offer_table).filter_by(offer_id=int(i)).first()
                    res += now.call + ' ' + str(now.actually_cost) + '₽\n'
                send_message(message['peer_id'], 'Корзина: \n' + res, table=offer_table)
            return 'ok'

        elif 'Я оплатил' in message['text']:
            send_message(message['peer_id'], 'Секунду...', table=offer_table)
            status = check_bill(1, message['text'].split(': ')[1])
            if status == 'WAITING':
                send_message(message['peer_id'], 'Пока что платеж не пришел. Подождите пока платешь пройдёт и повторите запрос', table=offer_table)
            elif status == 'REJECTED':
                send_message(message['peer_id'], 'Счет отклонен. Оформите заказ повторно')
            elif status == 'EXPIRED':
                send_message(message['peer_id'], 'Ссылка для платежа устарела. Оформите заказ повторно. Будьте внимательны - ссылка действительна лишь сутки!', table=offer_table)
            elif status == 'PAID':
                send_message(message['peer_id'], 'Отлично, счет оплачен! Мы приняли Ваш заказ. Совсем скоро с Вами свяжется администратор!', table=offer_table)
            else:
                send_message(message['peer_id'], 'Мы не смогли определить статус платежа. Возможно был указан недействительный номер.', table=offer_table)
            return 'ok'
        else:
            name = get_user_name(message['peer_id'])
            send_message(
                message['peer_id'], f'Здравствуйте, {name}, Вас приветствует интернет-магазин подушек "ОблакО". Я - Ваш консультант, могу чем-то помочь?', table=offer_table, keyboard='main')
            return 'ok'



if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
