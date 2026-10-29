-- Dimension: BRANCH
CREATE TABLE BRANCH (
    BranchID INT PRIMARY KEY,
    Name VARCHAR(30)
)
GO

-- Dimension: EMPLOYEE
CREATE TABLE EMPLOYEE (
    EmployeeID VARCHAR(11) PRIMARY KEY,
    Name VARCHAR(15),
    Surname VARCHAR(30)
)
GO

-- Dimension: GUEST
CREATE TABLE GUEST (
    GuestID INT IDENTITY(1,1) PRIMARY KEY,
    FirstName VARCHAR(30) NOT NULL,
    LastName VARCHAR(40) NOT NULL,
    DateOfBirth DATE NOT NULL,
    Email VARCHAR(50),
    PhoneNumber VARCHAR(15)
)
GO

-- Dimension: ROOM
CREATE TABLE ROOM (
    RoomID VARCHAR(10) PRIMARY KEY,
    FK_BranchID INT NOT NULL,
    RoomNumber VARCHAR(10) NOT NULL,
    ApartmentType VARCHAR(20) NOT NULL,
    FOREIGN KEY (FK_BranchID) REFERENCES BRANCH(BranchID),
    CHECK (ApartmentType IN ('Standard', 'Deluxe', 'Superior'))
)
GO

-- Fact: STAY
CREATE TABLE STAY (
    StayID VARCHAR(15) PRIMARY KEY,
    FK_GuestID INT NOT NULL,
    FK_RoomID VARCHAR(10) NOT NULL,
    CheckinDate DATETIME NOT NULL,
    CheckOutDate DATETIME NOT NULL,
    MealOffer VARCHAR(20) NOT NULL,
    FOREIGN KEY (FK_GuestID) REFERENCES GUEST(GuestID),
    FOREIGN KEY (FK_RoomID) REFERENCES ROOM(RoomID),
    CHECK (MealOffer IN ('None', 'Breakfast Only', 'Supper Only', 'Breakfast and Supper'))
)
GO

-- Fact: REQUEST
CREATE TABLE REQUEST (
    RequestID VARCHAR(15) PRIMARY KEY,
    FK_StayID VARCHAR(15) NOT NULL,
    FK_EmployeeID VARCHAR(11) NOT NULL,
    Category VARCHAR(50) NOT NULL,
    RequestTime DATETIME NOT NULL,
    ResolutionTime DATETIME,
    ManagerIntervention BIT NOT NULL,
    FOREIGN KEY (FK_StayID) REFERENCES STAY(StayID),
    FOREIGN KEY (FK_EmployeeID) REFERENCES EMPLOYEE(EmployeeID),
    CHECK (Category IN (
        'extra pillows', 'amenities restock', 'additional toilet paper', 
        'ordering room service', 'towel exchange', 'wake-up call', 
        'transportation request', 'equipment issue', 'ordering a meal to a specific room', 
        'loud neighbor complaint', 'bad service complaint', 'other complaint'
    ))
)
GO

-- Fact: SURVEY
CREATE TABLE SURVEY (
    SurveyID VARCHAR(15) PRIMARY KEY,
    FK_StayID VARCHAR(15) NOT NULL,
    OverallRating INT,
    StaffRating INT,
    ResponseRating INT,
    FOREIGN KEY (FK_StayID) REFERENCES STAY(StayID),
    CHECK (OverallRating BETWEEN 1 AND 10),
    CHECK (StaffRating BETWEEN 1 AND 10),
    CHECK (ResponseRating BETWEEN 1 AND 10)
)
GO