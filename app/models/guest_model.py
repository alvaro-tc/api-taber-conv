from app.extensions import db
from datetime import datetime

class Guest(db.Model):
    __tablename__ = 'guests'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(255), nullable=False)
    apellidos = db.Column(db.String(255), nullable=True)
    email = db.Column(db.String(255), nullable=True)
    telefono = db.Column(db.String(20), nullable=True)
    fecha_registro = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=True)
    code = db.Column(db.Integer, unique=True, nullable=True)  # Nuevo campo añadido
    
    # Relación con la tabla "positions"
    position_id = db.Column(db.Integer, db.ForeignKey('positions.id', ondelete='CASCADE'), nullable=True)
    position = db.relationship('Position', back_populates='guests')
    
    # Relación con la tabla "churchs"
    church_id = db.Column(db.Integer, db.ForeignKey('churchs.id', ondelete='CASCADE'), nullable=True)
    church = db.relationship('Church', back_populates='guests')
    
    # Relación con la tabla "directives"
    directive_id = db.Column(db.Integer, db.ForeignKey('directives.id', ondelete='CASCADE'), nullable=True)
    directive = db.relationship('Directive', back_populates='guests')

    
    
    event_details = db.relationship('EventDetail', back_populates='guest')
    payments_made = db.relationship('Payment', foreign_keys='Payment.id_payer', back_populates='payer')
    payments_received = db.relationship('Payment', foreign_keys='Payment.id_guest', back_populates='guest')
    
    
    
    @staticmethod
    def get_all():
        return Guest.query.all()

    @staticmethod
    def get_by_id(guest_id):
        return Guest.query.get(guest_id)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update_code (self, code):
        if code is not None:
            self.code = code
        db.session.commit()
        
    def update(self, church_id, directive_id, nombre=None, apellidos=None, email=None, telefono=None, position_id=None, code=None):
        if nombre is not None:
            self.nombre = nombre
        if apellidos is not None:
            self.apellidos = apellidos
        if email is not None:
            self.email = email
        if telefono is not None:
            self.telefono = telefono
        if position_id is not None:
            self.position_id = position_id
        self.church_id = church_id
        self.directive_id = directive_id
        if code is not None:
            self.code = code
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
            'church_id': self.church_id,
            'directive_id': self.directive_id,
            'code': self.code  # Nuevo campo añadido
        }