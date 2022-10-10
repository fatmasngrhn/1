from flask import Flask, render_template, request, session, redirect, url_for, flash
import sqlite3

app = Flask(__name__)
app.secret_key = "%&%secret%&%"


@app.route("/")
def index_page():
    if "user_email" in session:
        # return render_template("index.html", userstate=True, user_name=session["user_email"])
        return redirect(url_for("products_page"))
    else:
        return redirect(url_for("login_page"))


@app.route("/register", methods=["GET", "POST"])
def register_page():
    if request.method == "GET":
        if "user_email" in session:
            return redirect(url_for("index_page"))
        return render_template("register.html")
    else:
        with sqlite3.connect("database.db") as connection:
            cursor = connection.cursor()

            _email = request.form["email"]
            _password = request.form["password"]

            cursor.execute("INSERT INTO users(email, password) VALUES(?, ?)", (_email, _password))
            connection.commit()
        return redirect(url_for("login_page"))


@app.route("/login", methods=["GET", "POST"])
def login_page():
    if request.method == "POST":
        with sqlite3.connect("database.db") as connection:
            cursor = connection.cursor()

            _email = request.form["email"]
            _password = request.form["password"]
            cursor.execute("SELECT * FROM users WHERE email=? AND password=?", (_email, _password))
            res = cursor.fetchall()

        if len(res) > 0:
            user = res[0]
            session["user_id"] = user[0]
            session["user_email"] = user[1]
            return redirect(url_for("index_page"))
        else:
            return "Böyle bir kullanıcı bulunamadı"
    else:
        if "user_email" in session:
            return redirect(url_for("index_page"))
        else:
            return render_template("login.html")


@app.route("/logout", methods=["GET"])
def logout_page():
    if request.method == "GET":
        if "user_email" in session:
            session.pop("user_email")
            session.pop("user_id")
        return redirect(url_for("index_page"))


@app.route("/products")
def products_page():
    if "user_email" in session:
        with sqlite3.connect("database.db") as connection:
            cursor = connection.cursor()

            cursor.execute("SELECT * FROM urunler WHERE userid=?", (session["user_id"], ))
            res = cursor.fetchall()
        return render_template("products.html", userstate=True, user_name=session["user_email"], length_products=len(res), products=res)
    else:
        return redirect(url_for("login_page"))


@app.route("/product/add", methods=["GET", "POST"])
def product_add_page():
    if request.method == "GET":
        if "user_email" in session:
            return render_template("productadd.html")
        else:
            return redirect(url_for("login_page"))
    else:
        _product_name = request.form["product_name"]
        _product_sku = request.form["product_sku"]
        _product_num = request.form["product_num"]
        _product_price = request.form["product_price"]

        with sqlite3.connect("database.db") as connection:
            cursor = connection.cursor()

            cursor.execute("INSERT INTO urunler(userid, urunadi, stokkodu, adet, fiyat) VALUES(?, ?, ?, ?, ?)",
                           (session["user_id"], _product_name, _product_sku, _product_num, _product_price))
            connection.commit()

        return redirect(url_for("products_page"))


@app.route("/product/edit/<lineid>", methods=["GET", "POST"])
def product_edit_page(lineid):
    if request.method == "POST":
        _product_name = request.form["product_name"]
        _product_sku = request.form["product_sku"]
        _product_num = request.form["product_num"]
        _product_price = request.form["product_price"]

        with sqlite3.connect("database.db") as connection:
            cursor = connection.cursor()

            cursor.execute("UPDATE urunler SET urunadi=?, stokkodu=?, adet=?, fiyat=? WHERE urunid=?",
                           (_product_name, _product_sku, _product_num, _product_price, lineid))
            connection.commit()

        return redirect(url_for("products_page"))
    else:
        if "user_email" in session:
            with sqlite3.connect("database.db") as connection:
                cursor = connection.cursor()

                cursor.execute("SELECT * FROM urunler WHERE userid=? AND urunid=?", (session["user_id"], lineid))
                product = cursor.fetchall()[0]

            return render_template("productedit.html", product=product)
        else:
            return redirect(url_for("login_page"))


@app.route("/product/delete/<lineid>", methods=["POST"])
def product_delete_page(lineid):
    with sqlite3.connect("database.db") as connection:
        cursor = connection.cursor()

        cursor.execute("DELETE FROM urunler WHERE urunid=?", (lineid, ))
        connection.commit()

    return redirect(url_for("products_page"))


if __name__ == "__main__":
    app.run()
