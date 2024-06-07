import sqlite3

conn = sqlite3.connect('../courseDataset.db')
print("Connected to database successfully")

conn.executescript("""
   
   CREATE TABLE Users (
   Id INTEGER PRIMARY KEY AUTOINCREMENT,
   UserName VARCHAR(50) NOT NULL,
   Email VARCHAR(50) NOT NULL UNIQUE,
   PasswordHash VARCHAR(50) NOT NULL,
   JoinDate DATE NOT NULL,
   UserRole INTEGER NOT NULL,
FOREIGN KEY (UserRole) REFERENCES UserRoles(Id)
);

CREATE TABLE UserRoles (
   Id INTEGER PRIMARY KEY AUTOINCREMENT,
   Role VARCHAR(50) NOT NULL
);

CREATE TABLE Courses (
   Id INTEGER PRIMARY KEY AUTOINCREMENT,
   Title VARCHAR(50) NOT NULL,
   Description VARCHAR(50),
   InstructorId INTEGER NOT NULL,
   StartDate DATE NOT NULL,
   EndDate DATE NULL,
   AddingDate DATE NOT NULL,
   CategoryId INTEGER NOT NULL,
   CourseAvatarPath VARCHAR(200),
FOREIGN KEY (InstructorId) REFERENCES Users(Id),
FOREIGN KEY (CategoryId) REFERENCES CourseCategories(Id)
);

CREATE TABLE CourseCategories (
   Id INTEGER PRIMARY KEY AUTOINCREMENT,
   Name VARCHAR(50) NOT NULL
);

CREATE TABLE Enrollments (
   Id INTEGER PRIMARY KEY AUTOINCREMENT,
   UserId INTEGER NOT NULL,
   CourseId INTEGER NOT NULL UNIQUE,
   EnrollmentDate DATE NOT NULL,
   CompletionStatus INTEGER,
FOREIGN KEY (UserId) REFERENCES Users(Id),
FOREIGN KEY (CourseId) REFERENCES Courses(Id)
FOREIGN KEY (CompletionStatus) REFERENCES Statuses(Id)
);

CREATE TABLE Statuses (
   Id INTEGER PRIMARY KEY AUTOINCREMENT,
   Name VARCHAR(50) NOT NULL
);

CREATE TABLE CourseResources (
   Id INTEGER PRIMARY KEY AUTOINCREMENT,
   CourseId INTEGER NOT NULL,
   ResourceType INTEGER NOT NULL,
   Title VARCHAR(50) NOT NULL,
   Path VARCHAR(50),
FOREIGN KEY (ResourceType) REFERENCES ResourceTypes(Id),
FOREIGN KEY (CourseId) REFERENCES Courses(Id)
);

CREATE TABLE ResourceTypes (
   Id INTEGER PRIMARY KEY AUTOINCREMENT,
   Name VARCHAR(50) NOT NULL
);

CREATE TABLE Reviews (
   Id INTEGER PRIMARY KEY AUTOINCREMENT,
   UserId INTEGER NOT NULL,
   CourseId INTEGER NOT NULL,
   Rating INTEGER,
   Name VARCHAR(50),
   ReviewDate DATE NOT NULL,
FOREIGN KEY (UserId) REFERENCES Users(Id),
FOREIGN KEY (CourseId) REFERENCES Courses(Id)
);

CREATE TABLE CommunityDiscussions (
   Id INTEGER PRIMARY KEY AUTOINCREMENT,
   UserId INTEGER NOT NULL,
   CourseId INTEGER NOT NULL,
   Title VARCHAR(50),
   Content VARCHAR(50),
   PostDate Date Not Null,
FOREIGN KEY (UserId) REFERENCES Users(Id),
FOREIGN KEY (CourseId) REFERENCES Courses(Id)
);

CREATE TABLE Authentication (
   Id INTEGER PRIMARY KEY AUTOINCREMENT,
   UserId INTEGER NOT NULL,
   LoginSuccess BOOLEAN,
   LoginDate Date Not Null,
FOREIGN KEY (UserId) REFERENCES Users(Id)
);

""")
print("Created tables successfully!")

conn.close()