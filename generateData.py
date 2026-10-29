import pandas as pd
from faker import Faker
import random
from datetime import datetime, timedelta
# Set seeds for reproducibility
random.seed(42)
Faker.seed(42)
fake = Faker()

# Configuration for Scalability
NUM_BRANCHES = 10
NUM_EMPLOYEES = 500
NUM_ROOMS = 1500
NUM_GUESTS = 25000
NUM_STAYS_T1 = 8000  # Scale this up to ~250,000 to reach 1,000,000 total fact rows (Stays + Requests + Surveys)
NUM_STAYS_T2 = 2000
CUTOFF_DATE = datetime(2024, 12, 31)

# Allowed values defined by the schema requirements
MEAL_OFFERS = ['None', 'Breakfast Only', 'Supper Only', 'Breakfast and Supper']
ROOM_TYPES = ['Standard', 'Deluxe', 'Superior']
REQUEST_CATEGORIES = [
    'extra pillows', 'amenities restock', 'additional toilet paper', 
    'ordering room service', 'towel exchange', 'wake-up call', 
    'transportation request', 'equipment issue', 'ordering a meal to a specific room', 
    'loud neighbor complaint', 'bad service complaint', 'other complaint'
]
ROLES = ['Receptionist', 'Housekeeper', 'Technician', 'Head Manager', 'Kitchen staff']
EDUCATION = ['Middle school', 'Graduate', 'First degree', 'Second degree']

# 1. Generate Dimensions
branches_data = []
for i in range(1, NUM_BRANCHES + 1):
    branches_data.append({
        'BranchID': i,
        'Branch Name': f'Marble {fake.city()}',
        'City': fake.city(),
        'Address': fake.street_address(),
        'Postal code': fake.postcode(),
        'Year opened': random.randint(1990, 2023)
    })
df_branches_csv = pd.DataFrame(branches_data)
df_branches_db = df_branches_csv[['BranchID', 'Branch Name']].rename(columns={'Branch Name': 'Name'})

employees_csv_list = []
employees_db_list = []
for i in range(1, NUM_EMPLOYEES + 1):
    emp_id = f'EMP{i:04d}'
    fname, lname = fake.first_name(), fake.last_name()
    employees_csv_list.append({
        'EmployeeID': emp_id,
        'FK_BranchID': random.randint(1, NUM_BRANCHES),
        'FirstName': fname,
        'LastName': lname,
        'Role': random.choice(ROLES),
        'Education': random.choice(EDUCATION),
        'Date of acceptance for work on the current position': fake.date_between(start_date='-5y', end_date='-2y').strftime('%Y-%m-%d'),
        'Date of birth': fake.date_of_birth(minimum_age=20, maximum_age=60).strftime('%Y-%m-%d')
    })
    employees_db_list.append({'EmployeeID': emp_id, 'Name': fname, 'Surname': lname})

df_guests = pd.DataFrame([{
    'GuestID': i,
    'FirstName': fake.first_name(),
    'LastName': fake.last_name(),
    'DateOfBirth': fake.date_of_birth(minimum_age=18, maximum_age=80).strftime('%Y-%m-%d'),
    'Email': fake.email(),
    'PhoneNumber': fake.numerify('###########')
} for i in range(1, NUM_GUESTS + 1)])

df_rooms = pd.DataFrame([{
    'RoomID': f'R{i:05d}',
    'FK_BranchID': random.randint(1, NUM_BRANCHES),
    'RoomNumber': str(100 + (i % 500)), # Resets room numbers per branch roughly
    'ApartmentType': random.choice(ROOM_TYPES)
} for i in range(1, NUM_ROOMS + 1)])

# 2. Generate Fact Rows (T1 & T2 logic)
def generate_stay(stay_id, is_t2=False):
    start_window = CUTOFF_DATE + timedelta(days=1) if is_t2 else CUTOFF_DATE - timedelta(days=730)
    end_window = CUTOFF_DATE + timedelta(days=90) if is_t2 else CUTOFF_DATE
    checkin = fake.date_time_between(start_date=start_window, end_date=end_window)
    checkout = checkin + timedelta(days=random.randint(1, 7))
    return {
        'StayID': f'STAY{stay_id:07d}',
        'FK_GuestID': random.randint(1, NUM_GUESTS),
        'FK_RoomID': random.choice(df_rooms['RoomID'].tolist()),
        'CheckinDate': checkin.strftime('%Y-%m-%d %H:%M:%S'),
        'CheckOutDate': checkout.strftime('%Y-%m-%d %H:%M:%S'),
        'MealOffer': random.choice(MEAL_OFFERS)
    }

stays, requests, surveys = [], [], []
request_id_counter, survey_id_counter = 1, 1

# Generate T1 Stays
for i in range(1, NUM_STAYS_T1 + 1):
    stays.append(generate_stay(i, is_t2=False))

# --- T2: DIMENSION CHANGE ---
# Promote EMP0001 from their current role to 'Head Manager'
promoted_emp = employees_csv_list[0].copy()
promoted_emp['EmployeeID'] = 'EMP0001-V2'
promoted_emp['Role'] = 'Head Manager'
promoted_emp['Date of acceptance for work on the current position'] = (CUTOFF_DATE + timedelta(days=2)).strftime('%Y-%m-%d')
employees_csv_list.append(promoted_emp)
employees_db_list.append({'EmployeeID': 'EMP0001-V2', 'Name': promoted_emp['FirstName'], 'Surname': promoted_emp['LastName']})

# Generate T2 Stays
for i in range(NUM_STAYS_T1 + 1, NUM_STAYS_T1 + NUM_STAYS_T2 + 1):
    stays.append(generate_stay(i, is_t2=True))

# Generate Requests and Surveys for all stays
for stay in stays:
    checkin_dt = datetime.strptime(stay['CheckinDate'], '%Y-%m-%d %H:%M:%S')
    
    # Generate 1 to 4 requests per stay
    for _ in range(random.randint(1, 4)):
        req_time = checkin_dt + timedelta(hours=random.randint(1, 48))
        res_time = req_time + timedelta(minutes=random.randint(15, 120))
        
        emp_choice = random.choice(employees_db_list)['EmployeeID']
        
        # Prevent the future V2 ID from being used in the past (T1)
        if emp_choice == 'EMP0001-V2' and req_time <= CUTOFF_DATE:
            emp_choice = 'EMP0001'
            
        # Upgrade the old V1 ID to the new V2 ID in the future (T2)
        elif emp_choice == 'EMP0001' and req_time > CUTOFF_DATE:
            emp_choice = 'EMP0001-V2'
            
        requests.append({
            'RequestID': f'REQ{request_id_counter:08d}',
            'FK_StayID': stay['StayID'],
            'FK_EmployeeID': emp_choice,
            'Category': random.choice(REQUEST_CATEGORIES),
            'RequestTime': req_time.strftime('%Y-%m-%d %H:%M:%S'),
            'ResolutionTime': res_time.strftime('%Y-%m-%d %H:%M:%S'),
            'ManagerIntervention': random.choice([0, 1])
        })
        request_id_counter += 1
        
    # Generate 1 survey per stay
    surveys.append({
        'SurveyID': f'SUR{survey_id_counter:07d}',
        'FK_StayID': stay['StayID'],
        'OverallRating': random.randint(1, 10),
        'StaffRating': random.randint(1, 10),
        'ResponseRating': random.randint(1, 10)
    })
    survey_id_counter += 1

# 3. Export Data
df_branches_csv = pd.DataFrame(branches_data)
pd.DataFrame(employees_csv_list).to_csv('hotel_employees.csv', index=False, sep=',')
df_branches_csv.to_csv('hotel_branches.csv', index=False, sep=',')

df_branches_db.to_csv('branch.bulk', index=False, header=False, sep='|')
pd.DataFrame(employees_db_list).to_csv('employee.bulk', index=False, header=False, sep='|')
df_guests.to_csv('guest.bulk', index=False, header=False, sep='|')
df_rooms.to_csv('room.bulk', index=False, header=False, sep='|')
pd.DataFrame(stays).to_csv('stay.bulk', index=False, header=False, sep='|')
pd.DataFrame(requests).to_csv('request.bulk', index=False, header=False, sep='|')
pd.DataFrame(surveys).to_csv('survey.bulk', index=False, header=False, sep='|')

print("Data generation complete. Exported CSVs and BULK files.")