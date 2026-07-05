from main import ingest_signups, read_excel
import main
from flask import Flask, flash, request, redirect, url_for
import flask
#meow

import sqlite3
from flask import g

DATABASE = 'eugc.db'
app = Flask(__name__, static_folder="../frontend", static_url_path="/static")

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

# TODO this may perform horribly if the number of users grows
@app.route("/api/v1/list_people", methods=["GET"])
def list_people():
    db = get_db()
    people = [main.person_info(db, p) for p in main.list_people(db)]

    rows = []
    for person in people:
        availability = main.availability(db, person.id)
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
        ]
        rows.append(row)

    return {"rows": rows}
if __name__ == "__main__":
    app.run(debug=True)
