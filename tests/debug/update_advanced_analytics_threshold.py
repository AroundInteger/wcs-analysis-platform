#!/usr/bin/env python3
"""
Update Advanced Analytics Threshold
This script updates the threshold for advanced analytics from 10 to 3 files
to make testing easier with the 5 test files we created.
"""

def update_threshold():
    """Update the threshold in app.py"""
    
    # Read the file
    with open('src/app.py', 'r') as f:
        content = f.read()
    
    # Count occurrences
    count_10 = content.count('len(all_results) >= 10')
    count_5 = content.count('len(all_results) >= 5')
    count_10_warning = content.count('Advanced analytics require at least 10 files')
    
    print(f"Found {count_10} instances of '>= 10'")
    print(f"Found {count_5} instances of '>= 5'")
    print(f"Found {count_10_warning} instances of warning message")
    
    # Replace all instances
    updated_content = content.replace('len(all_results) >= 10', 'len(all_results) >= 3')
    updated_content = updated_content.replace('len(all_results) >= 5', 'len(all_results) >= 2')
    updated_content = updated_content.replace('Advanced analytics require at least 10 files', 'Advanced analytics require at least 3 files')
    
    # Write back to file
    with open('src/app.py', 'w') as f:
        f.write(updated_content)
    
    print("✅ Successfully updated advanced analytics threshold!")
    print("📊 New thresholds:")
    print("   - Advanced Analytics: 3+ files (was 10)")
    print("   - Dashboard Analytics: 2+ files (was 5)")
    print("   - Basic Analytics: 1+ files (unchanged)")

if __name__ == "__main__":
    print("🔧 Updating Advanced Analytics Threshold")
    print("=" * 50)
    update_threshold()
    print("\n🎉 Ready for testing with 5 files!") 