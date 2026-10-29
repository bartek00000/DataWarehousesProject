CREATE DATABASE MarbleGuestRequest
GO

USE MarbleGuestRequest;
GO

CREATE TABLE #TempBranch (
    Name VARCHAR(30) NOT NULL
);
GO

BULK INSERT #TempBranch 
FROM 'c:\Users\barte\Documents\studia\PG\DataWarehouses\laboratories\project\branch.bulk'
WITH (FIELDTERMINATOR='|', ROWTERMINATOR='\n');
GO

INSERT INTO BRANCH (Name)
SELECT Name FROM #TempBranch;
GO

DROP TABLE #TempBranch;
GO

BULK INSERT EMPLOYEE
FROM 'c:\Users\barte\Documents\studia\PG\DataWarehouses\laboratories\project\employee.bulk'
WITH (FIELDTERMINATOR='|', ROWTERMINATOR='\n');
GO

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

BULK INSERT ROOM
FROM 'c:\Users\barte\Documents\studia\PG\DataWarehouses\laboratories\project\room.bulk'
WITH (FIELDTERMINATOR='|', ROWTERMINATOR='\n');
GO

BULK INSERT STAY
FROM 'c:\Users\barte\Documents\studia\PG\DataWarehouses\laboratories\project\stay.bulk'
WITH (FIELDTERMINATOR='|', ROWTERMINATOR='\n');
GO

BULK INSERT REQUEST
FROM 'c:\Users\barte\Documents\studia\PG\DataWarehouses\laboratories\project\request.bulk'
WITH (FIELDTERMINATOR='|', ROWTERMINATOR='\n');
GO

BULK INSERT SURVEY
FROM 'c:\Users\barte\Documents\studia\PG\DataWarehouses\laboratories\project\survey.bulk'
WITH (FIELDTERMINATOR='|', ROWTERMINATOR='\n');
GO