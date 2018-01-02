import sqlite3
db = sqlite3.connect("sessions.db")
c = db.cursor()
c.execute("DELETE FROM sessions")
db.commit()
db.close()