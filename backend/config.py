import os


# ============================================
# BASE DIRECTORY
# ============================================

BASE_DIR = os.path.abspath(
    os.path.dirname(__file__)
)


# ============================================
# APPLICATION CONFIGURATION
# ============================================

class Config:

    SECRET_KEY = os.environ.get("SECRET_KEY")

    SQLALCHEMY_DATABASE_URI = (
        "sqlite:///"
        + os.path.join(
            BASE_DIR,
            "database.db"
        )
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False