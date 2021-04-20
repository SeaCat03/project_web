from flask import Flask
from flask import render_template
from flask_sqlalchemy import SQLAlchemy

import db.models.offers as Offer
import db.models.users as User  # из папки db/models импортировать файл status
import db.models.order as Order

# app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

app = Flask(__name__, static_folder="assets")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/base.sqlite3'  # Настраиваем базу и само приложение
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)

user_table = User.config(db)  # Поменять имя файла и таблицы (status_t)
offer_table = Offer.config(db)
order_table = Order.config(db)
db.create_all()


@app.route('/')
def index():
    return render_template('index.html')
    # return render_template('index-wcopy.html')


@app.route('/query')
def query():
    #status_user.person_name = 'Vasya'
    #status_user.person_email = 'vasyapupkin@gmail.com'
    #status_user.person_phone_number = 89723861896
    first = user_table(person_name='Ya', person_email='ya@gmail.com', phone_access_token= ,person_phone_number=89583861896)
    db.session.add_all([first])
    db.session.commit()
    return 'Сделай запрос'


#def get_token():
    



if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
