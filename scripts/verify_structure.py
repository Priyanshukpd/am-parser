#!/usr/bin/env python3
"""
Complete folder structure verification and cleanup for AM Parser
"""

import os
import shutil
from pathlib import Path

def verify_and_fix_structure():
    """Verify and fix the AM Parser folder structure."""
    root = Path("c:/Users/drabh/Downloads/am-parser")
    print(f"🔍 Analyzing structure in: {root}")
    print("=" * 60)
    
    # Define correct structure
    correct_structure = {
        "am_api": {
            "files": ["__init__.py", "cli.py", "__main__.py"],
            "description": "CLI interface module"
        },
        "am_services": {
            "files": ["__init__.py", "manual_parser.py"],
            "description": "Core parsing services"
        },
        "am_llm": {
            "files": ["__init__.py", "client.py", "parser.py"],
            "description": "LLM parsing functionality"
        },
        "am_persistence": {
            "files": ["__init__.py", "repository.py"],
            "description": "Database repository interfaces"
        },
        "am_common": {
            "files": ["__init__.py", "models.py"],
            "description": "Shared models and utilities"
        },
        "am_configs": {
            "files": ["header_maps.yaml"],
            "description": "Configuration files"
        },
        "am_parser": {
            "files": ["__init__.py", "cli/__init__.py", "cli/__main__.py", "parsers/__init__.py"],
            "description": "Legacy wrapper"
        }
    }
    
    # Check each module
    issues = []
    success = []
    
    for module, info in correct_structure.items():
        module_path = root / module
        
        if not module_path.exists():
            issues.append(f"❌ Missing module: {module}")
            continue
            
        success.append(f"✅ Module exists: {module} - {info['description']}")
        
        # Check required files
        for file_name in info["files"]:
            file_path = module_path / file_name
            if file_path.exists():
                success.append(f"  ✅ {file_name}")
            else:
                issues.append(f"  ❌ Missing: {module}/{file_name}")
    
    # Check for unwanted duplicates/old modules
    all_dirs = [d.name for d in root.iterdir() if d.is_dir() and not d.name.startswith('.')]
    expected_dirs = list(correct_structure.keys()) + ["data", "tests", "docs", "scripts"]
    
    duplicates = []
    for dir_name in all_dirs:
        if dir_name not in expected_dirs:
            # Check if it's a potential duplicate
            if any(pattern in dir_name.lower() for pattern in ["external", "am-", "api", "services", "llm", "persistence", "common", "configs"]):
                duplicates.append(dir_name)
    
    if duplicates:
        print(f"\n🗑️  FOUND {len(duplicates)} DUPLICATE/OLD DIRECTORIES:")
        for dup in duplicates:
            dup_path = root / dup
            print(f"  📁 {dup}/ -> Should be removed")
            # Don't auto-delete, just report
    
    # Summary
    print(f"\n✅ SUCCESS ({len(success)} items):")
    for item in success:
        print(f"  {item}")
    
    if issues:
        print(f"\n❌ ISSUES ({len(issues)} items):")
        for item in issues:
            print(f"  {item}")
    
    if duplicates:
        print(f"\n🧹 CLEANUP NEEDED:")
        print(f"  Remove {len(duplicates)} duplicate directories")
        print("  Run: python scripts/cleanup_duplicates.py")
    
    # Final status
    if not issues and not duplicates:
        print(f"\n🎉 STRUCTURE IS PERFECT!")
        return True
    else:
        print(f"\n⚠️  Structure needs attention: {len(issues)} issues, {len(duplicates)} duplicates")
        return False

if __name__ == "__main__":
    verify_and_fix_structure()