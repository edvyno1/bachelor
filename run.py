from api import app
from database.database import db
from waitress import serve
import sys


def run(database_uri):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_uri
    db.init_app(app)

    with app.app_context():
        db.create_all()
    serve(app, host="0.0.0.0", port=5000, url_scheme="https")


def run_test():
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
    db.init_app(app)
    with app.app_context():
        db.create_all()
    app.run()


def main():
    args = sys.argv[1]
    if args == "main":
        run("sqlite:///database.db")
    elif args == "test":
        run_test()


if __name__ == "__main__":
    main()
