from flask_shop import app


class Product(app.db.Model):
    __tablename__ = 'product_product'
    id = app.db.Column(app.db.Integer, primary_key=True)
    #name = app.db.Column(app.db.String(64), unique=False)
    code = app.db.Column(app.db.String(64), unique=False)
    description = app.db.Column(app.db.String(64), unique=False)
    #list_price = app.db.Column(app.db.Numeric, unique=False)
    attributes = app.db.Column(app.db.Text, unique=False)
    #categories = db.relationship('product.category', lazy='dynamic')

    def __repr__(self):
        return '<Product %r>' % self.id


class User():
    id = None
    nickname = None
    email = None
    posts = None

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        try:
            return unicode(self.id)  # python 2
        except NameError:
            return str(self.id)  # python 3

    def __repr__(self):
        return '<User %r>' % (self.nickname)