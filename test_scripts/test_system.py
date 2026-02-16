"""
Quick Test Script for AI Employee System
Run this to verify everything is set up correctly
"""

import os
import sys
from pathlib import Path
from datetime import datetime


def check_folder_structure(vault_path: Path) -> bool:
    """Check if all required folders exist"""
    required_folders = [
        'Inbox',
        'Needs_Action',
        'Done',
        'Plans',
        'Pending_Approval',
        'Approved',
        'Rejected',
        'Logs',
        'Accounting',
        'Briefings'
    ]

    print("\n📁 Checking folder structure...")
    all_good = True

    for folder in required_folders:
        folder_path = vault_path / folder
        if folder_path.exists():
            print(f"  ✅ {folder}/")
        else:
            print(f"  ❌ {folder}/ - MISSING")
            all_good = False

    return all_good


def check_files(vault_path: Path) -> bool:
    """Check if all required files exist"""
    required_files = [
        'Dashboard.md',
        'Company_Handbook.md',
        'Business_Goals.md'
    ]

    print("\n📄 Checking required files...")
    all_good = True

    for file in required_files:
        file_path = vault_path / file
        if file_path.exists():
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file} - MISSING")
            all_good = False

    return all_good


def check_watchers() -> bool:
    """Check if watcher scripts exist"""
    watchers_path = Path(__file__).parent / 'watchers'

    required_watchers = [
        'base_watcher.py',
        'file_watcher.py',
        'gmail_watcher.py'
    ]

    print("\n👁️ Checking watcher scripts...")
    all_good = True

    for watcher in required_watchers:
        watcher_path = watchers_path / watcher
        if watcher_path.exists():
            print(f"  ✅ {watcher}")
        else:
            print(f"  ❌ {watcher} - MISSING")
            all_good = False

    return all_good


def check_dependencies() -> bool:
    """Check if required Python packages are installed"""
    print("\n📦 Checking dependencies...")

    dependencies = {
        'watchdog': 'File system watching',
    }

    optional_deps = {
        'google.oauth2': 'Gmail API',
        'playwright': 'WhatsApp automation'
    }

    all_good = True

    for module, desc in dependencies.items():
        try:
            __import__(module)
            print(f"  ✅ {module} ({desc})")
        except ImportError:
            print(f"  ❌ {module} ({desc}) - NOT INSTALLED")
            all_good = False

    print("\n📦 Optional dependencies:")
    for module, desc in optional_deps.items():
        try:
            __import__(module)
            print(f"  ✅ {module} ({desc})")
        except ImportError:
            print(f"  ⚠️ {module} ({desc}) - Not installed (optional)")

    return all_good


def test_file_creation(vault_path: Path) -> bool:
    """Test creating a file in Inbox"""
    print("\n🧪 Testing file creation...")

    inbox = vault_path / 'Inbox'
    test_file = inbox / f'TEST_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'

    try:
        test_file.write_text("This is a test file from the AI Employee system.")
        print(f"  ✅ Created test file: {test_file.name}")
        print(f"  📍 Location: {test_file}")
        print(f"  💡 Run file_watcher.py to see it processed!")
        return True
    except Exception as e:
        print(f"  ❌ Failed to create test file: {e}")
        return False


def main():
    print("=" * 50)
    print("🤖 AI Employee System Test")
    print("=" * 50)

    # Determine vault path
    vault_path = Path(__file__).parent / 'vault'

    if not vault_path.exists():
        print(f"\n❌ Vault not found at: {vault_path}")
        print("Please run setup first!")
        sys.exit(1)

    print(f"\n📂 Vault path: {vault_path}")

    # Run checks
    results = []
    results.append(("Folder Structure", check_folder_structure(vault_path)))
    results.append(("Required Files", check_files(vault_path)))
    results.append(("Watcher Scripts", check_watchers()))
    results.append(("Dependencies", check_dependencies()))
    results.append(("File Creation", test_file_creation(vault_path)))

    # Summary
    print("\n" + "=" * 50)
    print("📊 Summary")
    print("=" * 50)

    all_passed = True
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status} - {name}")
        if not passed:
            all_passed = False

    print("\n" + "=" * 50)

    if all_passed:
        print("🎉 All tests passed! Your AI Employee is ready.")
        print("\nNext steps:")
        print("1. Open vault/ folder in Obsidian")
        print("2. Run: python watchers/file_watcher.py --vault vault")
        print("3. Drop a file in vault/Inbox/ to test")
    else:
        print("⚠️ Some tests failed. Please fix the issues above.")
        print("\nTo install missing dependencies:")
        print("  pip install -r requirements.txt")

    print("=" * 50)


if __name__ == '__main__':
    main()
