from datetime import datetime, timedelta
import random
from faker import Faker
import pandas as pd

random.seed(42)
Faker.seed(42)
fake = Faker()

NUM_BRANCHES = 10
NUM_EMPLOYEES_T1 = 450
NUM_ROOMS_T1 = 1400
NUM_GUESTS = 25000
NUM_STAYS_T1 = 8000
NUM_STAYS_T2 = 2000
ROOMS_PER_FLOOR = 30
CUTOFF_DATE = datetime(2024, 12, 31)

MEAL_OFFERS = ['None', 'Breakfast Only', 'Supper Only', 'Breakfast and Supper']
ROOM_TYPES = ['Standard', 'Deluxe', 'Superior']
REQUEST_CATEGORIES = [
    'extra pillows',
    'amenities restock',
    'additional toilet paper',
    'ordering room service',
    'towel exchange',
    'wake-up call',
    'transportation request',
    'equipment issue',
    'ordering a meal to a specific room',
    'loud neighbor complaint',
    'bad service complaint',
    'other complaint',
]
ROLES_EXCEPT_MANAGER = [
    'Receptionist',
    'Housekeeper',
    'Technician',
    'Kitchen staff',
]
EDUCATION = ['Middle school', 'Graduate', 'First degree', 'Second degree']
RATING_CHOICES = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
RATING_WEIGHTS = [1, 2, 3, 5, 8, 15, 30, 20, 12, 4]

# 1. GENERATE BRANCHES
branches_data = [
    {
        'BranchID': i,
        'Branch Name': f'Marble {fake.city()}',
        'City': fake.city(),
        'Address': fake.street_address(),
        'Postal code': fake.postcode(),
        'Year opened': random.randint(1990, 2023),
    }
    for i in range(1, NUM_BRANCHES + 1)
]
df_branches_csv = pd.DataFrame(branches_data)
df_branches_db = df_branches_csv[['Branch Name']].rename(
    columns={'Branch Name': 'Name'}
)

# 2. GENERATE EMPLOYEES (T1 Baseline)
employees_csv_list = []
employees_db_dict = {}  # Unique EmployeeID -> {Name, Surname}
employee_meta = {}

# Step A: 1 Head Manager per branch at T1
for b_id in range(1, NUM_BRANCHES + 1):
  emp_id = f'EMP{len(employees_db_dict) + 1:04d}'
  fname, lname = fake.first_name(), fake.last_name()
  dob = fake.date_of_birth(minimum_age=30, maximum_age=60).strftime('%Y-%m-%d')
  hire_date = fake.date_between(start_date='-5y', end_date='-2y').strftime(
      '%Y-%m-%d'
  )

  employees_csv_list.append({
      'EmployeeID': emp_id,
      'FK_BranchID': b_id,
      'FirstName': fname,
      'LastName': lname,
      'Role': 'Head Manager',
      'Education': 'Second degree',
      'Date of acceptance for work on the current position': hire_date,
      'Date of birth': dob,
  })
  employees_db_dict[emp_id] = {'Name': fname, 'Surname': lname}
  employee_meta[emp_id] = {
      'BranchID': b_id,
      'Role': 'Head Manager',
      'Active': True,
      'IsManager': True,
      'FirstName': fname,
      'LastName': lname,
      'Education': 'Second degree',
      'DOB': dob,
  }

# Step B: Staff across branches at T1
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
  emp_id = f'EMP{len(employees_db_dict) + 1:04d}'
  fname, lname = fake.first_name(), fake.last_name()
  dob = fake.date_of_birth(minimum_age=20, maximum_age=60).strftime('%Y-%m-%d')
  hire_date = fake.date_between(start_date='-5y', end_date='-2y').strftime(
      '%Y-%m-%d'
  )

  employees_csv_list.append({
      'EmployeeID': emp_id,
      'FK_BranchID': b_id,
      'FirstName': fname,
      'LastName': lname,
      'Role': role,
      'Education': random.choice(EDUCATION),
      'Date of acceptance for work on the current position': hire_date,
      'Date of birth': dob,
  })
  employees_db_dict[emp_id] = {'Name': fname, 'Surname': lname}
  employee_meta[emp_id] = {
      'BranchID': b_id,
      'Role': role,
      'Active': True,
      'IsManager': False,
      'FirstName': fname,
      'LastName': lname,
      'Education': random.choice(EDUCATION),
      'DOB': dob,
  }

# --- T2 PROMOTIONS, TURNOVER & EXTENSIONS ---

# 1. Fire non-managers (Turnover)
active_non_managers = [
    eid
    for eid, meta in employee_meta.items()
    if not meta['IsManager'] and meta['Active']
]
terminated_emps = random.sample(
    active_non_managers, k=int(len(active_non_managers) * 0.05)
)
for eid in terminated_emps:
  employee_meta[eid]['Active'] = False

# 2. Terminate Branch 1 Head Manager & Promote Branch 1 Receptionist
branch_1_managers = [
    eid
    for eid, meta in employee_meta.items()
    if meta['BranchID'] == 1 and meta['Role'] == 'Head Manager'
]
old_manager_id = branch_1_managers[0]
employee_meta[old_manager_id]['Active'] = False  # Former manager departs

# Find Receptionist at Branch 1
branch_1_receptionists = [
    eid
    for eid, meta in employee_meta.items()
    if meta['BranchID'] == 1 and meta['Role'] == 'Receptionist' and meta['Active']
]
promoted_emp_id = branch_1_receptionists[0]

# APPEND SECOND RECORD FOR PROMOTED EMPLOYEE (Preserving career history from T1)
promoted_info = employee_meta[promoted_emp_id]
promotion_date = (CUTOFF_DATE + timedelta(days=2)).strftime('%Y-%m-%d')

employees_csv_list.append({
    'EmployeeID': promoted_emp_id,  # Same EmployeeID!
    'FK_BranchID': 1,
    'FirstName': promoted_info['FirstName'],
    'LastName': promoted_info['LastName'],
    'Role': 'Head Manager',  # Promoted Role
    'Education': promoted_info['Education'],
    'Date of acceptance for work on the current position': promotion_date,
    'Date of birth': promoted_info['DOB'],
})

# Update operational tracking for T2 requests
employee_meta[promoted_emp_id]['Role'] = 'Head Manager'
employee_meta[promoted_emp_id]['IsManager'] = True

# 3. New Hires at T2
NUM_NEW_HIRES_T2 = 50
for _ in range(NUM_NEW_HIRES_T2):
  b_id = random.randint(1, NUM_BRANCHES)
  emp_id = f'EMP{len(employees_db_dict) + 1:04d}'
  fname, lname = fake.first_name(), fake.last_name()
  new_role = random.choice(ROLES_EXCEPT_MANAGER)
  hire_date = (
      CUTOFF_DATE + timedelta(days=random.randint(1, 30))
  ).strftime('%Y-%m-%d')
  dob = fake.date_of_birth(minimum_age=21, maximum_age=55).strftime('%Y-%m-%d')

  employees_csv_list.append({
      'EmployeeID': emp_id,
      'FK_BranchID': b_id,
      'FirstName': fname,
      'LastName': lname,
      'Role': new_role,
      'Education': random.choice(EDUCATION),
      'Date of acceptance for work on the current position': hire_date,
      'Date of birth': dob,
  })
  employees_db_dict[emp_id] = {'Name': fname, 'Surname': lname}
  employee_meta[emp_id] = {
      'BranchID': b_id,
      'Role': new_role,
      'Active': True,
      'IsManager': False,
  }

# 3. GUESTS & ROOMS
df_guests_db = pd.DataFrame([{
    'FirstName': fake.first_name(),
    'LastName': fake.last_name(),
    'DateOfBirth': fake.date_of_birth(minimum_age=18, maximum_age=80).strftime(
        '%Y-%m-%d'
    ),
    'Email': fake.email(),
    'PhoneNumber': fake.numerify('###########'),
} for _ in range(NUM_GUESTS)])

branch_room_counts = {b: 0 for b in range(1, NUM_BRANCHES + 1)}
rooms = []
for i in range(1, NUM_ROOMS_T1 + 201):
  b_id = random.randint(1, NUM_BRANCHES)
  branch_room_counts[b_id] += 1
  c_count = branch_room_counts[b_id]
  flr = ((c_count - 1) // ROOMS_PER_FLOOR) + 1
  rm_num = (flr * 100) + ((c_count - 1) % ROOMS_PER_FLOOR) + 1
  rooms.append({
      'RoomID': f'R{i:05d}',
      'FK_BranchID': b_id,
      'RoomNumber': str(rm_num),
      'ApartmentType': random.choice(ROOM_TYPES),
  })
df_rooms = pd.DataFrame(rooms)


# 4. FACT ROWS (STAYS, REQUESTS, SURVEYS)
def generate_stay_timestamps(is_t2=False):
  start_w = (
      CUTOFF_DATE + timedelta(days=1)
      if is_t2
      else CUTOFF_DATE - timedelta(days=730)
  )
  end_w = CUTOFF_DATE + timedelta(days=90) if is_t2 else CUTOFF_DATE
  base = fake.date_time_between(start_date=start_w, end_date=end_w)
  checkin = base.replace(
      hour=random.randint(14, 22),
      minute=random.randint(0, 59),
      second=random.randint(0, 59),
  )
  checkout = (checkin + timedelta(days=random.randint(1, 7))).replace(
      hour=random.randint(7, 11),
      minute=random.randint(0, 59),
      second=random.randint(0, 59),
  )
  return checkin, checkout


stays, requests, surveys = [], [], []
stay_id_cnt, req_id_cnt, sur_id_cnt = 1, 1, 1


def add_stay_entries(is_t2=False):
  global stay_id_cnt
  checkin, checkout = generate_stay_timestamps(is_t2)
  room_id = random.choice(df_rooms['RoomID'].tolist())
  meal = random.choice(MEAL_OFFERS)
  num_g = random.choices([1, 2, 3, 4, 5, 6], weights=[0.55, 0.25, 0.1, 0.05, 0.03, 0.02])[0]
  for g_id in random.sample(range(1, NUM_GUESTS + 1), num_g):
    stays.append({
        'StayID': f'STAY{stay_id_cnt:07d}',
        'FK_GuestID': g_id,
        'FK_RoomID': room_id,
        'CheckinDate': checkin.strftime('%Y-%m-%d %H:%M:%S'),
        'CheckOutDate': checkout.strftime('%Y-%m-%d %H:%M:%S'),
        'MealOffer': meal,
    })
    stay_id_cnt += 1


while len(stays) < NUM_STAYS_T1:
  add_stay_entries(is_t2=False)
while len(stays) < (NUM_STAYS_T1 + NUM_STAYS_T2):
  add_stay_entries(is_t2=True)

# Generate requests for non-manager active staff
for stay in stays:
  checkin_dt = datetime.strptime(stay['CheckinDate'], '%Y-%m-%d %H:%M:%S')
  checkout_dt = datetime.strptime(stay['CheckOutDate'], '%Y-%m-%d %H:%M:%S')
  dur = int((checkout_dt - checkin_dt).total_seconds())
  num_reqs = random.choices(
      [0, 1, 2, 3, 4, 5, 6, 7, 8],
      weights=[0.35, 0.25, 0.15, 0.10, 0.07, 0.04, 0.02, 0.01, 0.01],
  )[0]

  for _ in range(num_reqs):
    req_time = checkin_dt + timedelta(
        seconds=random.randint(300, max(300, dur - 300))
    )
    res_time = req_time + timedelta(seconds=random.randint(300, 10800))

    # Promoted employee handles requests at T1 as Receptionist, but NOT at T2 as Head Manager
    if req_time <= CUTOFF_DATE:
      valid_emps = [
          eid
          for eid, m in employee_meta.items()
          if m['Active'] and not m['IsManager']
      ] + [promoted_emp_id]
    else:
      valid_emps = [
          eid
          for eid, m in employee_meta.items()
          if m['Active'] and not m['IsManager']
      ]

    emp_choice = random.choice(valid_emps)

    requests.append({
        'RequestID': f'REQ{req_id_cnt:08d}',
        'FK_StayID': stay['StayID'],
        'FK_EmployeeID': emp_choice,
        'Category': random.choice(REQUEST_CATEGORIES),
        'RequestTime': req_time.strftime('%Y-%m-%d %H:%M:%S'),
        'ResolutionTime': res_time.strftime('%Y-%m-%d %H:%M:%S'),
        'ManagerIntervention': random.choice([0, 1]),
    })
    req_id_cnt += 1

  surveys.append({
      'SurveyID': f'SUR{sur_id_cnt:07d}',
      'FK_StayID': stay['StayID'],
      'OverallRating': random.choices(RATING_CHOICES, weights=RATING_WEIGHTS)[0],
      'StaffRating': random.choices(RATING_CHOICES, weights=RATING_WEIGHTS)[0],
      'ResponseRating': random.choices(
          RATING_CHOICES, weights=RATING_WEIGHTS
      )[0],
  })
  sur_id_cnt += 1

# EXPORT DATA
pd.DataFrame(employees_csv_list).to_csv(
    'hotel_employees.csv', index=False, sep=','
)
df_branches_csv.to_csv('hotel_branches.csv', index=False, sep=',')

df_branches_db.to_csv('branch.bulk', index=False, header=False, sep='|')
# Export distinct Employee list for EMPLOYEE table
employees_db_list = [
    {'EmployeeID': eid, 'Name': info['Name'], 'Surname': info['Surname']}
    for eid, info in employees_db_dict.items()
]
pd.DataFrame(employees_db_list).to_csv(
    'employee.bulk', index=False, header=False, sep='|'
)

df_guests_db.to_csv('guest.bulk', index=False, header=False, sep='|')
df_rooms.to_csv('room.bulk', index=False, header=False, sep='|')
pd.DataFrame(stays).to_csv('stay.bulk', index=False, header=False, sep='|')
pd.DataFrame(requests).to_csv('request.bulk', index=False, header=False, sep='|')
pd.DataFrame(surveys).to_csv('survey.bulk', index=False, header=False, sep='|')

print('Data generation complete.')