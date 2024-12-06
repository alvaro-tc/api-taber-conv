from extensions import db

class Position(db.Model):
    __tablename__ = 'positions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    descripcion = db.Column(db.String(100), nullable=False)
    
    guests = db.relationship('Guest', back_populates='position')

    @staticmethod
    def get_all():
        return Position.query.all()

    @staticmethod
    def get_by_id(position_id):
        return Position.query.get(position_id)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self, descripcion):
        self.descripcion = descripcion
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        
    def serialize(self):
        return {
            'id': self.id,
            'descripcion': self.descripcion
        }