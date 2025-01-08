from app.extensions import db
from datetime import datetime

class Payment(db.Model):
    __tablename__ = 'payments'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    monto1 = db.Column(db.Float, nullable=False)
    monto2 = db.Column(db.Float, nullable=False)
    observaciones1 = db.Column(db.String(255), nullable=True)
    observaciones2 = db.Column(db.String(255), nullable=False)
    fecha_registro = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=True)
    
    # Relación con la tabla "guests"
    guest_id = db.Column(db.Integer, db.ForeignKey('guests.id', ondelete='CASCADE'), nullable=True)
    guest = db.relationship('Guest', back_populates='payment')
    
    @staticmethod
    def get_all():
        return Payment.query.all()

    @staticmethod
    def get_by_id(payment_id):
        return Payment.query.get(payment_id)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self, monto1=None, monto2=None, observaciones1=None, observaciones2=None, guest_id=None):
        if monto1 is not None:
            self.monto1 = monto1
        if monto2 is not None:
            self.monto2 = monto2
        if observaciones1 is not None:
            self.observaciones1 = observaciones1
        if observaciones2 is not None:
            self.observaciones2 = observaciones2
        if guest_id is not None:
            self.guest_id = guest_id
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        
    def serialize(self):
        return {
            'id': self.id,
            'monto1': self.monto1,
            'monto2': self.monto2,
            'observaciones1': self.observaciones1,
            'observaciones2': self.observaciones2,
            'fecha_registro': self.fecha_registro.isoformat(),
            'guest_id': self.guest_id  # Nuevo campo añadido
        }