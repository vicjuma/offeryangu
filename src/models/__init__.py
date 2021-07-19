import hashlib
from src import db, loginmanager
import datetime
from flask_login import UserMixin
from itsdangerous import URLSafeTimedSerializer
from flask import current_app, request
import bleach
from markdown import markdown

followerstable = db.Table(
    "linktable",
    db.Column(
        'follower_id', db.Integer, db.ForeignKey('user.id'),
        nullable=False),
    db.Column(
        'following_id', db.Integer, db.ForeignKey('user.id'),
        nullable=False)
)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False, unique=True)
    password = db.Column(db.String(200))
    phone = db.Column(db.String(200), nullable=False)
    subscribed = db.Column(db.Boolean, default=False)
    is_super = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)
    product_owned = db.relationship(
        'Product', backref='needs', lazy='dynamic',
        cascade="all, delete-orphan")
    user_img = db.Column(db.String(200), nullable=False, default='default.png')
    confirmed = db.Column(db.Boolean, default=False)
    followed = db.relationship(
        'User',
        secondary=followerstable,
        primaryjoin=(followerstable.c.follower_id == id),
        secondaryjoin=(followerstable.c.following_id == id),
        backref=db.backref('followerstable', lazy="dynamic"),
        lazy='dynamic')
    messages_id = db.relationship(
        'Messages', backref='messages', lazy='dynamic',
        cascade="all, delete-orphan")
    last_seen = db.Column(
        db.DateTime, default=datetime.datetime.utcnow)
    external = db.relationship(
        'Recepient', lazy='dynamic', backref='recepient',
        cascade="all, delete-orphan")
    userrev = db.relationship(
        'Reviews', lazy='dynamic', backref='reviews',
        cascade="all, delete-orphan")
    userlike = db.relationship(
        'Likes', lazy='dynamic', backref='likes',
        cascade="all, delete-orphan")

    def __repr__(self):
        return '%d' % self.id

    def is_following(self, user: str):
        user = User.query.filter_by(name=user).first()
        return self.followed.filter(
            followerstable.c.following_id == user.id).count() > 0

    # get the product form the followed user
    def followed_products(self):
        return Product.query.join(
            followerstable,
            (followerstable.c.following_id == Product.owner_id)).filter(
                followerstable.c.follower_id == self.id).order_by(
                    Product.date_created.desc()).all()

    def unfollow(self, user):
        if self.is_following(user.name):
            self.followed.remove(user)
            db.session.commit()

    def follow(self, user):
        if not self.is_following(user.name):
            self.followed.append(user)
            db.session.commit()

    @loginmanager.user_loader
    def user_loader(id):
        return User.query.get(int(id))

    def get_reset_password_token(self):
        serializer = URLSafeTimedSerializer(current_app.secret_key)
        return serializer.dumps(self.id, salt=current_app.secret_key)

    def generate_gravatar(self, s=80, d='identicon'):
        if request.is_secure:
            url = 'https://www.gravatar.com/avatar/'
        else:
            url = 'http://www.gravatar.com/avatar/'
        hsh = hashlib.md5(self.email.encode('utf-8')).hexdigest()
        return f'{url}{hsh}?s={s}&d={d}'


class Product(db.Model):
    __searchable__ = ['name', 'location', 'category']
    __tablename__ = "product"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Integer)
    market_price = db.Column(db.Integer, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    date_ending = db.Column(db.DateTime)
    description = db.Column(db.Text)
    description_html = db.Column(db.Text)
    category = db.Column(db.String(200), default=None)
    subcategory = db.Column(db.String(200), default=None)
    photo = db.relationship(
        'Picture', backref='photos', lazy='dynamic',
        cascade="all, delete-orphan")
    path_1 = db.Column(db.String(200))
    path_2 = db.Column(db.String(200))
    is_deleted = db.Column(db.Boolean, default=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    prodrev = db.relationship(
        'Reviews', lazy='dynamic', backref='productr',
        cascade="all, delete-orphan")
    prodlik = db.relationship(
        'Likes', lazy='dynamic', backref='productl',
        cascade="all, delete-orphan")
    stock = db.Column(db.Integer, nullable=False, default=1)

    def __repr__(self):
        return '%s' % self.name

    def to_json(self):
        return {
            "name": self.name,
            "price": self.price,
            "id": self.id
        }

    @staticmethod
    def on_description_change(target, value, oldvalue, initiator):
        allowed_tags = [
            "h1", "h2", "p", "a", "blockquote", "br", "span", "div",
            "h3", "ul", "li", "tr", "td", "tbody", "table"]
        target.description_html = bleach.linkify(
            bleach.clean(markdown(
                value, output_format='html'), tags=allowed_tags, strip=True))


db.event.listen(Product.description, 'set', Product.on_description_change)


class Picture(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.String(200), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))

    def __repr__(self) -> str:
        return '%d' % self.id


class Subcategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subcategory_name = db.Column(db.String(200), nullable=False)
    category_name = db.Column(db.String(200), nullable=False)

    def __repr__(self) -> str:
        return '%s' % self.category_name


# likes for the product
class Likes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    likescount = db.Column(db.Integer, default=0)
    product_id = db.Column(
        db.Integer, db.ForeignKey('product.id'), nullable=False)
    user_id = db.Column(
        db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return '<%s>' % self.likescount


# reviews table
class Reviews(db.Model):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    message = db.Column(db.Text, nullable=False)
    message_html = db.Column(db.Text)
    creator_id = db.Column(db.Integer, db.ForeignKey('product.id'))

    def __repr__(self):
        return '<%s>' % self.id

    @staticmethod
    def on_post_change(target, value, oldvalue, initiator):
        tags = ["p", "h4", "a"]
        target.message_html = bleach.linkify(
            bleach.clean(markdown(
                value, output_format='html'), tags=tags, strip=True))


db.event.listen(Reviews.message, 'set', Reviews.on_post_change)


class Messages(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text, nullable=False)
    sender_id = db.Column(
        db.Integer, db.ForeignKey('user.id'), nullable=False)
    date_created = db.Column(
        db.DateTime, default=datetime.datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)
    code1 = db.Column(db.String(200), nullable=False)
    external = db.relationship(
        'Recepient', lazy='dynamic', backref='code',
        cascade="all, delete-orphan")

    def __repr__(self):
        return' <sender id %s>' % self.sender_id


class Recepient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    recepient_id = db.Column(
        db.Integer, db.ForeignKey('user.id'), nullable=False)
    code2 = db.Column(db.String(200), db.ForeignKey('messages.code1'))

    def __repr__(self):
        return' <%s>' % self.name
