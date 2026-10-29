USE MarbleGuestRequest;
GO

-- 1. Delete data from Fact tables (Child tables)
DELETE FROM SURVEY;
DELETE FROM REQUEST;
DELETE FROM STAY;

-- 2. Delete data from Dimension tables (Parent tables)
DELETE FROM ROOM;
DELETE FROM GUEST;
DELETE FROM EMPLOYEE;
DELETE FROM BRANCH;
GO

-- Optional but recommended: Reset the auto-increment counter for GUEST
DBCC CHECKIDENT ('GUEST', RESEED, 0);
GO