"""Authentication routes and session management."""

from functools import wraps
from flask import Blueprint, request, jsonify, session, redirect, url_for
from app.models import db, User

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


def login_required(f):
    """Decorator to protect routes requiring authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            if request.is_json or request.path.startswith("/api/"):
                return jsonify({"error": "Unauthorized", "message": "Authentication required"}), 401
            return redirect(url_for("web.login_page"))
        return f(*args, **kwargs)
    return decorated_function


@auth_bp.route("/register", methods=["POST"])
def register():
    """Register a new user."""
    data = request.get_json(silent=True) or request.form
    username = data.get("username", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not username or not email or not password:
        return jsonify({"error": "Missing fields", "message": "Username, email, and password are required"}), 400

    if len(password) < 6:
        return jsonify({"error": "Weak password", "message": "Password must be at least 6 characters"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Conflict", "message": "Username already taken"}), 409

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Conflict", "message": "Email already registered"}), 409

    user = User(username=username, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    # Automatically log user in
    session["user_id"] = user.id
    session["username"] = user.username

    if not request.is_json and request.form:
        return redirect(url_for("web.dashboard_page"))

    return jsonify({
        "status": "success",
        "message": "User registered successfully",
        "user": {"id": user.id, "username": user.username, "email": user.email}
    }), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    """Authenticate an existing user and create a session."""
    data = request.get_json(silent=True) or request.form
    username = data.get("username", "").strip()
    password = data.get("password", "")

    if not username or not password:
        return jsonify({"error": "Missing fields", "message": "Username and password required"}), 400

    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        if not request.is_json and request.form:
            return redirect(url_for("web.login_page", error="Invalid credentials"))
        return jsonify({"error": "Unauthorized", "message": "Invalid username or password"}), 401

    session["user_id"] = user.id
    session["username"] = user.username

    if not request.is_json and request.form:
        return redirect(url_for("web.dashboard_page"))

    return jsonify({
        "status": "success",
        "message": "Logged in successfully",
        "user": {"id": user.id, "username": user.username, "email": user.email}
    }), 200


@auth_bp.route("/logout", methods=["POST", "GET"])
def logout():
    """Clear session data and log out the user."""
    session.clear()
    if request.path.startswith("/api/") or request.is_json or request.headers.get("Accept") == "application/json":
        return jsonify({"status": "success", "message": "Logged out successfully"}), 200
    return redirect(url_for("web.login_page"))


@auth_bp.route("/me", methods=["GET"])
@login_required
def get_current_user():
    """Return profile details for currently authenticated user."""
    user = db.session.get(User, session["user_id"])
    if not user:
        session.clear()
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "status": "success",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "created_at": user.created_at.isoformat() if user.created_at else None
        }
    }), 200
