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
    image_path = db.Column(db.String(200), default='/static/img/sets/default_set.png')  # Добавь эту строку
    user = db.relationship('User', backref='card_sets')



class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(100), nullable=False)
    translation = db.Column(db.String(100), nullable=False)
    card_set_id = db.Column(db.Integer, db.ForeignKey('card_set.id'), nullable=False)
    card_set = db.relationship('CardSet', backref='cards')


class ReadyCard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(100), nullable=False)
    translation = db.Column(db.String(100), nullable=False)
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
            session['user_id'] = user.id
            return redirect(f'/user/{user.login}/{user.id}')
        else:
            return "Неверный логин или пароль <a href='/login'>Попробовать снова</a>"

    # Форма входа
    return render_template('login.html')


@app.route('/user/<string:login>/<int:id>')
@app.route('/user/<string:login>/<int:id>')
def user_profile(login, id):
    if 'user' not in session:
        return "Сначала пройдите авторизацию <a href='/login'>Войти</a>"
    if session['user'] != login:
        return "Логин не совпадает <a href='/'>На главную</a>"
    user_card_sets = CardSet.query.filter_by(user_id=id).all()

    return render_template('user_page.html', login=login, card_sets=user_card_sets)

@app.route('/card')
def card():
    return render_template('card.html')


@app.route('/new_card')
def new_card():
    if 'user' not in session:
        return "Ты не авторизован<a href='/login'>Войди</a>"
    ready_sets = ReadyCardSet.query.all()

    return render_template('new_card.html', ready_sets=ready_sets)


@app.route('/add_set/<int:set_id>', methods=['POST'])
def add_set(set_id):
    if 'user' not in session:
        return "Сначала пройдите авторизацию <a href='/login'>Войти</a>"
    user_id = session.get('user_id')
    ready_set = ReadyCardSet.query.get(set_id)

    existing_set = CardSet.query.filter_by(
        name=ready_set.name,
        user_id=user_id
    ).first()

    if existing_set:
        return render_template('add_set_failure.html', set_name=ready_set.name)

    new_set = CardSet(
        name=ready_set.name,
        user_id=user_id,
        image_path=ready_set.image_path
    )
    db.session.add(new_set)
    db.session.commit()

    for ready_card in ready_set.cards:
        new_card = Card(
            word=ready_card.word,
            translation=ready_card.translation,
            card_set_id=new_set.id
        )
        db.session.add(new_card)

    db.session.commit()

    return render_template('add_set_success.html', set_name=ready_set.name)

def create_ready_sets():
    with app.app_context():
        animals_set = ReadyCardSet(
            name="Животные",
            description="Собаки, кошки и другие животные",
            image_path="/static/img/sets/animals.png"
        )
        db.session.add(animals_set)
        db.session.commit()
        animals = [
            ("dog", "собака"), ("cat", "кошка"), ("cow", "корова"),
            ("horse", "лошадь"), ("bird", "птица"), ("fish", "рыба")
        ]
        for word, trans in animals:
            card = ReadyCard(word=word, translation=trans, ready_set_id=animals_set.id)
            db.session.add(card)
        colors_set = ReadyCardSet(
            name="Цвета",
            description="Основные цвета радуги",
            image_path="/static/img/sets/colours.png"
        )
        db.session.add(colors_set)
        db.session.commit()

        colors = [("red", "красный"), ("blue", "синий"), ("green", "зелёный"),
                  ("yellow", "жёлтый"), ("black", "чёрный"), ("white", "белый")]
        for word, trans in colors:
            card = ReadyCard(word=word, translation=trans, ready_set_id=colors_set.id)
            db.session.add(card)
        food_set = ReadyCardSet(
            name="Еда",
            description="Продукты и блюда",
            image_path="/static/img/sets/food.png"
        )
        db.session.add(food_set)
        db.session.commit()

        food = [("apple", "яблоко"), ("bread", "хлеб"), ("water", "вода"),
                ("meat", "мясо"), ("soup", "суп"), ("cake", "торт")]
        for word, trans in food:
            card = ReadyCard(word=word, translation=trans, ready_set_id=food_set.id)
            db.session.add(card)

        db.session.commit()
        print("Готовые наборы с картинками созданы!")
# with app.app_context():
#      db.drop_all()
#      db.create_all()
#      create_ready_sets()
#      print("База данных пересоздана!")
def main():
    app.run(debug=True)

if __name__ == '__main__':
    main()