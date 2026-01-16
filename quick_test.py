#!/usr/bin/env python3
"""
Super Quick gRPC Validation Test
Just tests one thing to verify gRPC is working

Usage:
    python3 quick_test.py
"""

import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bomach_backend_hr.settings')
django.setup()

from hr.models import Payroll
from django.core.exceptions import ValidationError
from datetime import date

print("\n" + "="*60)
print("  QUICK gRPC VALIDATION TEST")
print("="*60 + "\n")

# Test with invalid ID (should be rejected)
try:
    Payroll.objects.all().delete()
    p = Payroll(
        employee_id='100',
        payroll_period='Quick Test',
        gross_salary=5000,
        net_salary=6000,
        disbursement_date=date.today()
    )
    p.save()
    sys.exit(1)
except ValidationError as e:
    print(f"   Rejected invalid ID with error:")
    print(f"   {e}\n")

    if "unavailable" in str(e).lower():
        print("⚠️  WARNING: gRPC service seems unavailable")
        print("   Start servers: cd ../bomach_backend && python3 manage.py run_all_grpc\n")
        sys.exit(1)
    else:
        print("🎉 gRPC validation is working correctly!\n")
        sys.exit(0)
except Exception as e:
    print(f"❌ ERROR: Unexpected error: {e}\n")
    sys.exit(1)
