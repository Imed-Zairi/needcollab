from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import secrets

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///needcollab.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# ── MODELS ────────────────────────────────────────────

collaborators = db.Table('collaborators',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('need_id', db.Integer, db.ForeignKey('need.id'))
)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), default='')
    password_hash = db.Column(db.String(200), nullable=False)
    token = db.Column(db.String(40), unique=True)
    bio = db.Column(db.Text, default='')
    location = db.Column(db.String(100), default='')
    date_joined = db.Column(db.DateTime, default=db.func.now())
    needs = db.relationship('Need', backref='creator', lazy=True, foreign_keys='Need.creator_id')
    joined_needs = db.relationship('Need', secondary=collaborators, backref='collaborators')


class Need(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())
    archived = db.Column(db.Boolean, default=False)
    offers = db.relationship('Offer', backref='need', lazy=True, cascade='all, delete')


class Offer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    need_id = db.Column(db.Integer, db.ForeignKey('need.id'), nullable=False)
    seller_name = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    description = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())
    votes = db.relationship('Vote', backref='offer', lazy=True, cascade='all, delete')


class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    offer_id = db.Column(db.Integer, db.ForeignKey('offer.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    choice = db.Column(db.String(10), nullable=False)
    __table_args__ = (db.UniqueConstraint('offer_id', 'user_id'),)


# ── HELPERS ───────────────────────────────────────────

def get_user_from_token():
    auth = request.headers.get('Authorization', '')
    if not auth.startswith('Token '):
        return None
    return User.query.filter_by(token=auth[6:]).first()


def require_auth():
    user = get_user_from_token()
    if not user:
        return None, jsonify({'error': 'Non authentifié.'}), 401
    return user, None, None


def serialize_offer(o):
    return {
        'id': o.id, 'need': o.need_id, 'seller_name': o.seller_name,
        'price': str(o.price), 'description': o.description,
        'created_at': o.created_at.isoformat(),
        'accept_count': sum(1 for v in o.votes if v.choice == 'accept'),
        'reject_count': sum(1 for v in o.votes if v.choice == 'reject'),
        'votes': [{'id': v.id, 'user': v.user_id, 'choice': v.choice} for v in o.votes],
    }


def serialize_need(n, full=True):
    d = {
        'id': n.id, 'title': n.title, 'description': n.description,
        'creator': n.creator.username, 'creator_id': n.creator_id,
        'collaborators_count': len(n.collaborators),
        'created_at': n.created_at.isoformat(),
        'archived': n.archived,
    }
    if full:
        d['offers'] = [serialize_offer(o) for o in n.offers]
    return d


# ── AUTH ──────────────────────────────────────────────

@app.post('/api/auth/register/')
def register():
    data = request.json
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': "Nom d'utilisateur déjà pris."}), 400
    token = secrets.token_hex(20)
    user = User(username=data['username'], email=data.get('email', ''),
                password_hash=generate_password_hash(data['password']), token=token)
    db.session.add(user)
    db.session.commit()
    return jsonify({'token': token, 'user_id': user.id, 'username': user.username})


@app.post('/api/auth/login/')
def login():
    data = request.json
    user = User.query.filter_by(username=data['username']).first()
    if not user or not check_password_hash(user.password_hash, data['password']):
        return jsonify({'error': 'Identifiants invalides.'}), 400
    return jsonify({'token': user.token, 'user_id': user.id, 'username': user.username})


# ── PROFILE ───────────────────────────────────────────

@app.get('/api/profile/')
def my_profile():
    user, err, code = require_auth()
    if err:
        return err, code
    return jsonify({
        'username': user.username, 'email': user.email, 'bio': user.bio,
        'location': user.location, 'date_joined': user.date_joined.isoformat(),
        'needs_count': len(user.needs), 'collabs_count': len(user.joined_needs),
    })


@app.route('/api/profile/update/', methods=['PATCH'])
def update_profile():
    user, err, code = require_auth()
    if err:
        return err, code
    data = request.json
    if 'username' in data:
        user.username = data['username']
    if 'email' in data:
        user.email = data['email']
    if 'bio' in data:
        user.bio = data['bio']
    if 'location' in data:
        user.location = data['location']
    db.session.commit()
    return jsonify({'username': user.username, 'email': user.email, 'bio': user.bio, 'location': user.location})


@app.get('/api/profile/needs/')
def profile_needs():
    user, err, code = require_auth()
    if err:
        return err, code
    needs = Need.query.filter_by(creator_id=user.id).order_by(Need.created_at.desc()).all()
    return jsonify([{
        'id': n.id, 'title': n.title, 'description': n.description,
        'created_at': n.created_at.isoformat(), 'archived': n.archived,
        'offers_count': len(n.offers), 'collaborators_count': len(n.collaborators),
    } for n in needs])


@app.get('/api/profile/collabs/')
def profile_collabs():
    user, err, code = require_auth()
    if err:
        return err, code
    return jsonify([{
        'id': n.id, 'title': n.title, 'description': n.description,
        'created_at': n.created_at.isoformat(),
        'offers_count': len(n.offers), 'collaborators_count': len(n.collaborators),
    } for n in user.joined_needs])


# ── NEEDS ─────────────────────────────────────────────

@app.get('/api/needs/')
def list_needs():
    needs = Need.query.order_by(Need.created_at.desc()).all()
    return jsonify([serialize_need(n) for n in needs])


@app.post('/api/needs/')
def create_need():
    user, err, code = require_auth()
    if err:
        return err, code
    data = request.json
    need = Need(title=data['title'], description=data['description'], creator_id=user.id)
    db.session.add(need)
    db.session.commit()
    return jsonify(serialize_need(need)), 201


@app.get('/api/needs/<int:pk>/')
def need_detail(pk):
    need = Need.query.get_or_404(pk)
    return jsonify(serialize_need(need))


@app.route('/api/needs/<int:pk>/', methods=['PATCH'])
def update_need(pk):
    user, err, code = require_auth()
    if err:
        return err, code
    need = Need.query.get_or_404(pk)
    if need.creator_id != user.id:
        return jsonify({'error': 'Non autorisé.'}), 403
    data = request.json
    if 'title' in data:
        need.title = data['title']
    if 'description' in data:
        need.description = data['description']
    db.session.commit()
    return jsonify(serialize_need(need))


@app.route('/api/needs/<int:pk>/', methods=['DELETE'])
def delete_need(pk):
    user, err, code = require_auth()
    if err:
        return err, code
    need = Need.query.get_or_404(pk)
    if need.creator_id != user.id:
        return jsonify({'error': 'Non autorisé.'}), 403
    db.session.delete(need)
    db.session.commit()
    return jsonify({'status': 'deleted'})


@app.post('/api/needs/<int:pk>/archive/')
def archive_need(pk):
    user, err, code = require_auth()
    if err:
        return err, code
    need = Need.query.get_or_404(pk)
    if need.creator_id != user.id:
        return jsonify({'error': 'Non autorisé.'}), 403
    need.archived = not need.archived
    db.session.commit()
    return jsonify({'archived': need.archived})


@app.post('/api/needs/<int:pk>/join/')
def join_need(pk):
    user, err, code = require_auth()
    if err:
        return err, code
    need = Need.query.get_or_404(pk)
    if user not in need.collaborators:
        need.collaborators.append(user)
        db.session.commit()
    return jsonify({'status': 'joined'})


# ── OFFERS ────────────────────────────────────────────

@app.get('/api/needs/<int:need_id>/offers/')
def list_offers(need_id):
    offers = Offer.query.filter_by(need_id=need_id).all()
    return jsonify([serialize_offer(o) for o in offers])


@app.post('/api/needs/<int:need_id>/offers/')
def create_offer(need_id):
    user, err, code = require_auth()
    if err:
        return err, code
    data = request.json
    offer = Offer(need_id=need_id, seller_name=data['seller_name'],
                  price=data['price'], description=data['description'])
    db.session.add(offer)
    db.session.commit()
    return jsonify(serialize_offer(offer)), 201


# ── VOTES ─────────────────────────────────────────────

@app.post('/api/offers/<int:offer_id>/vote/')
def vote_offer(offer_id):
    user, err, code = require_auth()
    if err:
        return err, code
    offer = Offer.query.get_or_404(offer_id)
    vote = Vote.query.filter_by(offer_id=offer_id, user_id=user.id).first()
    if vote:
        vote.choice = request.json['choice']
    else:
        vote = Vote(offer_id=offer_id, user_id=user.id, choice=request.json['choice'])
        db.session.add(vote)
    db.session.commit()
    return jsonify({'id': vote.id, 'user': vote.user_id, 'choice': vote.choice})


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
