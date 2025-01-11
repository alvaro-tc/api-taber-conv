from app.extensions import db
from datetime import datetime
from app.models.guest_model import Guest
from app.models.user_model import User

class Payment(db.Model):
    __tablename__ = 'payments'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_payer = db.Column(db.Integer, db.ForeignKey('guests.id', ondelete='CASCADE'), nullable=False)
    id_guest = db.Column(db.Integer, db.ForeignKey('guests.id', ondelete='CASCADE'), nullable=False)
    id_user = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    first_payment = db.Column(db.Numeric(10, 2), nullable=True)
    second_payment = db.Column(db.Numeric(10, 2), nullable=True)
    fecha = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=False)
    observaciones = db.Column(db.Text, nullable=True)

    payer = db.relationship('Guest', foreign_keys=[id_payer], back_populates='payments_made')
    guest = db.relationship('Guest', foreign_keys=[id_guest], back_populates='payments_received')
    user = db.relationship('User', back_populates='payments_registered')
    details = db.relationship('PaymentDetail', back_populates='payment')

    @staticmethod
    def get_all():
        return Payment.query.all()

    @staticmethod
    def get_by_id(payment_id):
        return Payment.query.get(payment_id)

    def save(self):
        if not Guest.query.get(self.id_payer):
            raise ValueError("El pagador proporcionado no existe")
        if not Guest.query.get(self.id_guest):
            raise ValueError("El beneficiario proporcionado no existe")
        if not User.query.get(self.id_user):
            raise ValueError("El usuario (registrador) proporcionado no existe")
        
        db.session.add(self)
        db.session.commit()

    def update(self, id_payer=None, id_guest=None, id_user=None, first_payment=None, second_payment=None, fecha=None, observaciones=None):
        if id_payer and not Guest.query.get(id_payer):
            raise ValueError("El pagador proporcionado no existe")
        if id_guest and not Guest.query.get(id_guest):
            raise ValueError("El beneficiario proporcionado no existe")
        if id_user and not User.query.get(id_user):
            raise ValueError("El usuario (registrador) proporcionado no existe")
        
        if id_payer is not None:
            self.id_payer = id_payer
        if id_guest is not None:
            self.id_guest = id_guest
        if id_user is not None:
            self.id_user = id_user
        if first_payment is not None:
            self.first_payment = first_payment
        if second_payment is not None:
            self.second_payment = second_payment
        if fecha is not None:
            self.fecha = fecha
        if observaciones is not None:
            self.observaciones = observaciones
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def serialize(self):
        return {
            'id': self.id,
            'id_payer': self.id_payer,
            'id_guest': self.id_guest,
            'id_user': self.id_user,
            'first_payment': self.first_payment,
            'second_payment': self.second_payment,
            'fecha': self.fecha.isoformat(),
            'observaciones': self.observaciones
        }