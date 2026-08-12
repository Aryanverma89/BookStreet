from flask import Flask
from dotenv import load_dotenv

from config import Config
from models import db
from routes import register_routes

load_dotenv()

# ============================================
# CREATE APPLICATION
# ============================================

def create_app():

    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static"
    )

    

    # Load configuration
    app.config.from_object(Config)

    # Initialize database
    db.init_app(app)

    # Create database tables
    with app.app_context():
        db.create_all()

    # Register application routes
    register_routes(app)

    return app


# ============================================
# APPLICATION
# ============================================

app = create_app()


# ============================================
# RUN APPLICATION
# ============================================

if __name__ == "__main__":
    app.run(debug=True)