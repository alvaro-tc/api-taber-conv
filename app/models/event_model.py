from app.extensions import db

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
        if self._is_duplicate_event(self.estado, self.descripcion):
            raise ValueError("Ya existe un evento con estado 0 y la misma descripción")
        db.session.add(self)
        db.session.commit()

    def update(self, descripcion, estado, fecha):
        if self._is_duplicate_event(estado, descripcion):
            raise ValueError("Ya existe un evento con estado 0 y la misma descripción")
        self.descripcion = descripcion
        self.estado = estado
        self.fecha = fecha
        db.session.commit()

    def _is_duplicate_event(self, estado, descripcion):
        estado_no_rep = ["Asistencia Mañana", "Asistencia Tarde", "Cena", "Almuerzo", "Desayuno", "Refrigerio", "Merienda"]
        if estado == 0 and descripcion in estado_no_rep:
            existing_event = Event.query.filter_by(estado=0).filter(Event.descripcion.in_(estado_no_rep)).first()
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
            'fecha': self.fecha.isoformat()
        }