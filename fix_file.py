from flask import Flask, render_template, redirect, url_for, request, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash



def create_ready_sets():
    """Создаёт готовые наборы карточек (вызови один раз)"""
    with app.app_context():
        # Набор "Животные"
        animals_set = ReadyCardSet(
            name="Животные",
            description="Собаки, кошки и другие животные",
            image_path="/static/img/sets/animals.png"  # Было .jpg, стало .png
        )
        db.session.add(animals_set)
        db.session.commit()

        # Карточки для "Животные"
        animals = [
            ("dog", "собака"), ("cat", "кошка"), ("cow", "корова"),
            ("horse", "лошадь"), ("bird", "птица"), ("fish", "рыба")
        ]
        for word, trans in animals:
            card = ReadyCard(word=word, translation=trans, ready_set_id=animals_set.id)
            db.session.add(card)

        # Набор "Цвета" (обрати внимание - colours.png, а не colors.jpg)
        colors_set = ReadyCardSet(
            name="Цвета",
            description="Основные цвета радуги",
            image_path="/static/img/sets/colours.png"  # colours.png (с u)
        )
        db.session.add(colors_set)
        db.session.commit()

        colors = [("red", "красный"), ("blue", "синий"), ("green", "зелёный"),
                  ("yellow", "жёлтый"), ("black", "чёрный"), ("white", "белый")]
        for word, trans in colors:
            card = ReadyCard(word=word, translation=trans, ready_set_id=colors_set.id)
            db.session.add(card)

        # Набор "Еда"
        food_set = ReadyCardSet(
            name="Еда",
            description="Продукты и блюда",
            image_path="/static/img/sets/food.png"  # Было .jpg, стало .png
        )
        db.session.add(food_set)
        db.session.commit()

        food = [("apple", "яблоко"), ("bread", "хлеб"), ("water", "вода"),
                ("meat", "мясо"), ("soup", "суп"), ("cake", "торт")]
        for word, trans in food:
            card = ReadyCard(word=word, translation=trans, ready_set_id=food_set.id)
            db.session.add(card)

        db.session.commit()
        print("✅ Готовые наборы с картинками созданы!")