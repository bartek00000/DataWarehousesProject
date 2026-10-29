USE MarbleGuestRequest;
GO

--- Verifying T1 and T2 Snapshots (Fact Row Expansion)

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

--- Verifying the Change in a Dimension Element
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

--- Veryfing room logic :
--- 30 rooms per floor 
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