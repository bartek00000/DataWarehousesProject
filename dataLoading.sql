USE MarbleGuestRequest;
GO

-- 1. Load Dimension: BRANCH (przez tabelę tymczasową bez kolumny ID)
CREATE TABLE #TempBranch (
    Name VARCHAR(30) NOT NULL
);
GO

BULK INSERT #TempBranch s
FROM 'c:\Users\barte\Documents\studia\PG\DataWarehouses\laboratories\project\branch.bulk'
WITH (FIELDTERMINATOR='|', ROWTERMINATOR='\n');
GO

INSERT INTO BRANCH (Name)
SELECT Name FROM #TempBranch;
GO

DROP TABLE #TempBranch;
GO

-- 2. Load Dimension: EMPLOYEE
BULK INSERT EMPLOYEE
FROM 'c:\Users\barte\Documents\studia\PG\DataWarehouses\laboratories\project\employee.bulk'
WITH (FIELDTERMINATOR='|', ROWTERMINATOR='\n');
GO

-- 3. Load Dimension: GUEST (przez tabelę tymczasową bez kolumny ID)
CREATE TABLE #TempGuest (
    FirstName VARCHAR(30) NOT NULL,
    LastName VARCHAR(40) NOT NULL,
    DateOfBirth DATE NOT NULL,
    Email VARCHAR(50) NULL,
    PhoneNumber VARCHAR(15) NULL
);
GO

BULK INSERT #TempGuest
FROM 'c:\Users\barte\Documents\studia\PG\DataWarehouses\laboratories\project\guest.bulk'
WITH (FIELDTERMINATOR='|', ROWTERMINATOR='\n');
GO

INSERT INTO GUEST (FirstName, LastName, DateOfBirth, Email, PhoneNumber)
SELECT FirstName, LastName, DateOfBirth, Email, PhoneNumber FROM #TempGuest;
GO

DROP TABLE #TempGuest;
GO

-- 4. Load Dimension: ROOM
BULK INSERT ROOM
FROM 'c:\Users\barte\Documents\studia\PG\DataWarehouses\laboratories\project\room.bulk'
WITH (FIELDTERMINATOR='|', ROWTERMINATOR='\n');
GO

-- 5. Load Fact: STAY
BULK INSERT STAY
FROM 'c:\Users\barte\Documents\studia\PG\DataWarehouses\laboratories\project\stay.bulk'
WITH (FIELDTERMINATOR='|', ROWTERMINATOR='\n');
GO

-- 6. Load Fact: REQUEST
BULK INSERT REQUEST
FROM 'c:\Users\barte\Documents\studia\PG\DataWarehouses\laboratories\project\request.bulk'
WITH (FIELDTERMINATOR='|', ROWTERMINATOR='\n');
GO

-- 7. Load Fact: SURVEY
BULK INSERT SURVEY
FROM 'c:\Users\barte\Documents\studia\PG\DataWarehouses\laboratories\project\survey.bulk'
WITH (FIELDTERMINATOR='|', ROWTERMINATOR='\n');
GO