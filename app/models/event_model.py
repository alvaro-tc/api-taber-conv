from app.extensions import db

class Event(db.Model):
    __tablename__ = 'events'
    
    id = db.Column(db.Integer, primary_key=True)
    descripcion = db.Column(db.String(255), nullable=False)
    estado = db.Column(db.Integer, nullable=False)
    fecha = db.Column(db.DateTime, nullable=False)
    qr_available = db.Column(db.Boolean, default=False)
    
    event_details = db.relationship('EventDetail', back_populates='event')

    @staticmethod
    def get_all():
        return Event.query.all()

    @staticmethod
    def get_by_id(event_id):
        return Event.query.get(event_id)

    def save(self):
        if self._is_duplicate_event(self.estado):
            raise ValueError("Ya existe un evento con estado 0 y la misma descripción")
        db.session.add(self)
        db.session.commit()

    def update(self, descripcion, estado, fecha, qr_available):
        if self._is_duplicate_event(estado):
            raise ValueError("Ya existe un evento con estado 0 y la misma descripción")
        self.descripcion = descripcion
        self.estado = estado
        self.fecha = fecha
        self.qr_available = qr_available
        db.session.commit()
        
        
    def _is_duplicate_event(self, estado):
        if estado == 0 and self.qr_available:
            existing_event = Event.query.filter_by(estado=0).first()
            if existing_event:
                return True
        return False

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        
    def serialize(self):
        return {
            'id': self.id,
            'descripcion': self.descripcion,
            'estado': self.estado,
            'fecha': self.fecha.isoformat(),
            'qr_available': self.qr_available
        }