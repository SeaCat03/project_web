def config(db):
    class Offers(db.Model):
        def __init__(self, offer_id, call, always_cost, actually_cost, about, can_be, amount, picture, photo_id):
            self.offer_id = offer_id
            self.call = call
            self.actually_cost = actually_cost
            self.always_cost = always_cost
            self.about = about
            self.can_be = can_be
            self.amount = amount
            self.picture = picture
            self.photo_id = photo_id

        offer_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
        call = db.Column(db.String)
        actually_cost = db.Column(db.Integer, nullable=True)
        always_cost = db.Column(db.Integer, nullable=True)
        amount = db.Column(db.Integer)
        picture = db.Column(db.Text)
        about = db.Column(db.String, nullable=True)
        can_be = db.Column(db.Text)
        photo_id = db.Column(db.String)

    return Offers
