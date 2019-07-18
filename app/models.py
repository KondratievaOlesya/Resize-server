from app import db

READY = 1
NOT_READY = 0


class ImageRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    h = db.Column(db.Integer)
    w = db.Column(db.Integer)
    img_path = db.Column(db.String(100))
    status = db.Column(db.Integer, default=NOT_READY)

    def __repr__(self):
        return '<ImageRequest %r>' % (self.status)
