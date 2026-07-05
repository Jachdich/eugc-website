from flask import Flask, render_template, request
import main
import sqlite3
from flask import g

app = Flask(__name__)

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect("eugc.db")
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/partials/db-table.html")
def load_more():

    sort = request.args.get("sort", "name")
    filter_avail = request.args.get("filter_avail", "false") == "true"
    def sort_key(row):
        if sort == "name":
            return row[1]
        if sort == "id":
            return row[0]

    db = get_db()
    print(filter_avail)
    # if filter_avail:
    #     people = main.people_available(db, main.SATURDAY) +\
    #         main.people_available(db, main.SUNDAY) +\
    #         main.people_available(db, main.FRIDAY)
    # else:
    people = main.list_people(db)
    rows = []
    for p in people:
        person = main.person_info(db, p)
        availability = main.availability(db, person.id)
        if availability == 0 and filter_avail:
            continue
        row = (
            person.id,
            person.name,
            person.e_number,
            person.emails,
            person.phones,
            main.num_signups(db, person.id),
            main.num_flying_days(db, person.id),
            person.keenness,
            person.briefing_score,
            person.briefing_date.timestamp() if person.briefing_date is not None else None,
            person.notes,
            bin(availability)
        )
        rows.append(row)
    return render_template("partials/db-table.html", rows=sorted(rows, key=sort_key))

if __name__ == "__main__":
    app.run(debug=True)

