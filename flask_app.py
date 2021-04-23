from flask import Flask, render_template, request, redirect, make_response
from flask_sqlalchemy import SQLAlchemy
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


@app.route('/lk', methods=['GET', 'POST'])
def lk():
    person_id = request.cookies.get('person_id')
    if not check_token(person_id, request.cookies.get('token')) or person_id == None:
        return redirect('/login')

    person_id = int(person_id)
    name = get_user_name(person_id)
    #name = db.session.query(user_table).filter_by(person_id=person_id).scalar()
    if request.method == 'POST':
        if request.form.get('type') == 'delete_cart':
            del_cart_from_person(db, user_table, person_id, request.form.get('product_id'))
        elif request.form.get('type') == 'delete_like':
            del_offer_from_person(db, user_table, person_id, str(request.form.get('product_id')))
        else:
            return redirect('confirm')
    old_price = ''
    cart_list, cart_count = check_cart(db, user_table, person_id)
    fav_list, fav_count = check_fav(db, user_table, person_id)
    print(fav_list, fav_count)
    print(cart_list, cart_count)
    cart = ''
    fav = ''
    for x in cart_list:
        cart_count = 0
        for i in x.split(','):
            if i != '':
                cart_count += 1
                data = get_info_about_offer(db, offer_table, int(i))
                cart += f'''<div class="card shadow-lg" id="product_id" style="border-top-left-radius: 5vh;border-bottom-right-radius: 5vh;margin-right: 1%;width: 48%;">
                                    <div class="card-body shadow-lg" style="border-top-left-radius: 5vh;border-bottom-right-radius: 5vh;">
                                        <h4 class="d-md-flex d-lg-flex d-xl-flex d-xxl-flex justify-content-md-center justify-content-lg-center justify-content-xl-center justify-content-xxl-center card-title">{data['call']}<br></h4><img src="{data['picture'][0]}" alt="Slide Image" style="width: 100%;">
                                        <form style="margin-top: 2.5vw;" method="post"><input class="form-control" type="hidden" name="type" value="delete_cart"><input class="form-control" type="hidden" name="product_id" value="{i}"><button class="btn btn-danger" type="submit" style="width: 100%;margin-top: 0.5vh;margin-bottom: 2vh;"><i class="fas fa-eraser"></i> Удалить из корзины</button></form>
                                    </div>
                                </div>'''
    for x in fav_list:
        fav_count = 0
        for i in x.split(','):
            if i != '':
                fav_count += 1
                data = get_info_about_offer(db, offer_table, int(i))
                fav += f'''<div class="card shadow-lg" id="product_id-2" style="border-top-left-radius: 5vh;border-bottom-right-radius: 5vh;margin-left: 1%;width: 48%;">
                                <div class="card-body shadow-lg" style="border-top-left-radius: 5vh;border-bottom-right-radius: 5vh;">
                                    <h4 class="d-md-flex d-lg-flex d-xl-flex d-xxl-flex justify-content-md-center justify-content-lg-center justify-content-xl-center justify-content-xxl-center card-title">{data['call']}<br></h4><img src="{data['picture'][0]}" alt="Slide Image" style="width: 100%;">
                                    <form method="post"><input type="hidden" class="form-control" name="type" value="delete_like" /><input type="hidden" class="form-control" name="product_id" value="{i}" /><button class="btn btn-danger" type="submit" style="width: 100%;margin-top: 0.5vh;margin-bottom: 2vh;"><i class="fas fa-eraser"></i> Удалить из избранных</button></form>
                                </div>
                            </div>'''
    return render_template('user.html', name=name, cart=cart, cart_count=cart_count, fav_count=fav_count, fav=fav)


@app.route('/confirm', methods=['GET', 'POST'])
def confirm():
    person_id = request.cookies.get('person_id')
    if not check_token(person_id, request.cookies.get('token')) or person_id == None:
        return redirect('/login')
    person_id = int(person_id)
    if request.method == 'GET':
        return render_template('confirm.html')
    else:
        amount = 0
        offers = []
        user = db.session.query(user_table).filter_by(person_id=person_id).first()
        for i in user.cart.split(','):
            if i == '':
                continue
            i = db.session.query(offer_table).filter_by(offer_id=int(i)).first()
            amount += i.actually_cost
            offers.append(str(i))

        billId, Url = set_bill(db, person_id, amount, offers)
        return render_template('ok.html', Url=Url, billId=billId)

@app.route('/check/<billId>')
def check(billId):
    person_id = request.cookies.get('person_id')
    if not check_token(person_id, request.cookies.get('token')) or person_id == None:
        return redirect('/login')
    person_id = int(person_id)
    status = check_bill(db, person_id, billId)
    if status == 'WAITING':
        message = 'Пока что платеж не пришел. Подождите пока платеж пройдёт и повторите запрос'
    elif status == 'REJECTED':
        message = 'Счет отклонен. Оформите заказ повторно'
    elif status == 'EXPIRED':
        message = 'Ссылка для платежа устарела. Оформите заказ повторно. Будьте внимательны - ссылка действительна лишь сутки!'
    elif status == 'PAID':
        message = f'Отлично, счет оплачен! Мы приняли Ваш заказ. Совсем скоро с Вами свяжется администратор! Номер заказа: {billId}'
    else:
        message = 'Мы не смогли определить статус платежа. Возможно был указан недействительный номер'

    return render_template('check.html', message=message)


@app.route('/login')
def login():
    if request.args.get('code') == None:
        return render_template('login.html')
    else:
        data = requests.get(f'https://oauth.vk.com/access_token?client_id=7834991&client_secret=MerCQsWolUeNsetJsbtW&redirect_uri=https://oblako.pythonanywhere.com/login&code={request.args.get("code")}').json()
        person_id = data['user_id']
        if db.session.query(user_table).filter_by(person_id=int(person_id)).first() == None:
            db.session.add(user_table(person_id=person_id, id_vk=person_id, cart=offer, name=get_user_name(person_id), email='', phone='', orders='', favorites=''))
            db.session.commit()
        resp = make_response(redirect('/lk'))
        resp.set_cookie('person_id', str(person_id), max_age=3600*12)
        resp.set_cookie('token', generate_token(person_id), max_age=3600*12)
        return resp




@app.route('/offer/<offer_id>', methods=['GET', 'POST'])
def product(offer_id):
    person_id = request.cookies.get('person_id')
    if not check_token(person_id, request.cookies.get('token')) or person_id == None:
        return redirect('/login')
    person_id = int(person_id)
    old_price = ''
    data = get_info_about_offer(db, offer_table, offer_id)
    favorites, active = check_fav(db, user_table, person_id)
    cart, col = check_cart(db, user_table, person_id)
    fav_list = []
    try:
        if favorites:
            for x in favorites:
                for y in x.split(','):
                    fav_list.append(int(y))
    except Exception:
        fav_list = []
    cart_list = []
    try:
        if cart:
            for x in cart:
                for y in x.split(','):
                    cart_list.append(int(y))
    except Exception:
        cart_list = []
    pictures = ''
    active = 'active'
    can_be_off = ''
    type_can_be = ''
    if request.method == "POST":
        if request.form.get('type') == 'like':
            if int(offer_id) in fav_list:
                del_offer_from_person(db, user_table, person_id, offer_id)
                favorites, t = check_fav(db, user_table, person_id)
            else:
                add_offer_to_person_favorites(db, user_table, person_id, offer_id)
                favorites, t = check_fav(db, user_table, person_id)
        elif request.form.get('type') == 'add':
            if int(offer_id) not in cart_list:
                add_cart(db, user_table, person_id, offer_id)
    if offer_id in favorites:
        person_fav = f'''<form method="post"><input class="form-control" type="hidden" name="type" value="like"><input class="form-control" type="hidden" name="offer_id" value="{offer_id}"><button class="btn btn-info" type="submit" style="background: rgba(255,255,255,0);border-style: none;"><i class="far fa-heart" style="font-size: 300%"; color: "#ff0000"></i></button></form>'''
    else:
        person_fav = f'''<form method="post"><input class="form-control" type="hidden" name="type" value="like"><input class="form-control" type="hidden" name="offer_id" value="{offer_id}"><button class="btn btn-info" type="submit" style="background: rgba(255,255,255,0);border-style: none;"><i class="far fa-heart" style="font-size: 300%;"></i></button></form>'''
    for j in data['picture']:
        pictures += f'<div class="carousel-item {active}"><img class="w-100 d-block" src="{j}" alt="Slide Image" /></div>'
        active = ''
    if data['actually_cost'] != data['always_cost']:
        p = data["always_cost"]
        old_price = p
    if 'color' in data['can_be'].keys():
        type_can_be += data['can_be']['color']['name']
        for x in data['can_be']['color'].keys():
            if x != 'name':
                can_be_off += f'''<option value="black">{data['can_be']['color'][x]}</option>'''
    if 'size' in data['can_be'].keys():
        type_can_be += data['can_be']['size']['name']
        for x in data['can_be']['size'].keys():
            if x != 'name':
                can_be_off += f'''<option value="black">{data['can_be']['size'][x]}</option>'''
    return render_template('product.html', offer_id=offer_id, call=data['call'], about=data['call'],
                           price=data['actually_cost'], old_price=old_price, pictures=pictures, can_be=can_be_off, can_be_name=type_can_be, person_fav=person_fav)


@app.route('/bot', methods=['POST'])
def bot():
    data = dict(request.get_json())
    if data['type'] == 'confirmation':
        return '8cdc87db'
    if data['type'] == 'message_new':
        message = data['object']['message']
        if message['text'] == 'Начать':
            send_message(db, message['peer_id'], 'Привет! Продолжая общение с ботом Вы подтверждаете, что согласны с нашим пользовательским соглашением: http://oblako.pythonanywhere.com/terms', table=offer_table, keyboard='main')
            return 'ok'
        elif message['text'] == 'Куда я попал?':
            send_message(db,
                message['peer_id'], f'Сейчас вы общаетесь с ботом самого технологичного интернет-магазина подушек "ОблакО"', table=offer_table, keyboard='main')
            return 'ok'

        elif message['text'] in ['ЧаВо', 'ЧАВО', 'ЧаВО', 'ЧЗВ', 'frequently asked questions', 'FAQ', 'F.A.Q']:
            send_message(db, message['peer_id'], f'Часто задаваемые вопросы:\n\n\
                     1. Как общаться с ботом?\n - Вы можете общаться с ботом при помощи виртуальной клавиатуры.\n\n\
                     2. Какими способами я могу оплатить товар?\n - Вы можете оплатить товар Банковской картой или воспользоваться Qiwi кошельком.\n\n\
                     3. Могу ли я оплатить товар через VK Pay?\n - Да, можете, в разделе католога "Товары" нашего сообщества можно оплатить через VK Pay.', table=offer_table, keyboard='main')
            return 'ok'

        elif message['text'] == 'Каталог':
            send_message(db, message['peer_id'], f'Вот наш каталог:', table=offer_table, template='catalog0')
            for i in range(1, len(list(db.session.query(offer_table).all())) // 9 + 1):
                sleep(1)
                send_message(db, message['peer_id'], '&#12288;', table=offer_table, template=f'catalog{i}')
            return 'ok'

        elif 'Купить' in message['text'] and '[' in message['text']:
            send_message(db, message['peer_id'], 'Секунду...', table=offer_table)
            offer = db.session.query(offer_table).filter_by(offer_id=int(message['text'].split('[')[1].split(']')[0])).first()
            billId, Url = set_bill(db, message['peer_id'], offer.actually_cost, [offer.offer_id])
            send_message(db, message['peer_id'], 'Перейдите по ссылке, оплатите и нажмите на кнопку "Я оплатил". Будьте внимательны, ссылка действует лишь сутки! \n' + Url, table=offer_table, keyboard='payment', billId=billId)
            return 'ok'

        elif 'Добавить в корзину' in message['text'] and '[' in message['text']:
            offer = message['text'].split('[')[1].split(']')[0]
            send_message(db, message['peer_id'], 'Секунду...', table=offer_table)
            user = db.session.query(user_table).filter_by(person_id=int(message['peer_id'])).first()
            if user == None:
                db.session.add(user_table(person_id=message['peer_id'], id_vk=message['peer_id'], cart=offer, name=get_user_name(message['peer_id']), email='', phone='', orders='', favorites=''))

            elif len(user.cart) == 0:
                db.session.query(user_table).filter_by(person_id=int(message['peer_id'])).update({'cart': offer})
            else:
                db.session.query(user_table).filter_by(person_id=int(message['peer_id'])).update({'cart': user.cart + ',' + offer})
            send_message(db, message['peer_id'], 'Добавили в корзину!', table=offer_table)
            db.session.commit()
            return 'ok'

        elif message['text'] == 'Корзина':
            user = db.session.query(user_table).filter_by(person_id=int(message['peer_id'])).first()
            if user == None or len(user.cart) == 0:
                send_message(db, message['peer_id'], 'Пока что ваша корзина пуста', table=offer_table)
            else:
                send_message(db, message['peer_id'], 'Ваша корзина: ', table=user_table, offer_table=offer_table, template='cart0')
                for i in range(1, len(list(user.cart.split(','))) // 9 + 1):
                    send_message(db, message['peer_id'], '&#12288;', table=offer_table, template=f'cart{i}')
                send_message(db, message['peer_id'], '&#12288;', table=offer_table, keyboard='cart')
            return 'ok'

        elif 'Удалить из корзины' in message['text']:
            user = db.session.query(user_table).filter_by(person_id=int(message['peer_id'])).first()
            if user == None or len(user.cart) == 0:
                send_message(db, message['peer_id'], 'Пока что ваша корзина пуста', table=offer_table, keyboard='main')
            else:
                cart = list(user.cart.split(','))
                cart.pop(cart.index(message['text'].split('[')[1].split(']')[0]))
                db.session.query(user_table).filter_by(person_id=int(message['peer_id'])).update({'cart': ','.join(cart)})
                send_message(db, message['peer_id'], 'Удалили из корзины!', table=offer_table, keyboard='main')
                db.session.commit()
            return 'ok'

        elif 'Очистить всю корзину' in message['text']:
            user = db.session.query(user_table).filter_by(person_id=int(message['peer_id'])).first()
            if user == None or len(user.cart) == 0:
                send_message(db, message['peer_id'], 'Корзина пуста', table=offer_table, keyboard='main')
            else:
                db.session.query(user_table).filter_by(person_id=int(message['peer_id'])).update({'cart': ''})
                send_message(db, message['peer_id'], 'Очистили!', table=offer_table, keyboard='main')
                db.session.commit()
            return 'ok'

        elif 'Оформить заказ' in message['text']:
            user = db.session.query(user_table).filter_by(person_id=int(message['peer_id'])).first()
            if user == None or len(user.cart) == 0:
                send_message(db, message['peer_id'], 'Корзина пуста', table=offer_table, keyboard='main')
            else:
                send_message(db, message['peer_id'], 'Секунду...', table=offer_table)

                amount = 0
                offers = []
                user = db.session.query(user_table).filter_by(person_id=int(message['peer_id'])).first()
                if user == None or len(user.cart) == 0:
                    send_message(db, message['peer_id'], 'Корзина пуста', table=offer_table, keyboard='main')
                else:
                    for i in user.cart.split(','):
                        if i != '':
                            i = db.session.query(offer_table).filter_by(offer_id=int(i)).first()
                            amount += i.actually_cost
                            offers.append(str(i))
                    billId, Url = set_bill(db, message['peer_id'], amount, offers)
                    send_message(db, message['peer_id'], 'Перейдите по ссылке, оплатите и нажмите на кнопку "Я оплатил". Будьте внимательны, ссылка действует лишь сутки! \n' + Url, table=offer_table, keyboard='payment', billId=billId)
                    send_message(db, message['peer_id'], '&#12288;', table=offer_table, keyboard='main')
            return 'ok'

        elif 'На главную' in message['text']:
            send_message(db, message['peer_id'], 'Главная', table=offer_table, keyboard='main')
            return 'ok'

        elif 'Я оплатил' in message['text']:
            send_message(db, message['peer_id'], 'Секунду...', table=offer_table)
            status = check_bill(db, message['peer_id'], message['text'].split(': ')[1])
            if status == 'WAITING':
                send_message(db, message['peer_id'], 'Пока что платеж не пришел. Подождите пока платеж пройдёт и повторите запрос', table=offer_table)
            elif status == 'REJECTED':
                send_message(db, message['peer_id'], 'Счет отклонен. Оформите заказ повторно')
            elif status == 'EXPIRED':
                send_message(db, message['peer_id'], 'Ссылка для платежа устарела. Оформите заказ повторно. Будьте внимательны - ссылка действительна лишь сутки!', table=offer_table)
            elif status == 'PAID':
                send_message(db, message['peer_id'], 'Отлично, счет оплачен! Мы приняли Ваш заказ. Совсем скоро с Вами свяжется администратор!', table=offer_table)
            else:
                send_message(db, message['peer_id'], 'Мы не смогли определить статус платежа. Возможно был указан недействительный номер.', table=offer_table)
            return 'ok'
        else:
            name = get_user_name(message['peer_id'])
            send_message(db,
                message['peer_id'], f'Здравствуйте, {name}, Вас приветствует интернет-магазин подушек "ОблакО". Я - Ваш консультант, могу чем-то помочь?', table=offer_table, keyboard='main')
            return 'ok'

@app.route('/c')
def c():
    return check_bill('1', 1618312493)

if __name__ == '__main__':
   app.run(port=8080, host='127.0.0.1')
