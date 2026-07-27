import os
from urllib.parse import quote_plus

from dotenv import load_dotenv
from flask import Flask, redirect, render_template, request, session, url_for
from sqlalchemy import inspect, text

from admin_routes import admin_bp
from config import Config
from i18n import babel, get_locale, normalize_locale
from models import Cottage, Hall, Photo, db


load_dotenv()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config["SQLALCHEMY_DATABASE_URI"] = get_database_url()

    db.init_app(app)
    babel.init_app(app, locale_selector=get_locale)
    app.register_blueprint(admin_bp)
    register_i18n_helpers(app)

    with app.app_context():
        db.create_all()
        ensure_multilingual_columns()
        seed_initial_data()

    return app


def get_database_url():
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return database_url

    mysql_host = os.getenv("MYSQL_HOST")
    mysql_database = os.getenv("MYSQL_DATABASE")
    mysql_user = os.getenv("MYSQL_USER")
    mysql_password = os.getenv("MYSQL_PASSWORD", "")
    mysql_port = os.getenv("MYSQL_PORT", "3306")

    if mysql_host and mysql_database and mysql_user:
        password = quote_plus(mysql_password)
        return (
            f"mysql+pymysql://{mysql_user}:{password}@"
            f"{mysql_host}:{mysql_port}/{mysql_database}?charset=utf8mb4"
        )

    return "sqlite:///vodogray.db"


def register_i18n_helpers(app):
    @app.before_request
    def store_selected_language():
        lang = request.args.get("lang")
        if lang:
            session["lang"] = normalize_locale(lang)

    @app.context_processor
    def inject_i18n():
        def language_url(lang):
            args = request.args.to_dict()
            view_args = request.view_args or {}
            args["lang"] = lang
            return url_for(request.endpoint or "index", **view_args, **args)

        return {
            "current_language": get_locale(),
            "supported_languages": app.config["BABEL_SUPPORTED_LOCALES"],
            "language_url": language_url,
        }

    @app.route("/set-language/<lang>")
    def set_language(lang):
        session["lang"] = normalize_locale(lang)
        next_url = request.args.get("next") or url_for("index")
        return redirect(next_url)


def seed_initial_data():
    if Cottage.query.first() or Hall.query.first():
        return

    cottage = Cottage(
        name="Стандартний номер",
        name_uk="Стандартний номер",
        name_en="Standard Room",
        description="Затишний номер з усім необхідним для комфортного відпочинку.",
        description_uk="Затишний номер з усім необхідним для комфортного відпочинку.",
        description_en="A cozy room with everything needed for a comfortable stay.",
        price=1800,
        capacity=2,
        features="\n".join(
            [
                "Двоспальне ліжко",
                "Wi-Fi",
                "Кондиціонер",
                "Рушники",
                "Телевізор",
                "Тераса",
                "Ванна кімната",
                "Душ",
                "Робочий стіл",
                "Фен",
            ]
        ),
        features_uk="\n".join(
            [
                "Двоспальне ліжко",
                "Wi-Fi",
                "Кондиціонер",
                "Рушники",
                "Телевізор",
                "Тераса",
                "Ванна кімната",
                "Душ",
                "Робочий стіл",
                "Фен",
            ]
        ),
        features_en="\n".join(
            [
                "Double bed",
                "Wi-Fi",
                "Air conditioning",
                "Towels",
                "TV",
                "Terrace",
                "Bathroom",
                "Shower",
                "Work desk",
                "Hair dryer",
            ]
        ),
    )
    hall = Hall(
        name="Великий зал",
        name_uk="Великий зал",
        name_en="Large Hall",
        description="Простора бенкетна зала для свят, зустрічей та родинних подій.",
        description_uk="Простора бенкетна зала для свят, зустрічей та родинних подій.",
        description_en="A spacious banquet hall for celebrations, meetings, and family events.",
        price=1800,
        capacity=100,
        booking_from="09 липня 2026",
        features="\n".join(
            [
                "До 100 осіб",
                "Сцена та танцпол",
                "Фотозона",
                "Спеціальні меню",
            ]
        ),
        features_uk="\n".join(
            [
                "До 100 осіб",
                "Сцена та танцпол",
                "Фотозона",
                "Спеціальні меню",
            ]
        ),
        features_en="\n".join(
            [
                "Up to 100 guests",
                "Stage and dance floor",
                "Photo zone",
                "Special menus",
            ]
        ),
    )

    db.session.add_all([cottage, hall])
    db.session.flush()
    db.session.add_all(
        [
            Photo(image_url="/static/img/vodogray.png", alt_text="Водограй", cottage_id=cottage.id, sort_order=1),
            Photo(image_url="/static/img/retro_bell.png", alt_text="Готель", cottage_id=cottage.id, sort_order=2),
            Photo(image_url="/static/img/retro_coffe.png", alt_text="Кафе", cottage_id=cottage.id, sort_order=3),
            Photo(image_url="/static/img/vodogray.png", alt_text="Бенкетна зала", hall_id=hall.id, sort_order=1),
            Photo(image_url="/static/img/retro_bell.png", alt_text="Зала", hall_id=hall.id, sort_order=2),
            Photo(image_url="/static/img/retro_coffe.png", alt_text="Кафе", hall_id=hall.id, sort_order=3),
        ]
    )
    db.session.commit()


def ensure_multilingual_columns():
    inspector = inspect(db.engine)
    dialect = db.engine.dialect.name
    table_columns = {
        table: {column["name"] for column in inspector.get_columns(table)}
        for table in ("cottages", "halls")
    }

    columns = {
        "name_uk": "VARCHAR(150)",
        "name_en": "VARCHAR(150)",
        "description_uk": "TEXT",
        "description_en": "TEXT",
        "features_uk": "TEXT",
        "features_en": "TEXT",
    }

    with db.engine.begin() as connection:
        for table, existing_columns in table_columns.items():
            for column_name, column_type in columns.items():
                if column_name not in existing_columns:
                    connection.execute(text(f"ALTER TABLE {table} ADD COLUMN {column_name} {column_type} NULL"))

            connection.execute(
                text(
                    f"""
                    UPDATE {table}
                    SET
                        name_uk = COALESCE(name_uk, name),
                        description_uk = COALESCE(description_uk, description),
                        features_uk = COALESCE(features_uk, features)
                    """
                )
            )

    if dialect == "sqlite":
        db.session.remove()


app = create_app()


@app.route("/")
def index():
    cottages = Cottage.query.filter_by(is_active=True).order_by(Cottage.id.asc()).all()
    halls = Hall.query.filter_by(is_active=True).order_by(Hall.id.asc()).all()
    return render_template("index.html", cottages=cottages, halls=halls)


if __name__ == "__main__":
    app.run(debug=True)
