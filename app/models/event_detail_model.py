from extensions import db
from datetime import datetime
from models.event_model import Event
from models.guest_model import Guest
from models.user_model import User
import pytz

class EventDetail(db.Model):
    __tablename__ = 'event_details'


    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    hora = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id', ondelete='CASCADE'), nullable=False)
    guest_id = db.Column(db.Integer, db.ForeignKey('guests.id', ondelete='CASCADE'), nullable=False)
    observaciones = db.Column(db.String(255), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)

    event = db.relationship('Event', back_populates='event_details')
    guest = db.relationship('Guest', back_populates='event_details')
    user = db.relationship('User', back_populates='event_details')


    @staticmethod
    def get_all():
        return EventDetail.query.all()

    @staticmethod
    def get_by_id(event_detail_id):
        return EventDetail.query.get(event_detail_id)
    
    @staticmethod
    def get_event_with_estado(estado):
        event = Event.query.filter_by(estado=estado).first()
        return event.id if event else None
    
    
   
    def save(self):
        if not Guest.query.get(self.guest_id):
            raise ValueError("El guest_id proporcionado no existe")
        if not User.query.get(self.user_id):
            raise ValueError("El user_id proporcionado no existe")
        
        # Verificar si ya existe un EventDetail con el mismo event_id y guest_id
        existing_event_detail = EventDetail.query.filter_by(event_id=self.event_id, guest_id=self.guest_id).first()
        if existing_event_detail:
            raise ValueError("Ya existe un EventDetail con el mismo event_id y guest_id")
        
        # Ajustar la hora a la zona horaria de Bolivia (UTC-4)
        bolivia_tz = pytz.timezone('America/La_Paz')
        self.hora = datetime.now(bolivia_tz)
        
        db.session.add(self)
        db.session.commit()
        
    def update(self, hora, event_id, guest_id, observaciones, user_id):
        if not Guest.query.get(guest_id):
            raise ValueError("El guest_id proporcionado no existe")
        if not User.query.get(user_id):
            raise ValueError("El user_id proporcionado no existe")
        
        # Verificar si ya existe un EventDetail con el mismo event_id y guest_id
        existing_event_detail = EventDetail.query.filter_by(event_id=event_id, guest_id=guest_id).first()
        if existing_event_detail and existing_event_detail.id != self.id:
            raise ValueError("Ya existe un EventDetail con el mismo event_id y guest_id")
        
        # Ajustar la hora a la zona horaria de Bolivia (UTC-4)
        bolivia_tz = pytz.timezone('America/La_Paz')
        self.hora = hora.astimezone(bolivia_tz)
        
        self.event_id = event_id
        self.guest_id = guest_id
        self.observaciones = observaciones
        self.user_id = user_id
        db.session.commit()
        
        
    def delete(self):
        db.session.delete(self)
        db.session.commit()
        
    def serialize(self):
        return {
            'id': self.id,
            'hora': self.hora.isoformat(),
            'event_id': self.event_id,
            'guest_id': self.guest_id,
            'observaciones': self.observaciones,
            'user_id': self.user_id
        }