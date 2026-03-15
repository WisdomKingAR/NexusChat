try:
    from fastapi.middleware.cors import CORSMiddleware
    print("FastAPI CORS import success")
except ImportError as e:
    print(f"FastAPI CORS import failed: {e}")

try:
    from starlette.middleware.cors import CORSMiddleware
    print("Starlette CORS import success")
except ImportError as e:
    print(f"Starlette CORS import failed: {e}")
