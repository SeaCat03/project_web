def config(db):
    class Offers(db.Model):
        def __init__(self, call, always_cost, actually_cost, about, can_be):
            self.call = call
            self.actually_cost = actually_cost
            self.always_cost = always_cost
            self.about = about
            self.can_be = can_be
        offer_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
        call = db.Column(db.String)
        actually_cost = db.Column(db.Integer, nullable=True)
        always_cost = db.Column(db.Integer, nullable=True)
        about = db.Column(db.String, nullable=True)
        can_be = db.Column(db.Text)
    return Offers
