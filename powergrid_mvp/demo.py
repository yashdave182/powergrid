import subprocess
import time
import webbrowser

print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║       POWERGRID PROJECT PREDICTION MVP - DEMO SCRIPT          ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
""")

print("\n🚀 Starting MVP Demo...\n")

# Step 1: Check if data exists
print("1️⃣  Checking for data files...")
import os
if not os.path.exists('data/raw/projects_data.csv'):
    print("   Generating synthetic data...")
    subprocess.run(['python', 'src/data/generate_synthetic_data.py'])
else:
    print("   ✅ Data files found")

# Step 2: Check if processed data exists
print("\n2️⃣  Checking for processed data...")
if not os.path.exists('data/processed/processed_data.csv'):
    print("   Running preprocessing...")
    subprocess.run(['python', 'src/data/preprocess.py'])
else:
    print("   ✅ Processed data found")

# Step 3: Check if models exist
print("\n3️⃣  Checking for trained models...")
if not os.path.exists('models/cost_xgboost.pkl'):
    print("   Training models (this may take a few minutes)...")
    subprocess.run(['python', 'src/models/train_models.py'])
else:
    print("   ✅ Models found")

# Step 4: Run tests
print("\n4️⃣  Running tests...")
subprocess.run(['python', 'tests/test_mvp.py'])

# Step 5: Start services
print("\n5️⃣  Starting services...")

print("\n   📊 Starting Streamlit Dashboard...")
print("   Dashboard will open at: http://localhost:8501")

subprocess.Popen(['streamlit', 'run', 'src/dashboard/app.py'])

time.sleep(3)
webbrowser.open('http://localhost:8501')

print("\n✅ Demo setup complete!")
print("\n" + "="*60)
print("NEXT STEPS:")
print("="*60)
print("1. Dashboard is now running at http://localhost:8501")
print("2. To start API, run: uvicorn src.api.main:app --reload")
print("3. API docs will be at: http://localhost:8000/docs")
print("\nPress Ctrl+C to stop the dashboard")
print("="*60)