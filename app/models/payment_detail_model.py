from app.extensions import db
from app.models.payment_model import Payment


class PaymentDetail(db.Model):
    __tablename__ = 'payment_details'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_payment = db.Column(db.Integer, db.ForeignKey('payments.id', ondelete='CASCADE'), nullable=False)
    concepto = db.Column(db.String(100), nullable=False)
    monto = db.Column(db.Numeric(10, 2), nullable=False)

    payment = db.relationship('Payment', back_populates='details')

    @staticmethod
    def get_all():
        return PaymentDetail.query.all()

    @staticmethod
    def get_by_id(payment_detail_id):
        return PaymentDetail.query.get(payment_detail_id)

    def save(self):
        if not Payment.query.get(self.id_payment):
            raise ValueError("El pago proporcionado no existe")
        
        db.session.add(self)
        db.session.commit()

    def update(self, id_payment=None, concepto=None, monto=None):
        if id_payment and not Payment.query.get(id_payment):
            raise ValueError("El pago proporcionado no existe")
        
        if id_payment is not None:
            self.id_payment = id_payment
        if concepto is not None:
            self.concepto = concepto
        if monto is not None:
            self.monto = monto
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def serialize(self):
        return {
            'id': self.id,
            'id_payment': self.id_payment,
            'concepto': self.concepto,
            'monto': self.monto
        }
