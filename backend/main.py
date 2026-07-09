import sqlite3
import flask
import csv
import os
from io import BytesIO
import openpyxl
import datetime
from dataclasses import dataclass

# How to make it easy to make new memebership numbers - can't just be me being able to, automate the process or make it easy for anyone, document it
# In general we need better account logging - who pays for what flights, did they actually pay, E0000 costs broken down, mx, etc - internal use, record keeping
# improved planning of weekly flying

# TODO
# warn about double entry
# people signing up twice a week
# handle multiple/changing emails/phones

fresh_start = not os.path.exists("eugc.db")

con = sqlite3.connect("eugc.db")
cur = con.cursor()

cur.execute("""
create table if not exists signups (
    id integer primary key,
    person integer not null,
    completed_datetime integer not null,
    reported_trial boolean not null,
    attending_briefing boolean not null,
    available_days integer not null,
    has_car boolean not null,
    notes text,
    foreign key (person) references people(id)
)""")

cur.execute("""
create table if not exists flying_days (
    id integer primary key,
    date integer not null,
    instruct integer not null,
    drive integer not null,
    supervise integer not null,
    notes text,
    foreign key (instruct) references people(id),
    foreign key (drive) references people(id),
    foreign key (supervise) references people(id)
)""")

cur.execute("""
create table if not exists flying_days_people (
    id integer primary key,
    flying_day integer not null,
    person integer not null,
    foreign key (person) references people(id),
    foreign key (flying_day) references flying_days(id),
    unique (flying_day, person)
)""")

cur.execute("""
create table if not exists people (
    id integer primary key,
    name text not null unique,
    e_number integer unique,
    keenness real,
    role text,
    notes text
)""")

cur.execute("""
create table if not exists emails (
    id integer primary key,
    person integer not null,
    email text unique,
    foreign key (person) references people(id)
)
""")

cur.execute("""
create table if not exists phones (
    id integer primary key,
    person integer not null,
    phone text unique,
    foreign key (person) references people(id)
)
""")

cur.execute("""
create table if not exists briefings (
    id integer primary key,
    date integer not null,
    person integer not null,
    score real not null,
    foreign key (person) references people(id)
)""")

cur.execute("""
create table if not exists legacy_info (
    person integer primary key,
    signups integer not null,
    flying_days integer not null,
    
    foreign key (person) references people(id)
)""")

@dataclass
class Person:
    id: int
    name: str
    emails: list[str]
    phones: list[str]
    e_number: int | None
    keenness: float | None
    role: str | None
    notes: str | None

    briefing_date: datetime.datetime | None
    briefing_score: float | None

con.commit()

def read_excel(stream) -> list[tuple[any]]:
    workbook = openpyxl.load_workbook(stream)
    sheet = workbook.active

    table = list(sheet.values)
    return table
            
def find_person_by_details(db, name, email, phone) -> int | None:
    cur = db.cursor()
    by_name = list(cur.execute("select id from people where name LIKE ?", (f"%{name}%",)))
    if len(by_name) == 1:
        return by_name[0][0]
    by_phone = list(cur.execute("select person from phones where phone = ?", (phone,)))
    if len(by_phone) == 1:
        return by_phone[0][0]
    by_email = list(cur.execute("select person from emails where email = ?", (email,)))
    if len(by_email) == 1:
        return by_email[0][0]

    # can't find it
    # TODO search similar names?
    return None

MONDAY   = 0b0000001
TUESDAY  = 0b0000010
WEDNESDAY= 0b0000100
THURSDAY = 0b0001000
FRIDAY   = 0b0010000
SATURDAY = 0b0100000
SUNDAY   = 0b1000000

def ingest_signups(db, data: list[tuple[any]]):
    cur = db.cursor()
    header = data[0]
    body = data[1:]
    if all(test in colname for colname, test in zip(header, ('ID', 'Start time', 'Completion time', 'Email', 'Name', 'Is this your trial flight?', "Do you plan to attend this week's trial flight briefing?", 'Please enter your full name', 'Which days are you available?', 'Notes/comments (optional)', 'Email Addresss', 'Mobile number (in case we need to call you)', 'Do you have a car (and are willing to help with transport)?', 'Last modified time'))):
        indices = {
            "start": 1, "trial": 5, "name": 7, "days": 8, "notes": 9, "email": 10, "phone": 11, "car": 12
        }
    elif header == ('ID', 'Start time', 'Completion time', 'Email', 'Name', 'Is this your trial flight?', 'Please enter your full name', 'Which days are you available?', 'Notes/comments (optional)', 'Email Addresss', 'Mobile number (in case we need to call you)', 'Do you have a car (and are willing to help with transport)?', 'Last modified time'):
        indices = {
            "start": 1, "trial": 5, "name": 6, "days": 7, "notes": 8, "email": 9, "phone": 10, "car": 11
        }
    else:
        raise ValueError(f"I don't know how to process header {header}")
    for row in body:
        start = row[indices["start"]]
        reported_trial = row[indices["trial"]]
        name = row[indices["name"]]
        days = row[indices["days"]]
        notes = row[indices["notes"]]
        email = row[indices["email"]]
        phone = row[indices["phone"]]
        car = row[indices["car"]] == "Yes"

        if days is None or name is None or email is None or phone is None:
            print(f"something wrong with {name=} {days=} {email=} {phone=}")
            continue # TODO warn
        name = name.strip()
        email = email.strip()
        phone = phone.strip()
        days = days.lower()
        # Available days: bitfield. bit 0 is monday, 1 is tuesday, etc. 0bssftwtm
        available_days = 0
        if "friday" in days:
            available_days |= FRIDAY
        if "saturday" in days:
            available_days |= SATURDAY
        if "sunday" in days:
            available_days |= SUNDAY

        person_id = find_person_by_details(db, name, email, phone)
        if person_id is None:
            person_id = next(cur.execute("insert into people (name) values (?) returning id", (name,)))[0]
            cur.execute("insert into emails (person, email) values (?, ?)", (person_id, email))
            cur.execute("insert into phones (person, phone) values (?, ?)", (person_id, phone))

        cur.execute(
            "insert into signups (person, completed_datetime, reported_trial, attending_briefing, available_days, has_car, notes) values (?, ?, ?, ?, ?, ?, ?)",
            (person_id, start.timestamp(), reported_trial, False, available_days, car, notes)
        )

    db.commit()
        
def ingest_one_signup(db, reported_trial, briefing, name, available_days, notes, email, phone, car):
    cur = db.cursor()
    submit_time = datetime.datetime.now().timestamp()

    name = name.strip()
    email = email.strip()
    phone = phone.strip()

    person_id = find_person_by_details(db, name, email, phone)
    if person_id is None:
        person_id = next(cur.execute("insert into people (name) values (?) returning id", (name,)))[0]
        cur.execute("insert into emails (person, email) values (?, ?)", (person_id, email))
        cur.execute("insert into phones (person, phone) values (?, ?)", (person_id, phone))

    cur.execute(
        "insert into signups (person, completed_datetime, reported_trial, attending_briefing, available_days, has_car, notes) values (?, ?, ?, ?, ?, ?, ?)",
        (person_id, submit_time, reported_trial, briefing, available_days, car, notes)
    )

    db.commit()
        
def people_available(db, day: int) -> list[int]:
    cur = db.cursor()
    # now = datetime.datetime.now()
    now = datetime.datetime(2025, 6, 16, 10, 3, 32, 13513)
    monday = now - datetime.timedelta(days=now.weekday())
    return [i[0] for i in cur.execute("select person from signups where available_days & ? and completed_datetime > ?", (day, monday.timestamp()))]

def availability(db, person: int) -> int:
    cur = db.cursor()
    now = datetime.datetime(2025, 6, 16, 10, 3, 32, 13513)
    monday = now - datetime.timedelta(days=now.weekday())
    result = list(cur.execute("select available_days from signups where person = ? and completed_datetime > ?", (person, monday.timestamp())))
    if len(result) == 0:
        return 0
    # assert not (len(result) > 1), "More than one person for the same ID"
    print(result)
    print(result[0][0])
    return result[0][0]

def num_signups(db, person):
    cur = db.cursor()
    count = next(cur.execute("select count(1) from signups where person = ?1 limit 1", (person,)))[0]
    fudge_factor = list(cur.execute("select signups from legacy_info where person = ?", (person,)))
    if len(fudge_factor) > 0:
        count += fudge_factor[0][0]
    return count

# SELECT
#   Name,
#   Title
# FROM
#   artists
#   LEFT JOIN albums ON artists.ArtistId = albums.ArtistId

def person_info(db, person_id: int) -> Person | None:
    cur = db.cursor()
    result = list(cur.execute("select * from people left join briefings on people.id = briefings.person where people.id = ?", (person_id,)))
    if len(result) == 0:
        return None
    assert not (len(result) > 1), "More than one person for the same ID"
    p = result[0]
    emails = [i[0] for i in cur.execute("select email from emails where person = ?", (p[0],))]
    phones = [i[0] for i in cur.execute("select phone from phones where person = ?", (p[0],))]
    return Person(p[0], p[1], emails, phones, p[2], p[3], p[4], p[5], datetime.datetime.fromtimestamp(p[7]) if p[7] is not None else None, p[9])

def num_flying_days(db, person):
    cur = db.cursor()
    count = next(cur.execute("select count(1) from flying_days_people where person = ?1 limit 1", (person,)))[0]
    fudge_factor = list(cur.execute("select flying_days from legacy_info where person = ?", (person,)))
    if len(fudge_factor) > 0:
        count += fudge_factor[0][0]
    return count

def last_flying_days(db, person):
    cur = db.cursor()
    pass
    
def add_flying_day(db, date: datetime.datetime, instruct_id: int, drive_id: int, supervise_id: int, notes: str | None, people: list[int]):
    cur = db.cursor()
    day_id = next(cur.execute("insert into flying_days (date, instruct, drive, supervise, notes) values (?, ?, ?, ?, ?)", (date.timestamp(), instruct_id, drive_id, supervise_id, notes)))[0]
    for person in people:
        cur.execute("insert into flying_days_people (flying_day, person) values (?, ?)", (day_id, person))
    db.commit()

def add_briefing(db, date: datetime.datetime, people_scores: list[(int, float)]):
    cur = db.cursor()
    cur.executemany("insert into briefings (person, date, score) values (?, ?, ?)", [(person, date.timestamp(), score) for person, score in people_scores])
    db.commit()

flying_days = [next(cur.execute("insert into flying_days (date, instruct, drive, supervise) values (?, ?, ?, ?) returning id", (0, 0, 0, 0)))[0] for _ in range(50)]

if fresh_start:
    with open("flying_list.csv") as f:
        r = csv.reader(f)
        next(r)
        for row in r:
            name, e, cng, paid, email, phone, signups, flying, keenness, briefing_score, briefing_date, notes, _, _, _, _, *rest = row
            briefing_score = float(briefing_score) if briefing_score != "" else None
            keenness = float(keenness) if keenness != "" else None
            briefing_date = datetime.datetime.strptime(briefing_date, "%d/%m/%Y") if briefing_date != "" else None
            notes = notes if notes != "" else None
            e = int(e[1:]) if e != "" else None
            signups = int(signups)
            flying = int(flying)
            name = (" ".join(reversed(name.split(",")))).strip()
            emails = email.split(" ")
        
            # print(f"{name!r}", e, emails, phone, signups, flying, keenness, briefing_score, briefing_date, notes)

            person_id = next(cur.execute("insert into people (name, e_number, keenness, notes) values (?, ?, ?, ?) returning id", (name, e, keenness, notes)))[0]
            for email in emails:
                cur.execute("insert into emails (person, email) values (?, ?)", (person_id, email))

            if phone != "":
                cur.execute("insert into phones (person, phone) values (?, ?)", (person_id, phone))
            # for i in range(signups):
            #     cur.execute("insert into signups (person, completed_datetime, available_days, notes, reported_trial, attending_briefing, has_car) values (?, ?, ?, ?, ?, ?, ?)", (person_id, 0, 0, None, False, False, False))
            # for i in range(flying):
            #     cur.execute("insert into flying_days_people (flying_day, person) values (?, ?)", (flying_days[i], person_id))
            cur.execute("insert into legacy_info (person, signups, flying_days) values (?, ?, ?)", (person_id, signups, flying))

            if briefing_date is not None and briefing_score is not None:
                add_briefing(con, briefing_date, [(person_id, briefing_score)])

paths = [
 "Edinburgh University Gliding Club Sem2 2025_2026(1-7).xlsx",
 "Edinburgh University Gliding Club Sem2 2025_2026(1-8).xlsx",
]
if fresh_start:
    for path in paths:
        with open("/home/james/Downloads/"+path, "rb") as f:
            # data = f.read()
            ingest_signups(con, read_excel(f))

# add_briefing(datetime.datetime(2025, 12, 4), [(1, 3), (2, 3), (3, 1)])

# for person in people_available(SUNDAY):
#     info = person_info(person)
#     print(info,num_signups(person))

def list_people(db):
    cur = db.cursor()
    return [i[0] for i in cur.execute("select id from people")]

cols = [[] for _ in range(9)]
for id in [i[0] for i in cur.execute("select id from people order by (select count(1) from signups where person = people.id)")]:
    info = person_info(con, id)
    print(info)
    cols[0].append(str(info.name))
    cols[1].append(("E" + str(info.e_number)) if info.e_number is not None else "")
    cols[2].append(", ".join(info.emails))
    cols[3].append(", ".join(info.phones))
    cols[4].append(str(num_signups(con, id)))
    cols[5].append(str(num_flying_days(con, id)))
    cols[6].append(str(info.keenness) if info.keenness is not None else "")
    cols[7].append(str(info.briefing_score) if info.briefing_score is not None else "")
    cols[8].append(str(info.briefing_date.date()) if info.briefing_date is not None else "")


col_sizes = [max(len(i) for i in col) for col in cols]

def pad(s, l):
    return s + " " * (l - len(s))

for row in zip(*cols):
    for item, size in zip(row, col_sizes):
        print(pad(item, size), end=" | ")
    print()
        
con.close()
