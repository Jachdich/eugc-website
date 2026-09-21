import sqlite3
import flask
import csv
import os
from io import BytesIO
import openpyxl
import datetime
from dataclasses import dataclass

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
    has_bike boolean not null,
    notes text,
    foreign key (person) references people(id)
)""")

cur.execute("""
create table if not exists flying_days (
    id integer primary key,
    date integer not null,
    notes text
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
create table if not exists flying_days_instructors (
    id integer primary key,
    flying_day integer not null,
    person integer not null,
    foreign key (person) references people(id),
    foreign key (flying_day) references flying_days(id),
    unique (flying_day, person)
)""")
cur.execute("""
create table if not exists flying_days_transporters (
    id integer primary key,
    flying_day integer not null,
    person integer not null,
    spaces integer not null,
    foreign key (person) references people(id),
    foreign key (flying_day) references flying_days(id),
    unique (flying_day, person)
)""")
cur.execute("""
create table if not exists flying_days_supervisors (
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
    name text not null,
    e_number integer unique,
    keenness real,
    role number,
    notes text,
    tourist integer not null,
    email text not null unique,
    phone text not null,
    password_hash text
)""")

cur.execute("""
create table if not exists people_roles (
    id integer primary key,
    person integer not null,
    role integer not null,
    foreign key (person) references people(id),
    foreign key (role) references roles(id)
)
""")

cur.execute("""
create table if not exists roles (
    id integer primary key,
    name string not null
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

from enum import Enum
class Tourist(Enum):
    LearnToFly = 0
    NotSure = 1
    ExperienceGliding = 2

@dataclass
class Person:
    id: int
    name: str
    email: str
    phone: str
    e_number: int | None
    keenness: float | None
    role: str | None
    notes: str | None
    tourist: Tourist

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
    by_phone = list(cur.execute("select id from people where phone = ?", (phone,)))
    if len(by_phone) == 1:
        return by_phone[0][0]
    by_email = list(cur.execute("select id from people where email = ?", (email,)))
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
        reported_trial = row[indices["trial"]] == "Yes"
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
            person_id = next(cur.execute("insert into people (name, tourist, email, phone) values (?, ?, ?, ?) returning id", (name, 1, email, phone)))[0]

        cur.execute(
            "insert into signups (person, completed_datetime, reported_trial, attending_briefing, available_days, has_car, has_bike, notes) values (?, ?, ?, ?, ?, ?, ?, ?)",
            (person_id, start.timestamp(), reported_trial, False, available_days, car, False, notes)
        )

    db.commit()


from argon2 import PasswordHasher
password_hasher = PasswordHasher()

def make_account(db, email, phone, name, password, tourist):
    email = email.strip()
    phone = phone.strip()
    name = name.strip()
    cur = db.cursor()
    existing_emails = list(cur.execute("select id, password_hash from people where email = ?", (email,)))
    if len(existing_emails) > 0:
        id, ph = existing_emails[0]
    else:
        id = None
        ph = None

    # case 1: user exists and has password, trying to register again
    if id != None and ph != None:
        return None

    hash = password_hasher.hash(password)

    # case 2: user already in db, but not registered (doesn't have a password yet)
    if id != None and ph == None:
        cur.execute("update people set password_hash = ?, name = ?, email = ?, phone = ?, tourist = ? where id = ?", (hash, name, email, phone, tourist, id))

    # case 3: user not in db
    if id == None:
        id = next(cur.execute("insert into people (name, tourist, email, phone, password_hash) values (?, ?, ?, ?, ?) returning id", (name, tourist, email, phone, hash)))[0]

    db.commit()
    return id
        
def ingest_one_signup(db, person_id: int, reported_trial, briefing, available_days, notes, car, bike):
    cur = db.cursor()
    submit_time = datetime.datetime.now().timestamp()

    # name = name.strip()
    # email = email.strip()
    # phone = phone.strip()

    # person_id = find_person_by_details(db, name, email, phone)
    # if person_id is None:
    #     person_id = next(cur.execute("insert into people (name, tourist, email, phone) values (?, ?, ?, ?) returning id", (name, tourist, email, phone)))[0]

    # cur.execute("update people set tourist = ? where id = ?", (person_id, tourist))

    cur.execute(
        "insert into signups (person, completed_datetime, reported_trial, attending_briefing, available_days, has_car, has_bike, notes) values (?, ?, ?, ?, ?, ?, ?, ?)",
        (person_id, submit_time, reported_trial, briefing, available_days, car, bike, notes)
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

def person_info(db, person_id: int) -> Person | None:
    cur = db.cursor()
    # take the latest briefing for each person
    result = list(cur.execute("select p.id, p.name, p.email, p.phone, p.e_number, p.keenness, p.role, p.notes, p.tourist, b.date, b.score from people as p left join briefings as b on p.id = b.person where p.id = ? order by b.date desc limit 1", (person_id,)))
    if len(result) == 0:
        return None
    # assert not (len(result) > 1), "More than one person for the same ID"
    p = result[0]
    print(p)
    return Person(p[0], p[1], p[2], p[3], p[4], p[5], p[6], p[7], p[8], datetime.datetime.fromtimestamp(p[9]) if p[9] is not None else None, p[10])

def num_flying_days(db, person):
    cur = db.cursor()
    count = next(cur.execute("select count(1) from flying_days_people where person = ?1 limit 1", (person,)))[0]
    fudge_factor = list(cur.execute("select flying_days from legacy_info where person = ?", (person,)))
    if len(fudge_factor) > 0:
        count += fudge_factor[0][0]
    return count

@dataclass
class FlyingDay:
    id: int | None
    date: datetime.datetime
    supervise: list[int]
    transport: list[(int, int)]
    instruct: list[int]
    attend: list[int]
    notes: str | None

    def to_json(self):
        return {
            "id": self.id,
            "date": self.date.timestamp(),
            "supervise": self.supervise,
            "transport": self.transport,
            "instruct": self.instruct,
            "attend": self.attend,
            "notes": self.notes
        }

    def from_json(data):
        return FlyingDay(
            data.get("id"),
            datetime.datetime.fromtimestamp(data["date"]),
            data["supervise"],
            [(a, b) for a, b in data["transport"]],
            data["instruct"],
            data["attend"],
            data.get("notes"),
        )

def get_flying_day(db, id: int) -> FlyingDay:
    cur = db.cursor()
    date, notes = next(cur.execute("select date, notes from flying_days where id = ?", (id,)))
    day = FlyingDay(id, datetime.datetime.fromtimestamp(date), [], [], [], [], notes)
    day.instruct = [i[0] for i in cur.execute("select person from flying_days_instructors where flying_day = ?", (id,))]
    day.supervise = [i[0] for i in cur.execute("select person from flying_days_supervisors where flying_day = ?", (id,))]
    day.attend = [i[0] for i in cur.execute("select person from flying_days_people where flying_day = ?", (id,))]
    day.transport = list(cur.execute("select person, spaces from flying_days_transporters where flying_day = ?", (id,)))
    return day

def list_flying_days(db) -> list[int]:
    cur = db.cursor()
    return [i[0] for i in cur.execute("select id from flying_days")]

def last_flying_days(db, person):
    cur = db.cursor()
    pass

def add_flying_day(db, day: FlyingDay):
    cur = db.cursor()
    if day.id is None:
        day.id = next(cur.execute("insert into flying_days (date, notes) values (?,  ?) returning id", (day.date.timestamp(), day.notes)))[0]
    else:
        cur.execute("insert into flying_days (id, date, notes) values (?, ?, ?)", (day.id, day.date.timestamp(), day.notes))
    for person in day.attend:
        cur.execute("insert into flying_days_people (flying_day, person) values (?, ?)", (day.id, person))
    for person in day.instruct:
        cur.execute("insert into flying_days_instructors (flying_day, person) values (?, ?)", (day.id, person))
    for person, spaces in day.transport:
        cur.execute("insert into flying_days_transporters (flying_day, person, spaces) values (?, ?, ?)", (day.id, person, spaces))
    for person in day.supervise:
        cur.execute("insert into flying_days_supervisors (flying_day, person) values (?, ?)", (day.id, person))
    db.commit()

def add_briefing(db, date: datetime.datetime, people_scores: list[(int, float)]):
    cur = db.cursor()
    cur.executemany("insert into briefings (person, date, score) values (?, ?, ?)", [(person, date.timestamp(), score) for person, score in people_scores])
    db.commit()

# flying_days = [next(cur.execute("insert into flying_days (date, instruct, drive, supervise) values (?, ?, ?, ?) returning id", (0, 0, 0, 0)))[0] for _ in range(50)]

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

            person_id = next(cur.execute("insert into people (name, e_number, keenness, notes, tourist, email, phone) values (?, ?, ?, ?, ?, ?, ?) returning id", (name, e, keenness, notes, 1, emails[0] if len(emails) > 0 else "", phone)))[0]
            # for email in emails:
            #     cur.execute("insert into emails (person, email) values (?, ?)", (person_id, email))

            # if phone != "":
            #     cur.execute("insert into phones (person, phone) values (?, ?)", (person_id, phone))

            # for i in range(signups):
            #     cur.execute("insert into signups (person, completed_datetime, available_days, notes, reported_trial, attending_briefing, has_car) values (?, ?, ?, ?, ?, ?, ?)", (person_id, 0, 0, None, False, False, False))
            # for i in range(flying):
            #     cur.execute("insert into flying_days_people (flying_day, person) values (?, ?)", (flying_days[i], person_id))
            cur.execute("insert into legacy_info (person, signups, flying_days) values (?, ?, ?)", (person_id, signups, flying))

            if briefing_date is not None and briefing_score is not None:
                add_briefing(con, briefing_date, [(person_id, briefing_score)])

    cur.execute("insert into people (name, e_number, keenness, notes, tourist, email, phone) values (?, ?, ?, ?, ?, ?, ?)", ("James Kitching", "E1552", None, None, 0, "s2419438@ed.ac.uk", "+44 7729401806"))
    a = next(cur.execute("insert into roles (name) values (?) returning id", ("committee",)))
    person = next(cur.execute("select id from people where name = ?", ("James Kitching",)))
    cur.execute("insert into people_roles (person, role) values (?, ?)", (person[0], a[0]))
    print("AAAAAAAA", a)
    con.commit()

    paths = [
     "Edinburgh University Gliding Club Sem2 2025_2026(1-7).xlsx",
     "Edinburgh University Gliding Club Sem2 2025_2026(1-8).xlsx",
    ]
    for path in paths:
        with open("/home/james/Downloads/"+path, "rb") as f:
            # data = f.read()
            ingest_signups(con, read_excel(f))
    con.commit()
    # days = [
    #     FlyingDay(None, datetime.datetime(2026, 8, 2),  [10], [[4, 1], [5, 1], [6, 1]], [1, 2], [], None),
    # ]

    # for day in days:
    #     add_flying_day(con, day)
    # con.commit()

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
    cols[0].append(str(info.name))
    cols[1].append(("E" + str(info.e_number)) if info.e_number is not None else "")
    cols[2].append(info.email)
    cols[3].append(info.phone)
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
