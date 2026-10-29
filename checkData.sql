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

---Verifying Data Integration via Business Keys

