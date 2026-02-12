import os
from os import path
import sqlalchemy
from flask import Flask, render_template, request, redirect, url_for, session
from sqlalchemy import create_engine

# Database connection
# Check if the server name matches
Server = ""
Database = ""
User = ""
Password = ""
Database_Conn = f'mysql+pymysql://{User}:{Password}@{Server}/{Database}'

engine = create_engine(Database_Conn)
con = engine.connect()

app = Flask(__name__)
app.secret_key = "secret_key"


@app.teardown_request
def session_clear(exception=None):
    con.close()
    if exception:
        con.rollback()


@app.route("/", methods=["GET", "POST"])
def index():
    if not session.get("loggedin"):
        return redirect(url_for("login"))
    else:
        return render_template("index.html")


@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if not session.get("loggedin"):
        return redirect(url_for("login"))
    
    try:
        with engine.connect() as connection:
            sql_query = sqlalchemy.text("SELECT * FROM advices")
            result = connection.execute(sql_query)
            advices = result.fetchall()
            return render_template("dashboard.html", advices=advices)
    except Exception as e:
        return f"Eroare la încărcarea dashboard-ului: {str(e)}"

@app.route("/login")
def login():
    return render_template("login.html", session=session)


@app.route("/calendar")
def calendar():
    if not session.get("loggedin"):
        return redirect(url_for("login"))
    
    try:
        with engine.connect() as connection:
            sql = sqlalchemy.text("SELECT * FROM events")
            events = connection.execute(sql).fetchall()
            return render_template("calendar.html", events=events, user=session["username"])
    except Exception as e:
        return f"Eroare: {str(e)}"


@app.route("/logout")
def logout():
    session.pop("loggedin", None)
    session.pop("username", None)
    return redirect(url_for("login"))


@app.route("/base")
def test():
    return render_template("starter.html")


@app.route("/login_post", methods=["GET", "POST"])
def login_post():
    username = request.form.get("username")
    password = request.form.get("password")
    
    try:
        with engine.connect() as connection:
            sql_query = sqlalchemy.text("SELECT * FROM users WHERE username = :user_name AND password = :pwd")
            result = connection.execute(sql_query, {"user_name": username, "pwd": password})
            account = result.fetchone()

            if account:
                session["loggedin"] = True
                session["username"] = account[1]
                return redirect(url_for("index"))
            else:
                return "Utilizator sau parolă incorectă!"
    except Exception as e:
        return f"Eroare SQL: {e}"


@app.route("/event_post", methods=["GET", "POST"])
def event_post():
    if not session.get("loggedin"):
        return redirect(url_for("login"))
        
    title = request.form.get("title")
    date = request.form.get("date")
    user = session["username"]
    allday = request.form.get("allDay")

    try:
        with engine.connect() as connection:
            sql = sqlalchemy.text("INSERT INTO events (title, event_date, user, allday) VALUES (:t, :d, :u, :a)")
            connection.execute(sql, {"t": title, "d": date, "u": user, "a": allday})
            connection.commit()
            return redirect(url_for("calendar"))
    except Exception as e:
        return f"Eroare la salvare: {str(e)}"

@app.route("/advice_post", methods=["GET", "POST"])
def advice_post():
    if not session.get("loggedin"):
        return redirect(url_for("login"))

    if request.method == "POST":
        advice_title = request.form["title"]
        advice_message = request.form["message"]
        advice_user = session["username"]
        
        try:
            with engine.connect() as connection:
                sql_query = sqlalchemy.text("INSERT INTO advices (title, message, user) VALUES (:title, :message, :user)")
                connection.execute(sql_query, {"title": advice_title, "message": advice_message, "user": advice_user})
                connection.commit()
                return redirect(url_for("dashboard"))
        except Exception as e:
            return f"Eroare la salvare advice: {str(e)}"

    return redirect(url_for("dashboard"))


if __name__ == "__main__":
    app.run()
