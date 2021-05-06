from flask.cli import FlaskGroup

from mltrace.server import app


cli = FlaskGroup(app, static_folder=".ui/build")


if __name__ == "__main__":
    cli()
