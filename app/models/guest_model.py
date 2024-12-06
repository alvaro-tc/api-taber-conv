from extensions import db
from datetime import datetime

class Guest(db.Model):
    __tablename__ = 'guests'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(255), nullable=False)
    apellidos = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=True)
    telefono = db.Column(db.String(20), nullable=True)
    fecha_registro = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=False)
    
    # Relación con la tabla "positions"
    position_id = db.Column(db.Integer, db.ForeignKey('positions.id', ondelete='CASCADE'), nullable=False)
    position = db.relationship('Position', back_populates='guests')
    
    # Relación con la tabla "churchs"
    church_id = db.Column(db.Integer, db.ForeignKey('churchs.id', ondelete='CASCADE'), nullable=False)
    church = db.relationship('Church', back_populates='guests')

    
    event_details = db.relationship('EventDetail', back_populates='guest')
    
    
    @staticmethod
    def get_all():
        return Guest.query.all()

    @staticmethod
    def get_by_id(guest_id):
        return Guest.query.get(guest_id)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self, nombre, apellidos, email, telefono, position_id, church_id):
        self.nombre = nombre
        self.apellidos = apellidos
        self.email = email
        self.telefono = telefono
        self.position_id = position_id
        self.church_id = church_id
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        
    def serialize(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'apellidos': self.apellidos,
            'email': self.email,
            'telefono': self.telefono,
            'fecha_registro': self.fecha_registro.isoformat(),
            'position_id': self.position_id,
            'church_id': self.church_id
        }