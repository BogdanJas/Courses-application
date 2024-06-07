import sqlite3

conn = sqlite3.connect('../courseDataset.db')
print("Connected to database successfully")

conn.executescript("""INSERT INTO UserRoles(Role) VALUES ('Student'), ('Instructor'), ('Admin');
INSERT INTO Statuses(Name) VALUES ('Enrolled'), ('Started'), ('In progress'), ('Done');
INSERT INTO ResourceTypes(Name) VALUES ('Video'), ('PDF'), ('Article'), ('External link');
INSERT INTO CourseCategories(Name) VALUES ('Literature'), ('Economy'), ('Math'), ('Compter Science');
""")
print("Inserted values to the tables successfully!")

conn.close()