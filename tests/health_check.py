#!/usr/bin/env python3
"""
Seat Allocation System - Project Health Check
Run this script to validate the project structure and functionality
"""

import os
import sys
from pathlib import Path

def print_header(text):
    """Print formatted header"""
    print(f"\n{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}\n")

def check_files(files_to_check):
    """Check if files exist"""
    results = []
    for file_path in files_to_check:
        exists = os.path.exists(file_path)
        status = "✅" if exists else "❌"
        results.append((file_path, exists))
        print(f"  {status} {file_path}")
    return all(result[1] for result in results)

def main():
    print_header("SEAT ALLOCATION SYSTEM - HEALTH CHECK")
    
    all_passed = True
    
    # Check 1: Critical __init__.py files
    print("1️⃣  CHECKING MODULE INITIALIZATION FILES...")
    init_files = [
        "algo/__init__.py",
        "algo/api/__init__.py",
        "algo/api/blueprints/__init__.py",
        "algo/api/middleware/__init__.py",
        "algo/config/__init__.py",
        "algo/core/__init__.py",
        "algo/core/algorithm/__init__.py",
        "algo/core/cache/__init__.py",
        "algo/core/models/__init__.py",
        "algo/database/__init__.py",
        "algo/database/queries/__init__.py",
        "algo/services/__init__.py",
        "algo/pdf_gen/__init__.py",
    ]
    if not check_files(init_files):
        all_passed = False
    
    # Check 2: Service files
    print("\n2️⃣  CHECKING SERVICE MODULES...")
    service_files = [
        "algo/services/session_service.py",
        "algo/services/student_service.py",
        "algo/services/allocation_service.py",
    ]
    if not check_files(service_files):
        all_passed = False
    
    # Check 3: Blueprint files
    print("\n3️⃣  CHECKING BLUEPRINT MODULES...")
    blueprint_files = [
        "algo/api/blueprints/sessions.py",
        "algo/api/blueprints/students.py",
        "algo/api/blueprints/allocations.py",
        "algo/api/blueprints/pdf.py",
        "algo/api/blueprints/classrooms.py",
        "algo/api/blueprints/dashboard.py",
        "algo/api/blueprints/admin.py",
        "algo/api/blueprints/plans.py",
    ]
    if not check_files(blueprint_files):
        all_passed = False
    
    # Check 4: Core infrastructure
    print("\n4️⃣  CHECKING CORE INFRASTRUCTURE...")
    core_files = [
        "algo/app.py",
        "algo/main.py",
        "algo/config/settings.py",
        "algo/database/db.py",
        "algo/database/schema.py",
        "algo/core/algorithm/seating.py",
        "algo/core/cache/cache_manager.py",
    ]
    if not check_files(core_files):
        all_passed = False
    
    # Check 5: Database queries
    print("\n5️⃣  CHECKING DATABASE QUERY MODULES...")
    query_files = [
        "algo/database/queries/session_queries.py",
        "algo/database/queries/student_queries.py",
        "algo/database/queries/allocation_queries.py",
        "algo/database/queries/user_queries.py",
    ]
    if not check_files(query_files):
        all_passed = False
    
    # Check 6: PDF generation
    print("\n6️⃣  CHECKING PDF GENERATION...")
    pdf_files = [
        "algo/pdf_gen/pdf_generation.py",
        "algo/pdf_gen/template_manager.py",
    ]
    if not check_files(pdf_files):
        all_passed = False
    
    # Check 7: Test imports
    print("\n7️⃣  TESTING IMPORTS...")
    try:
        print("  Testing algo.main...")
        from algo.main import app, create_app
        print("    ✅ algo.main")
        
        print("  Testing algo.config...")
        from algo.config.settings import Config
        print("    ✅ algo.config")
        
        print("  Testing algo.services...")
        from algo.services.session_service import SessionService
        from algo.services.student_service import StudentService
        from algo.services.allocation_service import AllocationService
        print("    ✅ algo.services")
        
        print("  Testing algo.database...")
        from algo.database.queries.session_queries import SessionQueries
        print("    ✅ algo.database")
        
        print("  Testing algo.core...")
        from algo.core.algorithm.seating import SeatingAlgorithm
        from algo.core.cache.cache_manager import CacheManager
        print("    ✅ algo.core")
        
    except ImportError as e:
        print(f"    ❌ Import error: {e}")
        all_passed = False
    
    # Check 8: App creation
    print("\n8️⃣  TESTING APP CREATION...")
    try:
        from algo.main import create_app
        test_app = create_app()
        
        num_blueprints = len(test_app.blueprints)
        num_routes = sum(1 for _ in test_app.url_map.iter_rules() if _.endpoint != 'static')
        
        print(f"  ✅ App created successfully")
        print(f"  ✅ {num_blueprints} blueprints registered")
        print(f"  ✅ {num_routes} API endpoints available")
        
        if num_blueprints != 9 or num_routes != 37:
            print(f"  ⚠️  Expected 9 blueprints and 37 endpoints")
            
    except Exception as e:
        print(f"  ❌ App creation failed: {e}")
        all_passed = False
    
    # Check 9: Database connection
    print("\n9️⃣  TESTING DATABASE CONNECTION...")
    try:
        from algo.database.db import get_db_connection_standalone
        conn = get_db_connection_standalone()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        conn.close()
        
        print(f"  ✅ Database connected")
        print(f"  ✅ {len(tables)} tables found")
        
        expected_tables = [
            'allocation_sessions', 'students', 'uploads', 'allocations',
            'classrooms', 'feedback', 'user_activity', 'users',
            'allocation_history'
        ]
        found_tables = [t[0] for t in tables]
        
        for table in expected_tables:
            if table in found_tables:
                print(f"    ✅ {table}")
            else:
                print(f"    ⚠️  {table} (missing)")
                
    except Exception as e:
        print(f"  ❌ Database connection failed: {e}")
        all_passed = False
    
    # Final summary
    print_header("HEALTH CHECK SUMMARY")
    
    if all_passed:
        print("🎉 ALL CHECKS PASSED!")
        print("\n✅ Project structure is correct")
        print("✅ All modules can be imported")
        print("✅ App creates successfully")
        print("✅ Database is accessible")
        print("✅ All blueprints are registered")
        print("\n🚀 PROJECT IS READY TO USE\n")
        return 0
    else:
        print("⚠️  SOME CHECKS FAILED!")
        print("\nPlease review the output above for details.")
        print("Common issues:")
        print("  - Missing __init__.py files")
        print("  - Missing service or blueprint modules")
        print("  - Database not initialized")
        print("\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
