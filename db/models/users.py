def config(db):
    class Users(db.Model):
        def __init__(self, name, email, phone, id_vk=0, orders='', favorites=''):
            self.name = name
            self.email = email
            self.phone = phone
            self.orders = orders
            self.favorites = favorites
            self.id_vk = id_vk
        person_id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String, nullable=True)
        email = db.Column(db.String)
        id_vk = db.Column(db.Integer)
        phone = db.Column(db.String, nullable=True)
        orders = db.Column(db.String)
        favorites = db.Column(db.String)
    return Users
