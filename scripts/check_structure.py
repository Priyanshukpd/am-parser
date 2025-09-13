#!/usr/bin/env python3
"""
Script to verify the AM Parser folder structure is correctly organized.
"""

import os
from pathlib import Path

def check_folder_structure():
    """Check if the folder structure matches production requirements."""
    root = Path(__file__).resolve().parent.parent
    print(f"Checking structure for: {root}")
    print("="*60)
    
    # Expected structure
    expected_structure = {
        # Core modules
        "am_api": ["__init__.py", "cli.py", "__main__.py"],
        "am_services": ["__init__.py", "manual_parser.py"],
        "am_llm": ["__init__.py", "client.py", "parser.py"],
        "am_persistence": ["__init__.py", "repository.py"],
        "am_common": ["__init__.py"],
        "am_configs": ["header_maps.yaml"],
        
        # Legacy wrapper
        "am_parser": ["__init__.py", "cli/__init__.py", "cli/__main__.py", "parsers/__init__.py"],
        
        # Data and docs
        "data/samples": ["mutualfund_sample.csv", "README.md"],
        "tests": ["test_manual_parser.py"],
        "docs": ["ai-editor-context.md"],
        "scripts": ["validate_code_conventions.py", "check_structure.py"],
        
        # Config files
        ".": ["README.md", "requirements.txt", "requirements-mongo.txt", "ai-context.yaml", ".editorconfig"]
    }
    
    issues = []
    success = []
    
    # Check each expected directory and file
    for dir_path, files in expected_structure.items():
        full_dir = root / dir_path if dir_path != "." else root
        
        if not full_dir.exists():
            issues.append(f"❌ Missing directory: {dir_path}")
            continue
            
        if dir_path != ".":
            success.append(f"✅ Directory exists: {dir_path}")
        
        # Check files in directory
        for file_name in files:
            file_path = full_dir / file_name
            if file_path.exists():
                success.append(f"✅ File exists: {dir_path}/{file_name}")
            else:
                issues.append(f"❌ Missing file: {dir_path}/{file_name}")
    
    # Check for any leftover duplicate/external modules
    potential_duplicates = [
        "am_api_external", "am_services_external", "am_llm_external", 
        "am_persistence_external", "am_common_external", "am_configs_external",
        "am-api", "am-services", "am-llm", "am-persistence", "am-common", "am-configs",
        "api", "services", "llm", "persistence", "common", "configs"
    ]
    
    for dup in potential_duplicates:
        dup_path = root / dup
        if dup_path.exists():
            issues.append(f"❌ Duplicate/old module found: {dup}")
    
    # Print results
    print("\n✅ SUCCESS:")
    for item in success:
        print(f"  {item}")
    
    if issues:
        print(f"\n❌ ISSUES FOUND ({len(issues)}):")
        for item in issues:
            print(f"  {item}")
        return False
    else:
        print(f"\n🎉 STRUCTURE IS CLEAN! All {len(success)} components are in correct places.")
        return True

if __name__ == "__main__":
    check_folder_structure()