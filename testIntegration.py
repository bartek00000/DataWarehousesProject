import pandas as pd

# Load the external CSV data
csv_employees = pd.read_csv('hotel_employees.csv')

# Load the database fact data (using the pipe separator you defined)
db_requests = pd.read_csv('request.bulk', sep='|', header=None, 
                          names=['RequestID', 'FK_StayID', 'FK_EmployeeID', 'Category', 'RequestTime', 'ResolutionTime', 'ManagerIntervention'])

# Attempt to integrate the two sources using the business key
integrated_data = pd.merge(db_requests, csv_employees, left_on='FK_EmployeeID', right_on='EmployeeID', how='inner')

# Calculate the integration success rate
total_requests = len(db_requests)
integrated_requests = len(integrated_data)

print(f"Total Database Requests: {total_requests}")
print(f"Requests Successfully Linked to CSV Employees: {integrated_requests}")
if total_requests == integrated_requests:
    print("Verification Passed: 100% Data Integration via EmployeeID Business Key.")