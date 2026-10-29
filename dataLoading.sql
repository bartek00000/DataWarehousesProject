USE MarbleGuestRequest;
GO

-- Load Dimensions
BULK INSERT BRANCH FROM 'c:\Users\barte\Documents\studia\PG\DataWarehouses\laboratories\project\branch.bulk' WITH (FIELDTERMINATOR='|', ROWTERMINATOR='\n');
BULK INSERT EMPLOYEE FROM 'c:\Users\barte\Documents\studia\PG\DataWarehouses\laboratories\project\employee.bulk' WITH (FIELDTERMINATOR='|', ROWTERMINATOR='\n');

-- Use KEEPIDENTITY for the auto-generated GuestID column
BULK INSERT GUEST FROM 'c:\Users\barte\Documents\studia\PG\DataWarehouses\laboratories\project\guest.bulk' WITH (FIELDTERMINATOR='|', ROWTERMINATOR='\n', KEEPIDENTITY);

BULK INSERT ROOM FROM 'c:\Users\barte\Documents\studia\PG\DataWarehouses\laboratories\project\room.bulk' WITH (FIELDTERMINATOR='|', ROWTERMINATOR='\n');

-- Load Facts
BULK INSERT STAY FROM 'c:\Users\barte\Documents\studia\PG\DataWarehouses\laboratories\project\stay.bulk' WITH (FIELDTERMINATOR='|', ROWTERMINATOR='\n');
BULK INSERT REQUEST FROM 'c:\Users\barte\Documents\studia\PG\DataWarehouses\laboratories\project\request.bulk' WITH (FIELDTERMINATOR='|', ROWTERMINATOR='\n');
BULK INSERT SURVEY FROM 'c:\Users\barte\Documents\studia\PG\DataWarehouses\laboratories\project\survey.bulk' WITH (FIELDTERMINATOR='|', ROWTERMINATOR='\n');