
from app.extensions import db
from datetime import datetime

class PaymentConcept(db.Model):
    __tablename__ = 'payment_concepts'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False)
    monto_inicial = db.Column(db.Numeric(10, 2), nullable=False)

    @staticmethod
    def get_all():
        return PaymentConcept.query.all()

    @staticmethod
    def get_by_id(payment_concept_id):
        return PaymentConcept.query.get(payment_concept_id)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self, nombre=None, monto_inicial=None):
        if nombre is not None:
            self.nombre = nombre
        if monto_inicial is not None:
            self.monto_inicial = monto_inicial
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def serialize(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'monto_inicial': self.monto_inicial
        }