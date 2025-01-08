from app.extensions import db
from datetime import datetime
from app.models.event_model import Event
from app.models.guest_model import Guest
from app.models.user_model import User
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
        event = Event.query.filter_by(estado=estado, qr_available=True).first()
        return event.id if event else None
        
    
   
    def save(self):
        if not Guest.query.get(self.guest_id):
            raise ValueError("El usuario proporcionado no existe")
        if not User.query.get(self.user_id):
            raise ValueError("El usuario (registrador) proporcionado no existe")
        
        # Verificar si ya existe un EventDetail con el mismo event_id y guest_id
        existing_event_detail = EventDetail.query.filter_by(event_id=self.event_id, guest_id=self.guest_id).first()
        if existing_event_detail:
            event = Event.query.get(existing_event_detail.event_id)
            guest = Guest.query.get(existing_event_detail.guest_id)
            nombre_completo = f"{guest.nombre} {guest.apellidos}" if guest else "anonimo"
            descripcion = event.descripcion
            
            raise ValueError(nombre_completo+ " ya está registrado en el evento: " + descripcion)
        
        # Ajustar la hora a la zona horaria de Bolivia (UTC-4)
        bolivia_tz = pytz.timezone('America/La_Paz')
        self.hora = datetime.now(bolivia_tz)
        
        db.session.add(self)
        db.session.commit()
        
    def update(self, hora=None, event_id=None, guest_id=None, observaciones=None, user_id=None):
        if guest_id and not Guest.query.get(guest_id):
            raise ValueError("El guest_id proporcionado no existe")
        if user_id and not User.query.get(user_id):
            raise ValueError("El user_id proporcionado no existe")
        
        # Verificar si ya existe un EventDetail con el mismo event_id y guest_id
        if event_id and guest_id:
            existing_event_detail = EventDetail.query.filter_by(event_id=event_id, guest_id=guest_id).first()
            if existing_event_detail and existing_event_detail.id != self.id:
                event = Event.query.get(existing_event_detail.event_id)
                guest = Guest.query.get(existing_event_detail.guest_id)
                nombre_completo = f"{guest.nombre} {guest.apellidos}" if guest else "anonimo"
                descripcion = event.descripcion
                
                raise ValueError(nombre_completo + " ya fue registrado en el evento: " + descripcion + " a las " + existing_event_detail.hora.isoformat())
        
        # Ajustar la hora a la zona horaria de Bolivia (UTC-4)
        if hora:
            bolivia_tz = pytz.timezone('America/La_Paz')
            self.hora = hora.astimezone(bolivia_tz)
        
        if event_id:
            self.event_id = event_id
        if guest_id:
            self.guest_id = guest_id
        if observaciones is not None:
            self.observaciones = observaciones
        if user_id:
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