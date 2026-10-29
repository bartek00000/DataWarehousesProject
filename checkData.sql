USE MarbleGuestRequest;
GO

SELECT 
    CASE 
        WHEN CheckinDate <= '2024-12-31' THEN 'T1 (Historical Snapshot)' 
        ELSE 'T2 (Incremental Snapshot)' 
    END AS Snapshot_Period,
    COUNT(*) AS NumberOfStays
FROM STAY
GROUP BY 
    CASE 
        WHEN CheckinDate <= '2024-12-31' THEN 'T1 (Historical Snapshot)' 
        ELSE 'T2 (Incremental Snapshot)' 
    END;

SELECT EmployeeID, Name, Surname 
FROM EMPLOYEE 
WHERE EmployeeID LIKE 'EMP0001%';

SELECT 
    FK_EmployeeID, 
    COUNT(*) AS HandledRequests,
    MIN(RequestTime) AS FirstRequestTime, 
    MAX(RequestTime) AS LastRequestTime
FROM REQUEST
WHERE FK_EmployeeID LIKE 'EMP0001%'
GROUP BY FK_EmployeeID;

SELECT TOP 50 
    FK_BranchID, 
    RoomID, 
    RoomNumber
FROM ROOM
WHERE FK_BranchID = 1
ORDER BY CAST(RoomNumber AS INT);

SELECT 
    FK_BranchID,
    (CAST(RoomNumber AS INT) / 100) AS FloorNumber,
    COUNT(*) AS RoomsOnFloor
FROM ROOM
GROUP BY 
    FK_BranchID, 
    (CAST(RoomNumber AS INT) / 100)
ORDER BY 
    FK_BranchID, 
    FloorNumber;

SELECT 
    b.BranchID,
    b.Name AS BranchName,
    COUNT(s.StayID) AS TotalStays
FROM BRANCH b
JOIN ROOM rm ON b.BranchID = rm.FK_BranchID
JOIN STAY s ON rm.RoomID = s.FK_RoomID
GROUP BY b.BranchID, b.Name
ORDER BY b.BranchID;

SELECT 
    FK_BranchID,
    RoomNumber,
    COUNT(*) AS TimesUsedInBranch
FROM ROOM
GROUP BY FK_BranchID, RoomNumber
HAVING COUNT(*) > 1;

SELECT DISTINCT ApartmentType 
FROM ROOM 
WHERE ApartmentType NOT IN ('Standard', 'Deluxe', 'Superior');

SELECT DISTINCT MealOffer 
FROM STAY 
WHERE MealOffer NOT IN ('None', 'Breakfast Only', 'Supper Only', 'Breakfast and Supper');

SELECT DISTINCT Category 
FROM REQUEST 
WHERE Category NOT IN (
    'extra pillows', 'amenities restock', 'additional toilet paper', 
    'ordering room service', 'towel exchange', 'wake-up call', 
    'transportation request', 'equipment issue', 'ordering a meal to a specific room', 
    'loud neighbor complaint', 'bad service complaint', 'other complaint'
);

SELECT SurveyID, OverallRating, StaffRating, ResponseRating
FROM SURVEY 
WHERE OverallRating < 1 OR OverallRating > 10
   OR StaffRating < 1 OR StaffRating > 10
   OR ResponseRating < 1 OR ResponseRating > 10;

SELECT StayID, CheckinDate, CheckOutDate
FROM STAY
WHERE CheckOutDate <= CheckinDate;

SELECT RequestID, RequestTime, ResolutionTime
FROM REQUEST
WHERE ResolutionTime <= RequestTime;


-- VERIFYING SURVEY MANDATORY 1:1 RELATIONSHIP
SELECT StayID 
FROM STAY 
WHERE StayID NOT IN (SELECT FK_StayID FROM SURVEY);

SELECT FK_StayID, COUNT(SurveyID) AS SurveyCount
FROM SURVEY
GROUP BY FK_StayID
HAVING COUNT(SurveyID) > 1;