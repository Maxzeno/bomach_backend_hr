# gRPC Validation Test Scripts

Simple command-line scripts to test that gRPC validation is working.

---

## Prerequisites

Before running these tests:

1. **Start gRPC servers** in the main backend:
   ```bash
   cd /Users/developer/BOMACH/bomach_backend
   python3 manage.py run_all_grpc
   ```

2. Keep that terminal running!

---

## Quick Test (30 seconds)

Just verify gRPC validation is working:

```bash
python3 quick_test.py
```

**Expected Output:**
```
✅ SUCCESS: Validation is working!
   Rejected invalid ID with error:
   {'employee_id': "Employee with ID 'INVALID-TEST-999' does not exist..."}

🎉 gRPC validation is working correctly!
```

---

## Full Test Suite (2 minutes)

Run comprehensive tests:

```bash
python3 test_grpc_validation.py
```

**Tests:**
- ✅ Invalid IDs are rejected (3 tests)
- ✅ Valid IDs are accepted (3 tests)
- ✅ Optional fields work (2 tests)

**Note:** Before running, update the valid IDs in the script:
```python
VALID_EMPLOYEE_ID = 'EMP-TEST-001'    # Update this
VALID_DEPARTMENT_ID = '1'             # Update this
VALID_BRANCH_ID = '1'                 # Update this
```

---

## Create Test Data

If you need to create test data in the main backend:

```bash
cd /Users/developer/BOMACH/bomach_backend
python3 manage.py shell
```

```python
from user.models import Employee, Department, Branch, User, Country, State

# Create test data
country, _ = Country.objects.get_or_create(code='USA', defaults={'name': 'United States', 'is_active': True})
state, _ = State.objects.get_or_create(code='CA', country=country, defaults={'name': 'California', 'is_active': True})

branch, _ = Branch.objects.get_or_create(
    branch_name='HQ',
    defaults={'branch_id': 'BR-001', 'country': country, 'state': state,
              'office_address': '123 Main St', 'operational_status': 'active', 'is_active': True}
)

dept, _ = Department.objects.get_or_create(name='it', defaults={'description': 'IT'})

user, _ = User.objects.get_or_create(
    email='test@example.com',
    defaults={'username': 'testuser', 'first_name': 'Test', 'last_name': 'User', 'is_active': True}
)

employee, _ = Employee.objects.get_or_create(
    user=user,
    defaults={'employee_id': 'EMP-TEST-001', 'branch': branch, 'department': dept,
              'employment_type': 'full_time', 'is_active': True}
)

print(f"\n✅ Test data created!")
print(f"Branch ID: {branch.id}")
print(f"Department ID: {dept.id}")
print(f"Employee ID: {employee.employee_id}")
```

---

## Troubleshooting

### "Auth service is unavailable"
**Fix:** Start gRPC servers in main backend:
```bash
cd /Users/developer/BOMACH/bomach_backend
python3 manage.py run_all_grpc
```

### "Employee with ID 'EMP-TEST-001' does not exist"
**Fix:** Create test data (see above)

### All tests pass even with invalid IDs
**Issue:** gRPC servers not running or not configured correctly
**Fix:**
1. Check servers: `ps aux | grep run_all_grpc`
2. Check ports: `lsof -i :50052 && lsof -i :50053`
3. Restart servers

---

## What Success Looks Like

When validation is working correctly:

✅ **Invalid IDs are rejected:**
```
ValidationError: {'employee_id': "Employee with ID 'INVALID-999' does not exist in the auth service"}
```

✅ **Valid IDs are accepted:**
```
Created Payroll (ID: 123)
```

✅ **gRPC connection works:**
Error messages mention "auth service" or "department service"

---

## More Testing

For detailed testing, see:
- `/Users/developer/BOMACH/TEST_VALIDATION_GUIDE.md`
- `/Users/developer/BOMACH/QUICK_START_TESTING.md`
