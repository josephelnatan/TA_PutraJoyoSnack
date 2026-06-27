from flask import Flask, render_template, request, redirect, session
from config import Config
from models.user import db, User

app = Flask(__name__)

app.config.from_object(Config)

db.init_app(app)

with app.app_context():
    db.create_all()


# HOME
@app.route("/")
def home():
    return redirect("/login")


# LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(
            username=username,
            password=password
        ).first()

        if user:

            session["user_id"] = user.id
            session["username"] = user.username
            session["role"] = user.role

            if user.role == "admin":
                return redirect("/admin/dashboard")

            elif user.role == "kasir":
                return redirect("/kasir/dashboard")

            elif user.role == "gudang":
                return redirect("/gudang/dashboard")

        return "Username atau Password Salah"

    return render_template("login.html")


# ADMIN
@app.route("/admin/dashboard")
def admin_dashboard():

    if "user_id" not in session:
        return redirect("/login")

    return "Dashboard Admin"


# KASIR
@app.route("/kasir/dashboard")
def kasir_dashboard():

    if "user_id" not in session:
        return redirect("/login")

    return "Dashboard Kasir"


# GUDANG
@app.route("/gudang/dashboard")
def gudang_dashboard():

    if "user_id" not in session:
        return redirect("/login")

    return "Dashboard Staff Gudang"


# LOGOUT
@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")


# RUN APP
if __name__ == "__main__":
    app.run(debug=True)