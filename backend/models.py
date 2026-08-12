from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


# ============================================
# Database
# ============================================

db = SQLAlchemy()


# ============================================
# User Table
# ============================================

class User(db.Model):

    __tablename__ = "users"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100),
        nullable=False
    )

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )

    phone = db.Column(
        db.String(15),
        nullable=False
    )

    password = db.Column(
        db.String(255),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    # One User can upload many Books
    books = db.relationship(
        "Book",
        backref="seller",
        lazy=True
    )


# ============================================
# Book Table
# ============================================

class Book(db.Model):

    __tablename__ = "books"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    title = db.Column(
        db.String(200),
        nullable=False
    )

    author = db.Column(
        db.String(150),
        nullable=False
    )

    category = db.Column(
        db.String(100),
        nullable=False
    )

    price = db.Column(
        db.Float,
        nullable=False
    )

    condition = db.Column(
        db.String(50),
        nullable=False
    )

    description = db.Column(
        db.Text
    )

    image = db.Column(
        db.String(255),
        default="default.jpg"
    )

    seller_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )
    
# ============================================
# Cart Table
# ============================================

class Cart(db.Model):

    __tablename__ = "cart"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    book_id = db.Column(
        db.Integer,
        db.ForeignKey("books.id"),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    # Relationships
    user = db.relationship(
        "User",
        backref=db.backref(
            "cart_items",
            lazy=True
        )
    )

    book = db.relationship(
        "Book",
        backref=db.backref(
            "cart_items",
            lazy=True
        )
    )