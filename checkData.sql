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

-- Num of employees hired in t1 and t2
SELECT
    Role,
    CASE
        WHEN DateOfAcceptance <= '2024-12-31' THEN 'T1 (hired before)'
        ELSE 'T2 (hired after)'
    END AS hiring_time,
    COUNT(*) AS NumberOfEmployees
FROM HOTEL_EMPLOYEE_DETAILS
GROUP BY
    Role,
     CASE
        WHEN DateOfAcceptance <= '2024-12-31' THEN 'T1 (hired before)'
        ELSE 'T2 (hired after)'
    END
    ORDER BY Role;

-- checking new Head Manager...
SELECT * FROM HOTEL_EMPLOYEE_DETAILS
    WHERE EmployeeID = 'EMP0021' AND DateOfAcceptance <= '2024-12-31'
SELECT * FROM HOTEL_EMPLOYEE_DETAILS
    WHERE EmployeeID = 'EMP0021' AND DateOfAcceptance > '2024-12-31'

-- Head managers cannot handle any requests
SELECT r.RequestID, r.FK_EmployeeID, e.Name, e.SurnamE
FROM REQUEST r
JOIN EMPLOYEE e ON r.FK_EmployeeID = e.EmployeeID
WHERE e.EmployeeID IN (
    SELECT EmployeeID FROM HOTEL_EMPLOYEE_DETAILS WHERE Role = 'Head Manager' AND r.RequestTime >  DateOfAcceptance
)

-- Verify room additions
SELECT
    FK_BranchID,
    SUM(CASE WHEN CAST(SUBSTRING(RoomID, 2, LEN(RoomID)) AS INT) <= 1400 THEN 1 ELSE 0 END) AS T1_RoomsCount,
    SUM(CASE WHEN CAST(SUBSTRING(RoomID, 2, LEN(RoomID)) AS INT) > 1400 THEN 1 ELSE 0 END) AS T2_NewRoomsExpanded,
    COUNT(*) AS TotalRoomsPerBranch
FROM ROOM
GROUP BY FK_BranchID
ORDER BY FK_BranchID

-- Verify dimension change; check if roles changed properly between T1 and T2 for promoted staff
SELECT EmployeeID, FirstName, LastName, Role, DateOfAcceptance
FROM HOTEL_EMPLOYEE_DETAILS
WHERE Role = 'Head Manager'

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
)

SELECT SurveyID, OverallRating, StaffRating, ResponseRating
FROM SURVEY
WHERE OverallRating < 1 OR OverallRating > 10
   OR StaffRating < 1 OR StaffRating > 10
   OR ResponseRating < 1 OR ResponseRating > 10;

SELECT StayID, CheckinDate, CheckOutDate
FROM STAY
WHERE CheckOutDate <= CheckinDate

SELECT RequestID, RequestTime, ResolutionTime
FROM REQUEST
WHERE ResolutionTime <= RequestTime


/* checking if guests with stay that did not fill in the survey */
Select GuestID, COUNT(StayID), COUNT(SurveyID) AS survey_count from GUEST
	JOIN STAY ON GuestID=FK_GuestID
	LEFT JOIN SURVEY ON StayID=FK_STAYID
GROUP BY GuestID HAVING COUNT(SurveyID) < 1;

/* checking if some rooms having more than one guest in a room during one stay */
SELECT
    FK_RoomID,
    CheckInDate,
    CheckOutDate,
    COUNT(FK_GuestID) AS guest_count,
    STRING_AGG(CAST(FK_GuestID AS VARCHAR), ', ') AS guest_ids,
    STRING_AGG(StayID, ', ') AS stay_ids
FROM STAY
GROUP BY FK_RoomID, CheckInDate, CheckOutDate
HAVING COUNT(FK_GuestID) >= 1
ORDER BY guest_count DESC, CheckInDate;