def config(db):
    class Orders(db.Model):
        def __init__(self, who_id, when, what_offer, status='в пути'):
            self.who_id = who_id
            self.order_status = status
            self.when = when
            self.what_offer = what_offer

        order_id = db.Column(db.Integer, primary_key=True)
        who_id = db.Column(db.Integer, db.ForeignKey("users.person_id"))
        order_status = db.Column(db.String)
        when = db.Column(db.DATE)
        what_offer = db.Column(db.Integer, db.ForeignKey("offers.offer_id"))

    return Orders
