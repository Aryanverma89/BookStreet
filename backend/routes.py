# ============================================
# BookStreet - Routes
# ============================================

import os

from flask import (
    request,
    jsonify,
    render_template,
    session,
    redirect
)

from models import db, User, Book, Cart

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from werkzeug.utils import secure_filename


# ============================================
# Register All Routes
# ============================================

def register_routes(app):

    # ============================================
    # HOME PAGE
    # ============================================

    @app.route("/")
    def home():

        return render_template(
            "index.html"
        )


    # ============================================
    # REGISTER PAGE
    # ============================================

    @app.route("/register-page")
    def register_page():

        return render_template(
            "register.html"
        )


    # ============================================
    # LOGIN PAGE
    # ============================================

    @app.route("/login-page")
    def login_page():

        return render_template(
            "login.html"
        )


    # ============================================
    # USER REGISTRATION
    # ============================================

    @app.route("/register", methods=["POST"])
    def register():

        data = request.get_json(silent=True) or {}

        name = data.get("name")
        email = data.get("email")
        phone = data.get("phone")
        password = data.get("password")

        if not name or not email or not password:

            return jsonify({
                "success": False,
                "message": "Please fill all required fields."
            }), 400


        existing_user = User.query.filter_by(
            email=email
        ).first()


        if existing_user:

            return jsonify({
                "success": False,
                "message": "Email already exists."
            }), 400


        hashed_password = generate_password_hash(
            password
        )


        user = User(
            name=name,
            email=email,
            phone=phone,
            password=hashed_password
        )


        db.session.add(user)
        db.session.commit()


        return jsonify({
            "success": True,
            "message": "User Registered Successfully."
        })


    # ============================================
    # USER LOGIN
    # ============================================

    @app.route("/login", methods=["POST"])
    def login():

        # Support normal form data
        email = request.form.get("email")
        password = request.form.get("password")


        # Support JSON data
        if not email or not password:

            data = request.get_json(
                silent=True
            ) or {}

            email = data.get("email")
            password = data.get("password")


        if not email or not password:

            return jsonify({
                "success": False,
                "message": "Email and password are required."
            }), 400


        # Find user
        user = User.query.filter_by(
            email=email
        ).first()


        if not user:

            return jsonify({
                "success": False,
                "message": "Email not found."
            }), 404


        # Check password
        if not check_password_hash(
            user.password,
            password
        ):

            return jsonify({
                "success": False,
                "message": "Incorrect Password."
            }), 401


        # ========================================
        # SAVE USER SESSION
        # ========================================

        session["user_id"] = user.id
        session["user_name"] = user.name


        # ========================================
        # LOGIN SUCCESS
        # GO TO HOME PAGE
        # ========================================

        return redirect("/home")


    # ============================================
    # CART PAGE
    # ============================================

    @app.route("/cart")
    def cart():

        if "user_id" not in session:

            return redirect(
                "/login-page"
            )


        cart_items = Cart.query.filter_by(
            user_id=session["user_id"]
        ).all()


        total = sum(
            item.book.price
            for item in cart_items
            if item.book
        )


        return render_template(
            "cart.html",
            cart_items=cart_items,
            total=total
        )


    # ============================================
    # ADD TO CART
    # ============================================

    @app.route(
        "/add-to-cart/<int:book_id>",
        methods=["POST"]
    )
    def add_to_cart(book_id):

        if "user_id" not in session:

            return jsonify({
                "success": False,
                "message": "Please login first."
            }), 401


        book = Book.query.get_or_404(
            book_id
        )


        # Prevent seller from adding own book
        if book.seller_id == session["user_id"]:

            return jsonify({
                "success": False,
                "message": "You cannot add your own book to cart."
            }), 400


        # Check existing cart item
        existing_item = Cart.query.filter_by(
            user_id=session["user_id"],
            book_id=book_id
        ).first()


        if existing_item:

            return jsonify({
                "success": False,
                "message": "Book is already in your cart."
            }), 400


        cart_item = Cart(
            user_id=session["user_id"],
            book_id=book_id
        )


        db.session.add(cart_item)
        db.session.commit()


        return jsonify({
            "success": True,
            "message": "Book added to cart."
        })


    # ============================================
    # REMOVE FROM CART
    # ============================================

    @app.route(
        "/remove-from-cart/<int:book_id>",
        methods=["POST"]
    )
    def remove_from_cart(book_id):

        if "user_id" not in session:

            return jsonify({
                "success": False,
                "message": "Please login first."
            }), 401


        cart_item = Cart.query.filter_by(
            user_id=session["user_id"],
            book_id=book_id
        ).first()


        if not cart_item:

            return jsonify({
                "success": False,
                "message": "Book not found in cart."
            }), 404


        db.session.delete(cart_item)
        db.session.commit()


        return jsonify({
            "success": True,
            "message": "Book removed from cart."
        })


    # ============================================
    # CLEAR CART
    # ============================================

    @app.route(
        "/clear-cart",
        methods=["POST"]
    )
    def clear_cart():

        if "user_id" not in session:

            return jsonify({
                "success": False,
                "message": "Please login first."
            }), 401


        Cart.query.filter_by(
            user_id=session["user_id"]
        ).delete()


        db.session.commit()


        return jsonify({
            "success": True,
            "message": "Cart cleared."
        })


    # ============================================
    # DASHBOARD
    # ============================================

    @app.route("/dashboard")
    def dashboard():

        if "user_id" not in session:

            return redirect(
                "/login-page"
            )


        return render_template(
            "dashboard.html",
            name=session["user_name"]
        )


    # ============================================
    # SELL BOOK PAGE
    # ============================================

    @app.route("/sell-book")
    def sell_book_page():

        if "user_id" not in session:

            return redirect(
                "/login-page"
            )


        return render_template(
            "sell_book.html"
        )


    # ============================================
    # SELL BOOK
    # ============================================

    @app.route(
        "/sell-book",
        methods=["POST"]
    )
    def sell_book():

        if "user_id" not in session:

            return jsonify({
                "success": False,
                "message": "Please login first."
            }), 401


        title = request.form.get("title")
        author = request.form.get("author")
        category = request.form.get("category")
        price = request.form.get("price")
        condition = request.form.get("condition")
        description = request.form.get("description")

        image = request.files.get("image")


        # Default image
        filename = "default.jpg"


        # Save uploaded image
        if image and image.filename != "":

            filename = secure_filename(
                image.filename
            )


            upload_path = os.path.join(
                app.static_folder,
                "uploads",
                filename
            )


            image.save(
                upload_path
            )


        # Create book
        book = Book(
            title=title,
            author=author,
            category=category,
            price=float(price),
            condition=condition,
            description=description,
            image=filename,
            seller_id=session["user_id"]
        )


        db.session.add(book)
        db.session.commit()


        return jsonify({
            "success": True,
            "message": "Book Uploaded Successfully."
        })


    # # ============================================
    # # BROWSE BOOKS + SEARCH + CATEGORY FILTER
    # # ============================================

    # @app.route("/browse-books")
    # def browse_books():

    #     if "user_id" not in session:

    #         return redirect(
    #             "/login-page"
    #         )


    #     # Get search and category
    #     search = request.args.get(
    #         "search",
    #         ""
    #     ).strip()


    #     category = request.args.get(
    #         "category",
    #         ""
    #     ).strip()


    #     # ========================================
    #     # CATEGORY FILTER
    #     # ========================================

    #     if category:

    #         books = Book.query.filter(
    #             Book.category.ilike(category)
    #         ).order_by(
    #             Book.created_at.desc()
    #         ).all()


    #     # ========================================
    #     # SEARCH FILTER
    #     # ========================================

    #     elif search:

    #         books = Book.query.filter(
    #             (Book.title.ilike(
    #                 f"%{search}%"
    #             )) |

    #             (Book.author.ilike(
    #                 f"%{search}%"
    #             )) |

    #             (Book.category.ilike(
    #                 f"%{search}%"
    #             ))
    #         ).order_by(
    #             Book.created_at.desc()
    #         ).all()


    #     # ========================================
    #     # ALL BOOKS
    #     # ========================================

    #     else:

    #         books = Book.query.order_by(
    #             Book.created_at.desc()
    #         ).all()


    #     return render_template(
    #         "browse_books.html",
    #         books=books,
    #         search=search,
    #         category=category
    #     )
    # ============================================
    # BROWSE BOOKS + SEARCH + CATEGORY FILTER
    # ============================================

    @app.route("/browse-books")
    def browse_books():

        if "user_id" not in session:
            return redirect("/login-page")

        # Get search and category from URL
        search = request.args.get("search", "").strip()
        category = request.args.get("category", "").strip()

        # ========================================
        # CATEGORY + SEARCH FILTER
        # ========================================

        if category and search:

            books = Book.query.filter(
                Book.category.ilike(f"%{category}%"),
                (
                    Book.title.ilike(f"%{search}%")
                    |
                    Book.author.ilike(f"%{search}%")
                )
            ).order_by(
                Book.created_at.desc()
            ).all()

        # ========================================
        # CATEGORY ONLY
        # ========================================

        elif category:

            books = Book.query.filter(
                Book.category.ilike(f"%{category}%")
            ).order_by(
                Book.created_at.desc()
            ).all()

        # ========================================
        # SEARCH ONLY
        # ========================================

        elif search:

            books = Book.query.filter(
                (Book.title.ilike(f"%{search}%"))
                |
                (Book.author.ilike(f"%{search}%"))
                |
                (Book.category.ilike(f"%{search}%"))
            ).order_by(
                Book.created_at.desc()
            ).all()

    # ========================================
    # ALL BOOKS
    # ========================================

        else:

            books = Book.query.order_by(
                Book.created_at.desc()
            ).all()

        return render_template(
            "browse_books.html",
            books=books,
            search=search,
            category=category
        )

    # ============================================
    # BOOK DETAILS
    # ============================================

    @app.route(
        "/book-details/<int:book_id>"
    )
    def book_details(book_id):

        if "user_id" not in session:

            return redirect(
                "/login-page"
            )


        book = Book.query.get_or_404(
            book_id
        )


        return render_template(
            "book_details.html",
            book=book
        )


    # ============================================
    # MY BOOKS
    # ============================================

    @app.route("/my-books")
    def my_books():

        if "user_id" not in session:

            return redirect(
                "/login-page"
            )


        books = Book.query.filter_by(
            seller_id=session["user_id"]
        ).order_by(
            Book.created_at.desc()
        ).all()


        return render_template(
            "my_books.html",
            books=books
        )


    # ============================================
    # EDIT BOOK PAGE
    # ============================================

    @app.route(
        "/edit-book/<int:book_id>"
    )
    def edit_book(book_id):

        if "user_id" not in session:

            return redirect(
                "/login-page"
            )


        book = Book.query.get_or_404(
            book_id
        )


        # Only seller can edit
        if book.seller_id != session["user_id"]:

            return "Unauthorized", 403


        return render_template(
            "edit_book.html",
            book=book
        )


    # ============================================
    # UPDATE BOOK
    # ============================================

    @app.route(
        "/update-book/<int:book_id>",
        methods=["POST"]
    )
    def update_book(book_id):

        if "user_id" not in session:

            return jsonify({
                "success": False,
                "message": "Login Required"
            }), 401


        book = Book.query.filter_by(
            id=book_id,
            seller_id=session["user_id"]
        ).first()


        if not book:

            return jsonify({
                "success": False,
                "message": "Book Not Found"
            }), 404


        # Update information
        book.title = request.form.get(
            "title"
        )

        book.author = request.form.get(
            "author"
        )

        book.category = request.form.get(
            "category"
        )

        book.price = float(
            request.form.get(
                "price"
            )
        )

        book.condition = request.form.get(
            "condition"
        )

        book.description = request.form.get(
            "description"
        )


        # New image
        image = request.files.get(
            "image"
        )


        if image and image.filename != "":

            filename = secure_filename(
                image.filename
            )


            upload_path = os.path.join(
                app.static_folder,
                "uploads",
                filename
            )


            image.save(
                upload_path
            )


            book.image = filename


        db.session.commit()


        return jsonify({
            "success": True,
            "message": "Book Updated Successfully"
        })


    # ============================================
    # DELETE BOOK
    # ============================================

    @app.route(
        "/delete-book/<int:book_id>"
    )
    def delete_book(book_id):

        if "user_id" not in session:

            return redirect(
                "/login-page"
            )


        book = Book.query.filter_by(
            id=book_id,
            seller_id=session["user_id"]
        ).first()


        if not book:

            return "Book Not Found", 404


        # Remove related cart entries first
        Cart.query.filter_by(
            book_id=book_id
        ).delete()


        db.session.delete(book)
        db.session.commit()


        return redirect(
            "/my-books"
        )
    # ============================================
    # HOME PAGE
    # ============================================

    @app.route("/home")
    def home_back():

        return render_template(
            "home.html"
        )


    # ============================================
    # LOGOUT
    # ============================================

    @app.route("/logout")
    def logout():

        session.clear()


        return redirect(
            "/login-page"
        )


# ============================================
# END OF ROUTES
# ============================================