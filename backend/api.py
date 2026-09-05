from main import ingest_signups, read_excel, list_flying_days, get_flying_day
import datetime
import main
from flask import Flask, flash, request, redirect, url_for
import flask
import flask_login

import sqlite3
from flask import g
from dataclasses import dataclass
from argon2 import PasswordHasher
password_hasher = PasswordHasher()

#meow


DATABASE = 'eugc.db'
app = Flask(__name__, static_folder="../frontend", static_url_path="/static")


# login test


app.secret_key = "super secret string"  # Change this!

login_manager = flask_login.LoginManager()
login_manager.init_app(app)

@dataclass
class UserAccount(flask_login.UserMixin):
    id: int
    password_hash: str

@login_manager.user_loader
def user_loader(id):
    db = get_db()
    cur = db.cursor()
    res = cur.execute("select * from user_accounts where person = ?", (int(id),))
    try:
        return UserAccount(*next(res))
    except StopIteration:
        return None

@app.get("/api/login")
def api_ogin():
    return """<form method=post>
      Email: <input name="email"><br>
      Password: <input name="password" type=password><br>
      <button>Log In</button>
    </form>"""

@app.post("/api/v1/login")
def api_login():
    data = request.get_json()
    user = user_loader(data["id"])

    if user is None or not password_hasher.verify(user.password_hash, data["password"]):
        return flask.redirect(flask.url_for("login"))

    if password_hasher.check_needs_rehash(user.password_hash):
        user.password_hash = password_hasher.hash(data["password"])
        db = get_db()
        cur = db.cursor()
        cur.execute("update user_accounts set password_hash = ? where person = ?", (user.password_hash, user.id))

    flask_login.login_user(user)
    return flask.Response(status=200)

@app.route("/api/protected")
@flask_login.login_required
def protected():
    return flask.render_template_string(
        "Logged in as: {{ user.id }}",
        user=flask_login.current_user
    )

@app.route("/api/v1/logout")
def logout():
    flask_login.logout_user()
    return "Logged out"

@app.route("/api/v1/is_logged_in")
def is_logged_in():
    val = flask_login.current_user.is_authenticated
    uname = None
    if val:
        uname = flask_login.current_user.id
    return {"logged_in": val, "uname": uname}

# end login test


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/api/v1/add_signups', methods=['POST'])
@flask_login.login_required
def upload_file():
    # check if the post request has the file part
    if 'file' not in request.files:
        flash('No file part')
        return flask.Response(status=400)
    file = request.files['file']
    # If the user does not select a file, the browser submits an
    # empty file without a filename.
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    if file:
        table = read_excel(file.stream)
        print("adding", table)
        db = get_db()
        ingest_signups(db, table)
        return flask.Response(status=200)

@app.route("/api/v1/get_people_names", methods=["GET"])
@flask_login.login_required
def get_people_names():
    db = get_db()
    cur = db.cursor()
    return {"rows": [i for i in cur.execute("select id, name from people")]}

# TODO this may perform horribly if the number of users grows
@app.route("/api/v1/list_people", methods=["GET"])
@flask_login.login_required
def list_people():
    db = get_db()
    people = [main.person_info(db, p) for p in main.list_people(db)]

    cur = db.cursor()
    rows = []
    for person in people:
        availability = main.availability(db, person.id)
        flying_days = list(cur.execute("""
            select flying_days.date from flying_days_people
                left join flying_days on flying_days_people.flying_day = flying_days.id
                where flying_days_people.person = ?
                order by flying_days.date desc
                limit 1
        """, (person.id,)))
        last_flight_date = None
        if len(flying_days) > 0:
            last_flight_date = datetime.datetime.fromtimestamp(flying_days[0][0])
            days_since_last_flight = (datetime.datetime.now() - last_flight_date).days
        else:
            days_since_last_flight = None

        signups = list(cur.execute("select completed_datetime from signups where person = ? order by completed_datetime desc limit 1", (person.id,)))
        last_signup_date = None
        if len(signups) > 0:
            last_signup_date = datetime.datetime.fromtimestamp(signups[0][0])

        signups_since_last_flight = None
        if last_flight_date is None and last_signup_date is None:
            signups_since_last_flight = None
        else:
            date = last_flight_date or last_signup_date
            signups_since = list(cur.execute("select count(1) from signups where person = ? and completed_datetime >= ?", (person.id, date.timestamp())))
            assert len(signups_since) == 1
            signups_since_last_flight = signups_since[0][0]
            
        row = [
            person.id,
            person.name,
            person.notes,
            person.e_number,
            person.emails,
            person.phones,
            main.num_signups(db, person.id),
            main.num_flying_days(db, person.id),
            person.keenness,
            person.briefing_score,
            person.briefing_date.timestamp() if person.briefing_date is not None else None,
            availability,
            days_since_last_flight,
            signups_since_last_flight,
        ]
        rows.append(row)

    return {"rows": rows}

@app.route("/api/v1/get-flying-days")
@flask_login.login_required
def get_flying_days():
    db = get_db()
    ids = list_flying_days(db)
    days = [get_flying_day(db, id).to_json() for id in ids]
    return {"rows": days}

@app.route("/api/v1/list_signups")
@flask_login.login_required
def list_signups():
    db = get_db()
    cur = db.cursor()
    rows = list(cur.execute("select * from signups"))
    return {"rows": rows}

@app.route("/api/v1/list_briefings")
@flask_login.login_required
def list_briefings():
    db = get_db()
    cur = db.cursor()
    rows = list(cur.execute("select * from briefings order by date desc"))
    return {"rows": rows}

@app.post("/api/v1/add-briefing")
@flask_login.login_required
def add_briefing():
    db = get_db()
    cur = db.cursor()
    data = request.get_json()
    assert "person" in data
    assert "date" in data
    assert "score" in data
    rows = list(cur.execute("insert into briefings (date, person, score) values (?, ?, ?) returning *", (data["date"], data["person"], data["score"])))
    assert len(rows) == 1
    db.commit()
    return list(rows[0])

@app.route("/api/v1/availability_form", methods=["POST"])
@flask_login.login_required
def availability_form():
    data = request.get_json()
    print(data)
    db = get_db()
    main.ingest_one_signup(db, data["trial"], data["briefing"], data["name"], data["availability"], data["notes"], data["email"], data["phone"], data["car"], )
    return flask.Response(status=200)

@app.route("/api/v1/update-cell", methods=["POST"])
@flask_login.login_required
def update_cell():
    data = request.get_json()
    db = get_db()
    col = data["col"]
    if not col in [1, 2, 3, 4, 5, 8, 11]:
        return flask.Response(status=401) # TODO i forgot what 401 is

    # TODO data validation

    id = data["id"]
    value = data["new_value"]
    cur = db.cursor()
    if col == 1:
        cur.execute("update people set name = ? where id = ?", (value, id))
    if col == 2:
        cur.execute("update people set notes = ? where id = ?", (value, id))
    if col == 3:
        cur.execute("update people set e_number = ? where id = ?", (value, id))
    if col == 4:
        cur.execute("delete from emails where person = ?", (id,))
        cur.executemany("insert into emails (person, email) values (?, ?)", [(id, v) for v in value])
    if col == 5:
        cur.execute("delete from phones where person = ?", (id,))
        cur.executemany("insert into phones (person, phone) values (?, ?)", [(id, v) for v in value])
    if col == 8:
        cur.execute("update people set keenness = ? where id = ?", (value, id))

    db.commit()
    return flask.Response(status=200)
        
    

if __name__ == "__main__":
    app.run(debug=True)
