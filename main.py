from flask import Flask, render_template, redirect, url_for, request, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)


class CardSet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref='card_sets')


class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    word_eng = db.Column(db.String(100), nullable=False)
    word_rus = db.Column(db.String(100), nullable=False)
    card_set_id = db.Column(db.Integer, db.ForeignKey('card_set.id'), nullable=False)
    card_set = db.relationship('CardSet', backref='cards')


class ReadyCard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    word_eng = db.Column(db.String(100), nullable=False)
    word_rus = db.Column(db.String(100), nullable=False)
    ready_set_id = db.Column(db.Integer, db.ForeignKey('ready_card_set.id'), nullable=False)

    ready_set = db.relationship('ReadyCardSet', backref='cards')


class ReadyCardSet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))
    image_path = db.Column(db.String(200), default='/img/sets/default_set.png')


@app.route('/')
def index():
    return render_template('main_page.html')


@app.route('/odd_even')
def odd_even():
    return render_template('odd_even.html', number=2)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        login = request.form.get('login')
        password = request.form.get('password')
        existing_user = User.query.filter_by(login=login).first()
        if existing_user:
            return "Такой логин уже существует <a href='/register'>Назад</a>"
        hashed_password = generate_password_hash(password)

        new_user = User(login=login, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return "Регистрация успешна <a href='/login'>Войти</a>"
    return render_template('registration.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login = request.form.get('login')
        password = request.form.get('password')
        user = User.query.filter_by(login=login).first()
        if user and check_password_hash(user.password, password):
            session['user'] = login
            return redirect(f'/user/{user.login}/{user.id}')
        else:
            return "Неверный логин или пароль <a href='/login'>Попробовать снова</a>"

    return render_template('login.html')


@app.route('/user/<string:login>/<int:id>')
def user_profile(login, id):
    if 'user' not in session or session['user'] != login:
        return redirect(url_for('login'))

    user_card_sets = CardSet.query.filter_by(user_id=id).all()

    # Передаем их в шаблон под именем card_sets
    return render_template('user_page.html', login=login, card_sets=user_card_sets)


@app.route('/card')
def card():
    return render_template('card.html')


@app.route('/new_card', methods=['GET', 'POST'])
def new_card():
    if 'user' not in session:
        return redirect(url_for('login'))
    ready_sets = ReadyCardSet.query.all()
    if request.method == 'POST':
        return redirect(f'/add_set/{request.form.get('set_id')}')
    return render_template('new_card.html', ready_sets=ready_sets)

@app.route('/add_set/<int:set_id>')
def add_set(set_id):
    if 'user' not in session:
        return redirect(url_for('login'))

    user = User.query.filter_by(login=session['user']).first()
    ready_set = ReadyCardSet.query.get(set_id)

    new_user_set = CardSet(name=ready_set.name, user_id=user.id)
    db.session.add(new_user_set)
    db.session.flush()

    for rc in ready_set.cards:
        new_card = Card(
            word_eng=rc.word_eng,
            word_rus=rc.word_rus,
            card_set_id=new_user_set.id
        )
        db.session.add(new_card)

    db.session.commit()
    return redirect(url_for('user_profile', login=user.login, id=user.id))


def main():
    app.run(debug=True)

if __name__ == '__main__':
    main()