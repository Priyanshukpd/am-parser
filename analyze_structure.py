from pathlib import Path

# Check the current state
root = Path("c:/Users/drabh/Downloads/am-parser")

print("AM PARSER FOLDER STRUCTURE CHECK")
print("=" * 50)

# Key directories to check
key_dirs = [
    "am_api", "am_services", "am_llm", "am_persistence", 
    "am_common", "am_configs", "am_parser", "data", 
    "tests", "docs", "scripts"
]

print("\n📁 MAIN DIRECTORIES:")
for dir_name in key_dirs:
    dir_path = root / dir_name
    if dir_path.exists():
        print(f"✅ {dir_name}/")
        # Show key files
        files = list(dir_path.rglob("*.py")) + list(dir_path.rglob("*.yaml")) + list(dir_path.rglob("*.csv"))
        for f in sorted(files)[:3]:
            rel_path = f.relative_to(dir_path)
            print(f"   📄 {rel_path}")
        if len(files) > 3:
            print(f"   ... and {len(files) - 3} more files")
    else:
        print(f"❌ {dir_name}/ - MISSING")

# Check for duplicates
print("\n🔍 CHECKING FOR DUPLICATES:")
all_dirs = [d for d in root.iterdir() if d.is_dir() and not d.name.startswith('.')]
duplicate_patterns = ["external", "am-", "api", "services", "llm", "persistence", "common", "configs"]

duplicates_found = []
for d in all_dirs:
    for pattern in duplicate_patterns:
        if pattern in d.name.lower() and d.name not in key_dirs:
            duplicates_found.append(d.name)

if duplicates_found:
    print("❌ DUPLICATES FOUND:")
    for dup in duplicates_found:
        print(f"   🗂️ {dup}/")
else:
    print("✅ No duplicate directories found")

# Check key files in am_services (since user has it open)
print("\n📄 AM_SERVICES CONTENT:")
services_dir = root / "am_services"
if services_dir.exists():
    for f in services_dir.rglob("*"):
        if f.is_file():
            rel_path = f.relative_to(services_dir)
            size = f.stat().st_size
            print(f"   📄 {rel_path} ({size} bytes)")
else:
    print("   ❌ am_services directory not found")

print("\n" + "=" * 50)
print("STRUCTURE ANALYSIS COMPLETE")