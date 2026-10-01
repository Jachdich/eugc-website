from main import ingest_signups, read_excel, list_flying_days, get_flying_day, FlyingDay, add_flying_day, make_account
import datetime
import main
from flask import Flask, flash, request, redirect, url_for
import flask
import flask_login

import sqlite3
from flask import g
from dataclasses import dataclass
from argon2 import PasswordHasher
from functools import wraps
password_hasher = PasswordHasher()

#meow


DATABASE = 'eugc.db'
app = Flask(__name__, static_folder="../frontend", static_url_path="/static")


# login test


app.secret_key = "super secret string"  # Change this!

login_manager = flask_login.LoginManager()
login_manager.init_app(app)

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

@dataclass
class UserAccount(flask_login.UserMixin):
    id: int
    password_hash: str
    email: str
    roles: list[str]
    def get_id(self):
        return self.email

@login_manager.user_loader
def user_loader(email):
    db = get_db()
    cur = db.cursor()
    # TODO maybe left join this
    users = list(cur.execute("select id, password_hash from people where email = ?", (email,)))
    if len(users) == 0:
        return None
    assert len(users) == 1, ">1 users with the same email"
    user = users[0]
    roles = [i[0] for i in cur.execute("select role from people_roles where person = ?", (user[0],))]
    try:
        return UserAccount(*user, email, roles)
    except StopIteration:
        return None

def role_required(role):
    def role_required_inner(func):
        @wraps(func)
        def decorated_view(*args, **kwargs):
            if not role in flask_login.current_user.roles:
                return flask_login.current_app.login_manager.unauthorized()
            return func(*args, **kwargs)

        return decorated_view
    return role_required_inner


@app.post("/eugc/api/v1/register")
def api_register():
    data = request.get_json()
    db = get_db()
    
    new_account_id = make_account(db, data["email"], data["phone"], data["name"], data["password"], data["tourist"])
    if new_account_id is None:
        return flask.Response(status=409)

    user = user_loader(data["email"])
    if user is None or not password_hasher.verify(user.password_hash, data["password"]):
        return flask.Response(status=403)

    flask_login.login_user(user)
    return flask.Response(status=200)

@app.post("/eugc/api/v1/login")
def api_login():
    data = request.get_json()
    user = user_loader(data["id"])

    if user is None or user.password_hash is None or not password_hasher.verify(user.password_hash, data["password"]):
        return flask.Response(status=403)

    if password_hasher.check_needs_rehash(user.password_hash):
        user.password_hash = password_hasher.hash(data["password"])
        db = get_db()
        cur = db.cursor()
        cur.execute("update people set password_hash = ? where id = ?", (user.password_hash, user.id))

    flask_login.login_user(user)
    print(flask_login.current_user)
    return flask.Response(status=200)

@app.route("/eugc/api/v1/logout")
def logout():
    flask_login.logout_user()
    return "Logged out"

@app.route("/eugc/api/v1/is_logged_in")
def is_logged_in():
    val = flask_login.current_user.is_authenticated
    uname = None
    db = get_db()
    cur = db.cursor()
    roles = []
    if val:
        uname = next(cur.execute("select name from people where id = ?", (flask_login.current_user.id,)))[0]
        roles = flask_login.current_user.roles
    return {"logged_in": val, "uname": uname, "roles": roles}

@app.route('/eugc/api/v1/add_signups', methods=['POST'])
@flask_login.login_required
@role_required(1)
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

@app.route("/eugc/api/v1/get_people_names", methods=["GET"])
@flask_login.login_required
@role_required(1)
def get_people_names():
    db = get_db()
    cur = db.cursor()
    return {"rows": [i for i in cur.execute("select id, name from people")]}

# TODO this may perform horribly if the number of users grows
@app.route("/eugc/api/v1/list_people", methods=["GET"])
@flask_login.login_required
@role_required(1)
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

        recency = None
        if person.briefing_date is not None and last_flight_date is not None:
            if person.briefing_date > last_flight_date:
                recency = person.briefing_date
            else:
                recency = last_flight_date
        elif person.briefing_date is not None:
            recency = person.briefing_date
        elif last_flight_date is not None:
            recency = last_flight_date
            
        row = [
            person.id,
            person.name,
            person.notes,
            person.e_number,
            person.email,
            person.phone,
            main.num_signups(db, person.id),
            main.num_flying_days(db, person.id),
            person.keenness,
            person.briefing_score,
            person.briefing_date.timestamp() if person.briefing_date is not None else None,
            availability,
            days_since_last_flight,
            signups_since_last_flight,
            person.tourist,
        ]
        rows.append(row)

    return {"rows": rows}

@app.route("/eugc/api/v1/get-flying-days")
@flask_login.login_required
@role_required(1)
def get_flying_days():
    db = get_db()
    ids = list_flying_days(db)
    days = [get_flying_day(db, id).to_json() for id in ids]
    return {"rows": days}

@app.post("/eugc/api/v1/update-flying-day")
@flask_login.login_required
@role_required(1)
def update_flying_day():
    db = get_db()
    cur = db.cursor()
    data = request.get_json()
    day = FlyingDay.from_json(data)

    # TODO - partial update would be better
    print(repr(day.id))
    cur.execute("delete from flying_days where id = ?", (day.id,))
    cur.execute("delete from flying_days_instructors where flying_day = ?", (day.id,))
    cur.execute("delete from flying_days_supervisors where flying_day = ?", (day.id,))
    cur.execute("delete from flying_days_transporters where flying_day = ?", (day.id,))
    cur.execute("delete from flying_days_people where flying_day = ?", (day.id,))

    add_flying_day(db, day)
    db.commit()
    return flask.Response(status=200)

@app.route("/eugc/api/v1/list_signups")
@flask_login.login_required
@role_required(1)
def list_signups():
    db = get_db()
    cur = db.cursor()
    rows = list(cur.execute("select * from signups"))
    return {"rows": rows}

@app.route("/eugc/api/v1/list_briefings")
@flask_login.login_required
@role_required(1)
def list_briefings():
    db = get_db()
    cur = db.cursor()
    rows = list(cur.execute("select * from briefings order by date desc"))
    return {"rows": rows}

@app.post("/eugc/api/v1/add-briefing")
@flask_login.login_required
@role_required(1)
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

@app.route("/eugc/api/v1/availability_form", methods=["POST"])
@flask_login.login_required
def availability_form():
    data = request.get_json()
    if data["availability"] == 0:
        return flask.Response(status=401)
    db = get_db()
    main.ingest_one_signup(db, flask_login.current_user.id, data["trial"], data["briefing"], data["availability"], data["notes"], data["car"], data["bike"])
    return flask.Response(status=200)

@app.route("/eugc/api/v1/update-cell", methods=["POST"])
@flask_login.login_required
@role_required(1)
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
        cur.execute("update people set email = ? where id = ?", (value, id))
    if col == 5:
        cur.execute("update people set phone = ? where id = ?", (value, id))
    if col == 8:
        cur.execute("update people set keenness = ? where id = ?", (value, id))

    db.commit()
    return flask.Response(status=200)
        
@app.route("/eugc/api/v1/add-user", methods=["POST"])
@flask_login.login_required
@role_required(1)
def add_user():
    data = request.get_json()
    db = get_db()
    cur = db.cursor()
    cur.execute("insert into people (name, email, phone, tourist) values (?, ?, ?, ?)", (data["name"], data["email"], data["phone"], data["tourist"]))
    db.commit()
    return flask.Response(status=200)
    
# TODO stupid hack
from threading import Lock
mutex = Lock()

@app.before_request
def before_request():
    with mutex:
        db = get_db()
        cur = db.cursor()
        latest_org = cur.execute("select date from flying_days order by date desc limit 1")
        the_date = latest_org.fetchone()
        the_date = datetime.datetime.fromtimestamp(the_date[0]).date() if the_date is not None else None
        if the_date is None:
            date = datetime.date.today()
        elif (the_date - datetime.date.today()).days < 7:
            date = the_date
        else:
            return

        while date < datetime.date.today() + datetime.timedelta(days=7):
            this_day = date.isoweekday() - 1
            until_friday = (4 - this_day) % 7
            friday = date + datetime.timedelta(days=until_friday)
            saturday = friday + datetime.timedelta(days=1)
            sunday = friday + datetime.timedelta(days=2)

            add_flying_day(db, FlyingDay(None, datetime.datetime.combine(friday, datetime.datetime.min.time()), [], [], [], [], None))
            add_flying_day(db, FlyingDay(None, datetime.datetime.combine(saturday, datetime.datetime.min.time()), [], [], [], [], None))
            add_flying_day(db, FlyingDay(None, datetime.datetime.combine(sunday, datetime.datetime.min.time()), [], [], [], [], None))

            date = sunday

if __name__ == "__main__":
    app.run(debug=True)
