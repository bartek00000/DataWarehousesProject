from datetime import datetime, timedelta
import random
from faker import Faker
import pandas as pd

# Set seeds for reproducibility
random.seed(42)
Faker.seed(42)
fake = Faker()

# Configuration for Scalability
NUM_BRANCHES = 10
NUM_EMPLOYEES_T1 = 450  # Base staff at T1
NUM_ROOMS_T1 = 1400  # Initial rooms at T1
NUM_GUESTS = 25000
NUM_STAYS_T1 = 8000
NUM_STAYS_T2 = 2000
ROOMS_PER_FLOOR = 30
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
ROLES_EXCEPT_MANAGER = ['Receptionist', 'Housekeeper', 'Technician', 'Kitchen staff']
EDUCATION = ['Middle school', 'Graduate', 'First degree', 'Second degree']

# Rating distribution (weighted to ensure average overall rating is close to ~7.0)
RATING_CHOICES = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
RATING_WEIGHTS = [1, 2, 3, 5, 8, 15, 30, 20, 12, 4]

# 1. Generate Dimensions: BRANCHES
branches_data = []
for i in range(1, NUM_BRANCHES + 1):
  branches_data.append({
      'BranchID': i,
      'Branch Name': f'Marble {fake.city()}',
      'City': fake.city(),
      'Address': fake.street_address(),
      'Postal code': fake.postcode(),
      'Year opened': random.randint(1990, 2023),
  })
df_branches_csv = pd.DataFrame(branches_data)
df_branches_db = df_branches_csv[['Branch Name']].rename(
    columns={'Branch Name': 'Name'}
)

# 2. Generate Dimensions: EMPLOYEES (T1 Baseline)
employees_csv_list = []
employees_db_list = []

# Track active status per employee for T1/T2 filtering
employee_meta = {}  # EmpID -> {BranchID, Role, ActiveStatus, IsManager}

# Step A: Exactly 1 Head Manager for each Branch at T1
for b_id in range(1, NUM_BRANCHES + 1):
  emp_id = f'EMP{len(employees_csv_list) + 1:04d}'
  fname, lname = fake.first_name(), fake.last_name()
  employees_csv_list.append({
      'EmployeeID': emp_id,
      'FK_BranchID': b_id,
      'FirstName': fname,
      'LastName': lname,
      'Role': 'Head Manager',
      'Education': 'Second degree',
      'Date of acceptance for work on the current position': fake.date_between(
          start_date='-5y', end_date='-2y'
      ).strftime('%Y-%m-%d'),
      'Date of birth': fake.date_of_birth(
          minimum_age=30, maximum_age=60
      ).strftime('%Y-%m-%d'),
  })
  employees_db_list.append(
      {'EmployeeID': emp_id, 'Name': fname, 'Surname': lname}
  )
  employee_meta[emp_id] = {
      'BranchID': b_id,
      'Role': 'Head Manager',
      'Active': True,
      'IsManager': True,
  }

# Step B: Distribution of remaining staff roles across branches at T1
num_remaining_t1 = NUM_EMPLOYEES_T1 - NUM_BRANCHES
role_counts = {
    role: num_remaining_t1 // len(ROLES_EXCEPT_MANAGER)
    for role in ROLES_EXCEPT_MANAGER
}
for i in range(num_remaining_t1 % len(ROLES_EXCEPT_MANAGER)):
  role_counts[ROLES_EXCEPT_MANAGER[i]] += 1

all_remaining_roles = []
for role, count in role_counts.items():
  all_remaining_roles.extend([role] * count)
random.shuffle(all_remaining_roles)

for idx, role in enumerate(all_remaining_roles):
  b_id = (idx % NUM_BRANCHES) + 1
  emp_id = f'EMP{len(employees_csv_list) + 1:04d}'
  fname, lname = fake.first_name(), fake.last_name()
  employees_csv_list.append({
      'EmployeeID': emp_id,
      'FK_BranchID': b_id,
      'FirstName': fname,
      'LastName': lname,
      'Role': role,
      'Education': random.choice(EDUCATION),
      'Date of acceptance for work on the current position': fake.date_between(
          start_date='-5y', end_date='-2y'
      ).strftime('%Y-%m-%d'),
      'Date of birth': fake.date_of_birth(
          minimum_age=20, maximum_age=60
      ).strftime('%Y-%m-%d'),
  })
  employees_db_list.append(
      {'EmployeeID': emp_id, 'Name': fname, 'Surname': lname}
  )
  employee_meta[emp_id] = {
      'BranchID': b_id,
      'Role': role,
      'Active': True,
      'IsManager': False,
  }

# --- T2 DIMENSION CHANGES: Staff Turnover & Promotions ---
# 1. Fire / Terminate a few non-manager employees
active_non_managers = [
    eid
    for eid, meta in employee_meta.items()
    if not meta['IsManager'] and meta['Active']
]
terminated_emps = random.sample(
    active_non_managers, k = int(len(active_non_managers) * 0.05)
)
for eid in terminated_emps:
  employee_meta[eid]['Active'] = False

# 2. Fire/Replace/Promote for Head Manager change:
# Pick Branch 1's current Head Manager to be fired/replaced, and promote a Receptionist to Head Manager
branch_1_managers = [
    eid
    for eid, meta in employee_meta.items()
    if meta['BranchID'] == 1 and meta['Role'] == 'Head Manager'
]
old_manager_id = branch_1_managers[0]
employee_meta[old_manager_id]['Active'] = False  # Old manager leaves/fired

# Pick a Receptionist from Branch 1 to promote to Head Manager
branch_1_receptionists = [
    eid
    for eid, meta in employee_meta.items()
    if meta['BranchID'] == 1 and meta['Role'] == 'Receptionist' and meta['Active']
]
promoted_emp_id = branch_1_receptionists[0]
employee_meta[promoted_emp_id]['Role'] = 'Head Manager'
employee_meta[promoted_emp_id]['IsManager'] = True

# Update their role in the CSV structure log
for emp in employees_csv_list:
  if emp['EmployeeID'] == promoted_emp_id:
    emp['Role'] = 'Head Manager'
    emp['Date of acceptance for work on the current position'] = (
        CUTOFF_DATE + timedelta(days=1)
    ).strftime('%Y-%m-%d')

# 3. Hire brand new employees at T2 (Staff extension)
NUM_NEW_HIRES_T2 = 50
for i in range(NUM_NEW_HIRES_T2):
  b_id = random.randint(1, NUM_BRANCHES)
  emp_id = f'EMP{len(employees_csv_list) + 1:04d}'
  fname, lname = fake.first_name(), fake.last_name()
  new_role = random.choice(ROLES_EXCEPT_MANAGER)
  employees_csv_list.append({
      'EmployeeID': emp_id,
      'FK_BranchID': b_id,
      'FirstName': fname,
      'LastName': lname,
      'Role': new_role,
      'Education': random.choice(EDUCATION),
      'Date of acceptance for work on the current position': (
          CUTOFF_DATE + timedelta(days=random.randint(1, 30))
      ).strftime('%Y-%m-%d'),
      'Date of birth': fake.date_of_birth(
          minimum_age=21, maximum_age=55
      ).strftime('%Y-%m-%d'),
  })
  employees_db_list.append(
      {'EmployeeID': emp_id, 'Name': fname, 'Surname': lname}
  )
  employee_meta[emp_id] = {
      'BranchID': b_id,
      'Role': new_role,
      'Active': True,
      'IsManager': False,
  }

# 3. Generate Dimensions: GUESTS
df_guests_db = pd.DataFrame([{
    'FirstName': fake.first_name(),
    'LastName': fake.last_name(),
    'DateOfBirth': fake.date_of_birth(minimum_age=18, maximum_age=80).strftime(
        '%Y-%m-%d'
    ),
    'Email': fake.email(),
    'PhoneNumber': fake.numerify('###########'),
} for i in range(1, NUM_GUESTS + 1)])

# 4. Generate Dimensions: ROOMS (T1 + T2 Expansion via Renovations)
branch_room_counts = {b: 0 for b in range(1, NUM_BRANCHES + 1)}
rooms = []

# T1 Rooms
for i in range(1, NUM_ROOMS_T1 + 1):
  assigned_branch = random.randint(1, NUM_BRANCHES)
  branch_room_counts[assigned_branch] += 1
  current_count = branch_room_counts[assigned_branch]
  floor_number = ((current_count - 1) // ROOMS_PER_FLOOR) + 1
  room_on_floor = ((current_count - 1) % ROOMS_PER_FLOOR) + 1
  room_number = (floor_number * 100) + room_on_floor

  rooms.append({
      'RoomID': f'R{i:05d}',
      'FK_BranchID': assigned_branch,
      'RoomNumber': str(room_number),
      'ApartmentType': random.choice(ROOM_TYPES),
  })

# T2 Room Expansion (Renovation / New Wing)
NUM_NEW_ROOMS_T2 = 200
for i in range(NUM_ROOMS_T1 + 1, NUM_ROOMS_T1 + NUM_NEW_ROOMS_T2 + 1):
  assigned_branch = random.randint(1, NUM_BRANCHES)
  branch_room_counts[assigned_branch] += 1
  current_count = branch_room_counts[assigned_branch]
  floor_number = ((current_count - 1) // ROOMS_PER_FLOOR) + 1
  room_on_floor = ((current_count - 1) % ROOMS_PER_FLOOR) + 1
  room_number = (floor_number * 100) + room_on_floor

  rooms.append({
      'RoomID': f'R{i:05d}',
      'FK_BranchID': assigned_branch,
      'RoomNumber': str(room_number),
      'ApartmentType': random.choice(ROOM_TYPES),
  })

df_rooms = pd.DataFrame(rooms)


# Helper function for stay timestamps
def generate_stay_timestamps(is_t2=False):
  start_window = (
      CUTOFF_DATE + timedelta(days=1)
      if is_t2
      else CUTOFF_DATE - timedelta(days=730)
  )
  end_window = (
      CUTOFF_DATE + timedelta(days=90) if is_t2 else CUTOFF_DATE
  )

  base_date = fake.date_time_between(
      start_date=start_window, end_date=end_window
  )
  checkin = base_date.replace(
      hour=random.randint(14, 22),
      minute=random.randint(0, 59),
      second=random.randint(0, 59),
  )
  stay_days = random.randint(1, 7)
  checkout = (checkin + timedelta(days=stay_days)).replace(
      hour=random.randint(7, 11),
      minute=random.randint(0, 59),
      second=random.randint(0, 59),
  )
  return checkin, checkout


stays, requests, surveys = [], [], []
stay_id_counter = 1
request_id_counter, survey_id_counter = 1, 1


def add_stay_entries(is_t2=False):
  global stay_id_counter
  checkin, checkout = generate_stay_timestamps(is_t2)
  room_id = random.choice(df_rooms['RoomID'].tolist())
  meal = random.choice(MEAL_OFFERS)

  num_guests_in_room = random.choices(
      [1, 2, 3, 4, 5, 6], weights=[0.55, 0.25, 0.10, 0.05, 0.03, 0.02]
  )[0]
  guest_ids = random.sample(range(1, NUM_GUESTS + 1), num_guests_in_room)

  for g_id in guest_ids:
    stays.append({
        'StayID': f'STAY{stay_id_counter:07d}',
        'FK_GuestID': g_id,
        'FK_RoomID': room_id,
        'CheckinDate': checkin.strftime('%Y-%m-%d %H:%M:%S'),
        'CheckOutDate': checkout.strftime('%Y-%m-%d %H:%M:%S'),
        'MealOffer': meal,
    })
    stay_id_counter += 1


# Generate T1 Stays
while len(stays) < NUM_STAYS_T1:
  add_stay_entries(is_t2=False)

# Generate T2 Stays
target_t2_total = len(stays) + NUM_STAYS_T2
while len(stays) < target_t2_total:
  add_stay_entries(is_t2=True)

# Filter valid operational staff for requests (EXCLUDING Head Managers)
valid_request_employees = [
    eid
    for eid, meta in employee_meta.items()
    if meta['Active'] and not meta['IsManager']
]

# Generate Requests and Surveys for ALL stays (1:1 survey mapping)
for stay in stays:
  checkin_dt = datetime.strptime(stay['CheckinDate'], '%Y-%m-%d %H:%M:%S')
  checkout_dt = datetime.strptime(stay['CheckOutDate'], '%Y-%m-%d %H:%M:%S')
  stay_duration_sec = int((checkout_dt - checkin_dt).total_seconds())

  num_requests = random.choices(
      [0, 1, 2, 3, 4, 5, 6, 7, 8],
      weights=[0.35, 0.25, 0.15, 0.10, 0.07, 0.04, 0.02, 0.01, 0.01],
  )[0]

  for _ in range(num_requests):
    offset_sec = random.randint(300, max(300, stay_duration_sec - 300))
    req_time = checkin_dt + timedelta(seconds=offset_sec)
    resolution_sec = random.randint(300, 10800)
    res_time = req_time + timedelta(seconds=resolution_sec)

    # STRICT: Pick only from non-manager operational staff
    emp_choice = random.choice(valid_request_employees)

    requests.append({
        'RequestID': f'REQ{request_id_counter:08d}',
        'FK_StayID': stay['StayID'],
        'FK_EmployeeID': emp_choice,
        'Category': random.choice(REQUEST_CATEGORIES),
        'RequestTime': req_time.strftime('%Y-%m-%d %H:%M:%S'),
        'ResolutionTime': res_time.strftime('%Y-%m-%d %H:%M:%S'),
        'ManagerIntervention': random.choice([0, 1]),
    })
    request_id_counter += 1

  surveys.append({
      'SurveyID': f'SUR{survey_id_counter:07d}',
      'FK_StayID': stay['StayID'],
      'OverallRating': random.choices(RATING_CHOICES, weights=RATING_WEIGHTS)[0],
      'StaffRating': random.choices(RATING_CHOICES, weights=RATING_WEIGHTS)[0],
      'ResponseRating': random.choices(
          RATING_CHOICES, weights=RATING_WEIGHTS
      )[0],
  })
  survey_id_counter += 1

# Export files
pd.DataFrame(employees_csv_list).to_csv('hotel_employees.csv', index=False, sep=',')
df_branches_csv.to_csv('hotel_branches.csv', index=False, sep=',')

df_branches_db.to_csv('branch.bulk', index=False, header=False, sep='|')
pd.DataFrame(employees_db_list).to_csv(
    'employee.bulk', index=False, header=False, sep='|'
)
df_guests_db.to_csv('guest.bulk', index=False, header=False, sep='|')
df_rooms.to_csv('room.bulk', index=False, header=False, sep='|')
pd.DataFrame(stays).to_csv('stay.bulk', index=False, header=False, sep='|')
pd.DataFrame(requests).to_csv('request.bulk', index=False, header=False, sep='|')
pd.DataFrame(surveys).to_csv('survey.bulk', index=False, header=False, sep='|')

print(
    'Data generation complete with promotions, staff turnover, room expansions,'
    ' and strict manager request exclusions.'
)