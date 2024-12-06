from extensions import db

class Event(db.Model):
    __tablename__ = 'events'
    
    id = db.Column(db.Integer, primary_key=True)
    descripcion = db.Column(db.String(255), nullable=False)
    estado = db.Column(db.Integer, nullable=False)
    fecha = db.Column(db.DateTime, nullable=False)
    
    event_details = db.relationship('EventDetail', back_populates='event')

    @staticmethod
    def get_all():
        return Event.query.all()

    @staticmethod
    def get_by_id(event_id):
        return Event.query.get(event_id)

    def save(self):
        if self.estado == 0:
            existing_event = Event.query.filter_by(estado=0).first()
            if existing_event:
                raise ValueError("Ya existe un evento con estado 0")
        db.session.add(self)
        db.session.commit()

    def update(self, descripcion, estado, fecha):
        if estado == 0 and self.estado != 0:
            existing_event = Event.query.filter_by(estado=0).first()
            if existing_event:
                raise ValueError("Ya existe un evento con estado 0")
        self.descripcion = descripcion
        self.estado = estado
        self.fecha = fecha
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        
    def serialize(self):
        return {
            'id': self.id,
            'descripcion': self.descripcion,
            'estado': self.estado,
            'fecha': self.fecha.isoformat()
        }