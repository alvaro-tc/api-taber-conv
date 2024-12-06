from extensions import db

class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False)

    @staticmethod
    def get_all():
        return Product.query.all()

    @staticmethod
    def get_by_id(product_id):
        return Product.query.get(product_id)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self, name, description, price, stock):
        self.name = name
        self.description = description
        self.price = price
        self.stock = stock
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()