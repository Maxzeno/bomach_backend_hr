#!/usr/bin/env python3
"""
Simple gRPC Validation Test Script
Run this to quickly verify that gRPC validation is working

Usage:
    python3 test_grpc_validation.py
"""

import os
import sys
import django
from datetime import date, timedelta

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bomach_backend_hr.settings')
django.setup()

from hr.models import Payroll, Associate, JobPosting, Asset
from django.core.exceptions import ValidationError


def print_header(text):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")


def test_invalid_ids():
    """Test that invalid IDs are rejected"""
    print_header("TEST 1: Invalid IDs (Should be REJECTED)")

    passed = 0

    # Test 1: Invalid employee_id in Payroll
    print("1. Testing Payroll with invalid employee_id...")
    try:
        p = Payroll(
            employee_id='INVALID-999',
            payroll_period='Test Period',
            gross_salary=5000,
            disbursement_date=date.today()
        )
        p.save()
        print("   ❌ FAIL: Accepted invalid employee_id")
    except ValidationError as e:
        print("   ✅ PASS: Rejected invalid employee_id")
        print(f"   Error: {str(e)[:100]}...")
        passed += 1
    except Exception as e:
        print(f"   ⚠️  ERROR: {e}")

    # Test 2: Invalid department_id in Associate
    print("\n2. Testing Associate with invalid department_id...")
    try:
        a = Associate(
            full_name='Test User',
            email='test@example.com',
            phone_number='1234567890',
            company_name='Test Corp',
            department_id='INVALID-DEPT-999',
            contract_start_date=date.today(),
            contract_end_date=date.today() + timedelta(days=365)
        )
        a.save()
        print("   ❌ FAIL: Accepted invalid department_id")
    except ValidationError as e:
        print("   ✅ PASS: Rejected invalid department_id")
        print(f"   Error: {str(e)[:100]}...")
        passed += 1
    except Exception as e:
        print(f"   ⚠️  ERROR: {e}")

    # Test 3: Invalid branch_id in JobPosting
    print("\n3. Testing JobPosting with invalid branch_id...")
    try:
        jp = JobPosting(
            job_title='Test Position',
            branch_id='INVALID-BRANCH-999',
            job_type='Full-Time',
            status='Active'
        )
        jp.save()
        print("   ❌ FAIL: Accepted invalid branch_id")
    except ValidationError as e:
        print("   ✅ PASS: Rejected invalid branch_id")
        print(f"   Error: {str(e)[:100]}...")
        passed += 1
    except Exception as e:
        print(f"   ⚠️  ERROR: {e}")

    print(f"\n{'─'*60}")
    print(f"Result: {passed}/3 tests passed")
    return passed == 3


def test_valid_ids():
    """Test that valid IDs are accepted"""
    print_header("TEST 2: Valid IDs (Should be ACCEPTED)")

    # Get valid IDs (you may need to adjust these)
    print("⚠️  NOTE: Update these IDs in the script if tests fail:")
    VALID_EMPLOYEE_ID = 'EMP-TEST-001'
    VALID_DEPARTMENT_ID = '1'
    VALID_BRANCH_ID = '1'

    print(f"   Using employee_id: {VALID_EMPLOYEE_ID}")
    print(f"   Using department_id: {VALID_DEPARTMENT_ID}")
    print(f"   Using branch_id: {VALID_BRANCH_ID}\n")

    passed = 0
    created_objects = []

    # Test 1: Valid employee_id in Payroll
    print("1. Testing Payroll with valid employee_id...")
    try:
        p = Payroll(
            employee_id=VALID_EMPLOYEE_ID,
            payroll_period='Test Period Valid',
            gross_salary=5000,
            disbursement_date=date.today()
        )
        p.save()
        print(f"   ✅ PASS: Created Payroll (ID: {p.id})")
        created_objects.append(('payroll', p))
        passed += 1
    except ValidationError as e:
        print(f"   ❌ FAIL: Rejected valid employee_id")
        print(f"   Error: {e}")
        print(f"   → Check that employee '{VALID_EMPLOYEE_ID}' exists in main backend")
    except Exception as e:
        print(f"   ⚠️  ERROR: {e}")

    # Test 2: Valid department_id in Associate
    print("\n2. Testing Associate with valid department_id...")
    try:
        a = Associate(
            full_name='Valid Test User',
            email='valid.test@example.com',
            phone_number='5551234567',
            company_name='Valid Corp',
            department_id=VALID_DEPARTMENT_ID,
            contract_start_date=date.today(),
            contract_end_date=date.today() + timedelta(days=365)
        )
        a.save()
        print(f"   ✅ PASS: Created Associate (ID: {a.id})")
        created_objects.append(('associate', a))
        passed += 1
    except ValidationError as e:
        print(f"   ❌ FAIL: Rejected valid department_id")
        print(f"   Error: {e}")
        print(f"   → Check that department ID '{VALID_DEPARTMENT_ID}' exists in main backend")
    except Exception as e:
        print(f"   ⚠️  ERROR: {e}")

    # Test 3: Valid branch_id in JobPosting
    print("\n3. Testing JobPosting with valid branch_id...")
    try:
        jp = JobPosting(
            job_title='Valid Test Position',
            department_id=VALID_DEPARTMENT_ID,
            branch_id=VALID_BRANCH_ID,
            job_type='Full-Time',
            status='Active'
        )
        jp.save()
        print(f"   ✅ PASS: Created JobPosting (ID: {jp.id})")
        created_objects.append(('jobposting', jp))
        passed += 1
    except ValidationError as e:
        print(f"   ❌ FAIL: Rejected valid branch_id")
        print(f"   Error: {e}")
        print(f"   → Check that branch ID '{VALID_BRANCH_ID}' exists in main backend")
    except Exception as e:
        print(f"   ⚠️  ERROR: {e}")

    # Cleanup
    if created_objects:
        print("\n" + "─"*60)
        print("Cleaning up test records...")
        for obj_type, obj in created_objects:
            try:
                obj.delete()
                print(f"   Deleted {obj_type} (ID: {obj.id})")
            except Exception as e:
                print(f"   Failed to delete {obj_type}: {e}")

    print(f"\n{'─'*60}")
    print(f"Result: {passed}/3 tests passed")
    return passed == 3


def test_optional_fields():
    """Test that optional fields work with null values"""
    print_header("TEST 3: Optional Fields (Should be ACCEPTED)")

    passed = 0
    created_objects = []

    # Test 1: Associate without department_id
    print("1. Testing Associate without department_id (optional)...")
    try:
        a = Associate(
            full_name='Freelancer Test',
            email='freelancer@example.com',
            phone_number='5559876543',
            company_name='Independent',
            department_id=None,  # Optional
            contract_start_date=date.today(),
            contract_end_date=date.today() + timedelta(days=180)
        )
        a.save()
        print(f"   ✅ PASS: Created Associate without department_id (ID: {a.id})")
        created_objects.append(a)
        passed += 1
    except Exception as e:
        print(f"   ❌ FAIL: {e}")

    # Test 2: Asset without optional fields
    print("\n2. Testing Asset without optional IDs...")
    try:
        asset = Asset(
            name='Unassigned Equipment',
            asset_type='Equipment',
            branch='Storage',
            assigned_to_id=None,  # Optional
            department_id=None,   # Optional
            status='Available'
        )
        asset.save()
        print(f"   ✅ PASS: Created Asset without optional IDs (ID: {asset.id})")
        created_objects.append(asset)
        passed += 1
    except Exception as e:
        print(f"   ❌ FAIL: {e}")

    # Cleanup
    if created_objects:
        print("\n" + "─"*60)
        print("Cleaning up test records...")
        for obj in created_objects:
            try:
                obj.delete()
                print(f"   Deleted {obj.__class__.__name__} (ID: {obj.id})")
            except Exception as e:
                print(f"   Failed to delete: {e}")

    print(f"\n{'─'*60}")
    print(f"Result: {passed}/2 tests passed")
    return passed == 2


def main():
    print("\n" + "="*60)
    print("  gRPC VALIDATION TEST SUITE")
    print("="*60)

    print("\nPrerequisites:")
    print("  1. Main backend gRPC servers must be running")
    print("  2. Run: cd ../bomach_backend && python3 manage.py run_all_grpc")
    print("  3. Test data must exist in main backend\n")

    try:
        input("Press Enter to start tests (Ctrl+C to cancel)...")
    except KeyboardInterrupt:
        print("\n\nTests cancelled.")
        return 1

    # Run all tests
    results = []

    try:
        test1_pass = test_invalid_ids()
        results.append(("Invalid IDs", test1_pass))
    except Exception as e:
        print(f"\n⚠️  Test 1 crashed: {e}")
        results.append(("Invalid IDs", False))

    try:
        test2_pass = test_valid_ids()
        results.append(("Valid IDs", test2_pass))
    except Exception as e:
        print(f"\n⚠️  Test 2 crashed: {e}")
        results.append(("Valid IDs", False))

    try:
        test3_pass = test_optional_fields()
        results.append(("Optional Fields", test3_pass))
    except Exception as e:
        print(f"\n⚠️  Test 3 crashed: {e}")
        results.append(("Optional Fields", False))

    # Final summary
    print_header("FINAL RESULTS")

    all_passed = True
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status}: {name}")
        if not passed:
            all_passed = False

    print("\n" + "="*60)

    if all_passed:
        print("  🎉 ALL TESTS PASSED!")
        print("  Validation system is working correctly!")
        print("="*60 + "\n")
        return 0
    else:
        print("  ⚠️  SOME TESTS FAILED")
        print("\n  Troubleshooting:")
        print("  1. Check gRPC servers are running:")
        print("     ps aux | grep run_all_grpc")
        print("  2. Verify test data exists in main backend")
        print("  3. Check logs for detailed errors")
        print("="*60 + "\n")
        return 1


if __name__ == '__main__':
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user.\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
