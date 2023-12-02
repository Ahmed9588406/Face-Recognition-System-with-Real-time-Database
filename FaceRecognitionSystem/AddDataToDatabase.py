import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    "databaseURL": ""
})

ref = db.reference("Participants")

data = {
    "20211495122": {
        "name": "Ahmed Alaa",
        "Major": "AI",
        "starting_year": 2021,
        "total_attendance": 23,
        "standing": "A",
        "year": 4,
        "last_attendance_time": "2023-11-23 00:54:34"

    },
    "20211495123": {
        "name": "Abdelrahman ",
        "Major": "AI",
        "starting_year": 2016,
        "total_attendance": 55,
        "standing": "A",
        "year": 12,
        "last_attendance_time": "2018-11-23 00:54:34"

    },
    "20211495124": {
        "name": "Chris Evans",
        "Major": "Actor",
        "starting_year": 2012,
        "total_attendance": 5,
        "standing": "A",
        "year": 4,
        "last_attendance_time": "2014-11-23 00:54:34"

    }

}

for key, value in data.items():
    ref.child(key).set(value)
