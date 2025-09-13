import subprocess
import sys
from pathlib import Path

# Run the structure check script
try:
    result = subprocess.run([
        sys.executable, 
        str(Path(__file__).parent / "scripts" / "check_structure.py")
    ], capture_output=True, text=True, cwd=Path(__file__).parent)
    
    print("FOLDER STRUCTURE CHECK RESULTS:")
    print("=" * 50)
    print(result.stdout)
    if result.stderr:
        print("ERRORS:")
        print(result.stderr)
        
    # Also check what directories actually exist
    print("\nACTUAL DIRECTORIES FOUND:")
    print("=" * 30)
    root = Path(__file__).parent
    for item in sorted(root.iterdir()):
        if item.is_dir() and not item.name.startswith('.'):
            print(f"📁 {item.name}/")
            # Show first few files in each directory
            files = list(item.glob("*"))[:5]
            for f in files:
                prefix = "📁" if f.is_dir() else "📄"
                print(f"   {prefix} {f.name}")
            if len(list(item.glob("*"))) > 5:
                print(f"   ... and {len(list(item.glob('*'))) - 5} more")
                
except Exception as e:
    print(f"Error running check: {e}")
    
    # Manual check
    print("\nMANUAL DIRECTORY LISTING:")
    root = Path(__file__).parent
    for item in sorted(root.iterdir()):
        if item.is_dir():
            print(f"📁 {item.name}/")
        else:
            print(f"📄 {item.name}")