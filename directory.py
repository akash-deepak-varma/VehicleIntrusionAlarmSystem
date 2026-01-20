import os

# Base project folder
base_dir = r"D:\Akash\FinalYear\vehicle_alert_system"

# List of directories to create
dirs = [
    "data/videos",
    "data/images",
    "configs",
    "models/tracker",
    "src",
    "logs",
    "snapshots"
]

# Create directories
for d in dirs:
    dir_path = os.path.join(base_dir, d)
    os.makedirs(dir_path, exist_ok=True)  # exist_ok=True avoids errors if folder exists
    print(f"Created: {dir_path}")

print("\nAll directories created successfully!")
