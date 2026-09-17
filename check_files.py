import os

required_files = [
    'results.csv', 'wc_2026_fixtures.csv', 'Fifa world cup data.csv',
    'former_names.csv', 'teams.csv', 'shootouts.csv', 'goalscorers.csv'
]

print("🔍 Checking project folder directory...")
missing_files = 0

for file in required_files:
    if os.path.exists(file):
        print(f"  ✅ Found: {file}")
    else:
        print(f"  ❌ MISSING: {file} (Check spelling or folder location)")
        missing_files += 1

if missing_files == 0:
    print("\n🚀 Environment check passed! All data files are in place and ready.")
else:
    print(f"\n⚠️ Action required: {missing_files} file(s) could not be located in this directory.")