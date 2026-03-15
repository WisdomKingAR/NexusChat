
import sys

imports = [
    "os",
    "bcrypt",
    "logging",
    "uvicorn",
    "datetime",
    "typing",
    "fastapi",
    "jose",
    "motor",
    "pydantic",
    "bson",
    "dotenv",
    "slowapi"
]

print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")
print("-" * 20)

for module in imports:
    try:
        __import__(module)
        print(f"SUCCESS: {module}")
    except ImportError as e:
        print(f"FAILED: {module} - {e}")
    except Exception as e:
        print(f"ERROR: {module} - {e}")
