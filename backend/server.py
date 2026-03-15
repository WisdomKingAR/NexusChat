import os
import bcrypt
import logging
import uvicorn
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Dict, Any, cast
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, status, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse
from jose import JWTError, jwt
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from bson import ObjectId
import re

OBJECTID_RE = re.compile(r"^[0-9a-f]{24}$")

def validate_object_id(value: str, name: str = "ID") -> ObjectId:
    if not OBJECTID_RE.match(value):
        raise HTTPException(status_code=400, detail=f"Invalid {name} format")
    return ObjectId(value)
from dotenv import load_dotenv
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Configuration
MONGO_URL = os.getenv("MONGO_URL")
DB_NAME = os.getenv("DB_NAME", "nexuschat_v3")
JWT_SECRET = os.getenv("JWT_SECRET")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 24 * 60  # 24 hours
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000,http://localhost:3001").split(",")
PORT = int(os.getenv("PORT", 8001))

logger.debug(f"CORS_ORIGINS loaded: {CORS_ORIGINS}")

# Fail loudly on startup if critical secrets are missing
required_vars = ["MONGO_URL", "JWT_SECRET"]
missing = [v for v in required_vars if not os.getenv(v)]
if missing:
    logger.error(f"Missing required environment variables: {missing}")
    raise EnvironmentError(f"Missing required environment variables: {missing}")

if JWT_SECRET and len(JWT_SECRET) < 32:
    logger.warning("JWT_SECRET is too short! Use at least 32 characters for security.")

# Initialize FastAPI
app = FastAPI(title="NexusChat v3 API")

def get_user_identifier(request: Request) -> str:
    # Get user identifier from Auth token if available, else fallback to IP
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
            email = payload.get("sub")
            if email:
                return f"user:{email}"
        except Exception:
            pass
    return f"ip:{get_remote_address(request)}"

limiter = Limiter(key_func=get_user_identifier)
app.state.limiter = limiter

@app.exception_handler(RateLimitExceeded)
async def custom_rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Too many requests. Please slow down.", "retry_after": str(exc.detail)}
    )

# Global Exception Handler to prevent information disclosure
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error. Please try again later."}
    )

# CORS
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response: Response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        return response

app.add_middleware(SecurityHeadersMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

@app.get("/")
async def root():
    return {"status": "online", "message": "NexusChat v3 API", "version": "3.0.0"}

# MongoDB Client
try:
    client = AsyncIOMotorClient(MONGO_URL, serverSelectionTimeoutMS=5000)
    db = client[DB_NAME]
    # Simple check to verify connection
    logger.debug("Initializing MongoDB connection...")
except Exception as e:
    logger.error(f"Failed to connect to MongoDB at {MONGO_URL}: {e}")

@app.on_event("startup")
async def create_indexes():
    await db.users.create_index("email", unique=True)
    # Optimized compound index for fetching room messages sorted by time
    await db.messages.create_index([("room_id", 1), ("created_at", 1)])
    await db.messages.create_index("room_id")
    await db.messages.create_index("created_at")
    logger.info("MongoDB indexes ensured")

# OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# --- Models ---

class UserBase(BaseModel):
    email: EmailStr
    display_name: str = Field(..., min_length=1, max_length=50, pattern=r"^[a-zA-Z0-9 _.-]+$")

    model_config = ConfigDict(extra='forbid')

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100)

class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)

    model_config = ConfigDict(extra='forbid')

class UserPublicProfile(BaseModel):
    id: str = Field(..., pattern=r"^[0-9a-f]{24}$")
    display_name: str
    role: str
    created_at: datetime
    is_online: bool = False

    model_config = ConfigDict(arbitrary_types_allowed=True, json_encoders={ObjectId: str}, extra='forbid')

class UserProfile(UserPublicProfile):
    email: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserProfile

class RoomBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50, pattern=r"^[a-zA-Z0-9 _-]+$")
    is_private: bool = False

    model_config = ConfigDict(extra='forbid')

class RoomCreate(RoomBase):
    members: List[str] = Field(default_factory=list)

class Room(RoomBase):
    id: str = Field(..., pattern=r"^[0-9a-f]{24}$")
    created_by: str = Field(..., pattern=r"^[0-9a-f]{24}$")
    created_at: datetime
    members: List[str] = Field(default_factory=list)

    model_config = ConfigDict(extra='forbid')

class MessageBase(BaseModel):
    content: str = Field(..., min_length=1, max_length=1000)

    model_config = ConfigDict(extra='forbid')

class MessageCreate(MessageBase):
    pass

class Message(MessageBase):
    id: str = Field(..., pattern=r"^[0-9a-f]{24}$")
    room_id: str = Field(..., pattern=r"^[0-9a-f]{24}$")
    sender_id: str = Field(..., pattern=r"^[0-9a-f]{24}$")
    sender_name: str = Field(..., min_length=1, max_length=100)
    sender_role: str = Field(..., pattern="^(admin|moderator|participant|system)$")
    created_at: datetime

    model_config = ConfigDict(extra='forbid')

class CommandRequest(BaseModel):
    command: str = Field(..., min_length=1, max_length=20, pattern=r"^[a-z]+$")
    args: List[str] = Field(default_factory=list, max_length=10)
    room_id: str = Field(..., pattern=r"^[0-9a-f]{24}$")

    model_config = ConfigDict(extra='forbid')

class RoleUpdate(BaseModel):
    role: str = Field(..., pattern="^(admin|moderator|participant)$")

    model_config = ConfigDict(extra='forbid')

# --- WebSocket Manager ---

class ConnectionManager:
    def __init__(self):
        # room_id -> list of (user_id, WebSocket) tuples
        self.active_connections: Dict[str, List[tuple[str, WebSocket]]] = {}

    async def connect(self, websocket: WebSocket, room_id: str, user_id: str):
        await websocket.accept()
        if room_id not in self.active_connections:
            self.active_connections[room_id] = []
        self.active_connections[room_id].append((user_id, websocket))

    def disconnect(self, websocket: WebSocket, room_id: str):
        if room_id in self.active_connections:
            self.active_connections[room_id] = [
                (uid, ws) for uid, ws in self.active_connections[room_id]
                if ws is not websocket
            ]
            if not self.active_connections[room_id]:
                self.active_connections.pop(room_id, None)

    async def broadcast(self, room_id: str, message: dict):
        if room_id in self.active_connections:
            for _, ws in self.active_connections[room_id]:
                try:
                    await ws.send_json(message)
                except Exception:
                    pass

    async def disconnect_user(self, room_id: str, user_id: str):
        """Close all WebSocket connections for a specific user in a room."""
        if room_id not in self.active_connections:
            return
        to_close = [ws for uid, ws in self.active_connections[room_id] if uid == user_id]
        for ws in to_close:
            try:
                await ws.close(code=4003)  # custom code: kicked
            except Exception:
                pass
        self.active_connections[room_id] = [
            (uid, ws) for uid, ws in self.active_connections[room_id]
            if uid != user_id
        ]

class DmConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[tuple[str, WebSocket]]] = {}

    async def connect(self, websocket: WebSocket, channel_id: str, user_id: str):
        await websocket.accept()
        if channel_id not in self.active_connections:
            self.active_connections[channel_id] = []
        self.active_connections[channel_id].append((user_id, websocket))

    def disconnect(self, websocket: WebSocket, channel_id: str):
        if channel_id in self.active_connections:
            self.active_connections[channel_id] = [
                (uid, ws) for uid, ws in self.active_connections[channel_id]
                if ws is not websocket
            ]
            if not self.active_connections[channel_id]:
                self.active_connections.pop(channel_id, None)

    async def broadcast(self, channel_id: str, message: dict):
        if channel_id in self.active_connections:
            for _, ws in self.active_connections[channel_id]:
                try:
                    await ws.send_json(message)
                except Exception:
                    pass

manager = ConnectionManager()
dm_manager = DmConnectionManager()

# --- Utilities ---

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme)) -> Any:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        email: Optional[str] = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user_doc = await db.users.find_one({"email": email})
    if not user_doc:
        raise credentials_exception
    
    return {
        "id": str(user_doc["_id"]),
        "email": str(user_doc["email"]),
        "display_name": str(user_doc["display_name"]),
        "role": str(user_doc["role"]),
        "created_at": cast(datetime, user_doc["created_at"])
    }

# --- Auth Routes ---

@app.post("/api/auth/register", response_model=Token)
@limiter.limit("5/minute")
async def register(request: Request, user_in: UserCreate):
    # Check if user exists
    existing_user = await db.users.find_one({"email": user_in.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Check if this is the first user (for admin role)
    count = await db.users.count_documents({})
    role = "admin" if count == 0 else "participant"
    
    user_doc = {
        "email": user_in.email,
        "password_hash": hash_password(user_in.password),
        "display_name": user_in.display_name,
        "role": role,
        "created_at": datetime.now(timezone.utc)
    }
    
    result = await db.users.insert_one(user_doc)
    user_id = str(result.inserted_id)
    
    profile = {
        "id": user_id,
        "email": user_in.email,
        "display_name": user_in.display_name,
        "role": role,
        "created_at": user_doc["created_at"]
    }
    
    access_token = create_access_token(data={"sub": user_in.email})
    
    return {"access_token": access_token, "token_type": "bearer", "user": profile}

@app.post("/api/auth/login", response_model=Token)
@limiter.limit("10/minute")
async def login(request: Request, user_in: UserLogin):
    user = await db.users.find_one({"email": user_in.email})
    if not user or not verify_password(user_in.password, user["password_hash"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    profile = {
        "id": str(user["_id"]),
        "email": user["email"],
        "display_name": user["display_name"],
        "role": user["role"],
        "created_at": user["created_at"]
    }
    
    access_token = create_access_token(data={"sub": user["email"]})
    
    return {"access_token": access_token, "token_type": "bearer", "user": profile}

@app.get("/api/auth/me", response_model=UserProfile)
@limiter.limit("20/minute")
async def get_me(request: Request, current_user: dict = Depends(get_current_user)):
    return current_user

# --- Room Routes ---

@app.get("/api/rooms", response_model=List[Room])
@limiter.limit("20/minute")
async def get_rooms(request: Request, current_user: dict = Depends(get_current_user)):
    rooms = []
    user_id = str(current_user["id"])
    async for room in db.rooms.find():
        is_private = room.get("is_private", False)
        members = room.get("members", [])
        if is_private and current_user["role"] != "admin" and user_id not in members:
            continue
        
        rooms.append({
            "id": str(room["_id"]),
            "name": room["name"],
            "created_by": str(room["created_by"]),
            "created_at": room["created_at"],
            "is_private": is_private,
            "members": members
        })
    return rooms

@app.post("/api/rooms", response_model=Room)
@limiter.limit("10/minute")
async def create_room(request: Request, room_in: RoomCreate, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only admins can create rooms")
    
    existing = await db.rooms.find_one({"name": room_in.name})
    if existing:
        raise HTTPException(status_code=400, detail="Room name already exists")
    
    room_doc = {
        "name": room_in.name,
        "created_by": ObjectId(current_user["id"]),
        "created_at": datetime.now(timezone.utc),
        "is_private": room_in.is_private,
        "members": room_in.members
    }
    result = await db.rooms.insert_one(room_doc)
    return {
        "id": str(result.inserted_id),
        "name": room_in.name,
        "created_by": str(current_user["id"]),
        "created_at": room_doc["created_at"],
        "is_private": room_in.is_private,
        "members": room_in.members
    }

@app.delete("/api/rooms/{room_id}")
@limiter.limit("5/minute")
async def delete_room(room_id: str, request: Request, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only admins can delete rooms")
    
    room_oid = validate_object_id(room_id, "room_id")
    await db.messages.delete_many({"room_id": room_oid})
    result = await db.rooms.delete_one({"_id": room_oid})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Room not found")
    
    # Broadcast room deletion
    await manager.broadcast(room_id, {"type": "room_deleted", "room_id": room_id})
    return {"status": "success"}

# --- Message Routes ---

@app.get("/api/rooms/{room_id}/messages", response_model=List[Message])
@limiter.limit("30/minute")
async def get_messages(room_id: str, request: Request, current_user: dict = Depends(get_current_user)):
    room_oid = validate_object_id(room_id, "room_id")
    room = await db.rooms.find_one({"_id": room_oid})
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    if current_user["id"] in room.get("banned_users", []):
        raise HTTPException(status_code=403, detail="You have been kicked from this room")
        
    is_private = room.get("is_private", False)
    members = room.get("members", [])
    if is_private and current_user["role"] != "admin" and current_user["id"] not in members:
        raise HTTPException(status_code=403, detail="Access denied")

    messages = []
    # Join with users to get sender details
    pipeline = [
        {"$match": {"room_id": room_oid}},
        {"$sort": {"created_at": -1}},
        {"$limit": 50},
        {
            "$lookup": {
                "from": "users",
                "localField": "sender_id",
                "foreignField": "_id",
                "as": "sender"
            }
        },
        {"$unwind": "$sender"}
    ]
    
    async for msg in db.messages.aggregate(pipeline):
        messages.append({
            "id": str(msg["_id"]),
            "room_id": str(msg["room_id"]),
            "sender_id": str(msg["sender_id"]),
            "sender_name": msg["sender"]["display_name"],
            "sender_role": msg["sender"]["role"],
            "content": msg["content"],
            "created_at": msg["created_at"].replace(tzinfo=timezone.utc)
        })
    return sorted(messages, key=lambda x: x["created_at"])

@app.post("/api/rooms/{room_id}/messages", response_model=Message)
@limiter.limit("60/minute")
async def send_message(room_id: str, request: Request, msg_in: MessageCreate, current_user: dict = Depends(get_current_user)):
    room_oid = validate_object_id(room_id, "room_id")
    room = await db.rooms.find_one({"_id": room_oid})
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    # Prevent banned users from posting
    if current_user["id"] in room.get("banned_users", []):
        raise HTTPException(status_code=403, detail="You have been kicked from this room")
        
    is_private = room.get("is_private", False)
    members = room.get("members", [])
    if is_private and current_user["role"] != "admin" and current_user["id"] not in members:
        raise HTTPException(status_code=403, detail="Access denied")

    msg_doc = {
        "room_id": room_oid,
        "sender_id": ObjectId(current_user["id"]),
        "content": msg_in.content,
        "created_at": datetime.now(timezone.utc)
    }
    result = await db.messages.insert_one(msg_doc)
    
    temp_iso = msg_doc["created_at"].isoformat()
    if not temp_iso.endswith("Z"):
        temp_iso = temp_iso.replace("+00:00", "Z")
        if not temp_iso.endswith("Z"):
            temp_iso += "Z"
            
    message_data = {
        "id": str(result.inserted_id),
        "room_id": room_id,
        "sender_id": current_user["id"],
        "sender_name": current_user["display_name"],
        "sender_role": current_user["role"],
        "content": msg_in.content,
        "created_at": temp_iso
    }
    
    # Broadcast via WebSocket
    await manager.broadcast(room_id, {"type": "new_message", "message": message_data})
    
    # Check for slash commands (very basic server-side handling example)
    # Most parsing is on frontend, but we could handle some here if needed.
    
    return message_data

@app.delete("/api/messages/{message_id}")
@limiter.limit("30/minute")
async def delete_message(message_id: str, request: Request, current_user: dict = Depends(get_current_user)):
    msg_oid = validate_object_id(message_id, "message_id")
    msg = await db.messages.find_one({"_id": msg_oid})
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")
    
    room_id = str(msg["room_id"])
    
    # Permissions: Admin, Moderator, or Owner
    if current_user["role"] not in ["admin", "moderator"] and current_user["id"] != str(msg["sender_id"]):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    await db.messages.delete_one({"_id": msg_oid})
    
    # Broadcast deletion
    await manager.broadcast(room_id, {"type": "delete_message", "message_id": message_id})
    return {"status": "success"}

# --- User Management ---

@app.get("/api/users", response_model=List[UserPublicProfile])
@limiter.limit("10/minute")
async def get_users(request: Request, current_user: dict = Depends(get_current_user)):
    users = []
    async for user in db.users.find():
        users.append({
            "id": str(user["_id"]),
            "display_name": user["display_name"],
            "role": user["role"],
            "created_at": user["created_at"]
        })
    return users

@app.put("/api/users/{user_id}/role")
@limiter.limit("5/minute")
async def update_user_role(user_id: str, request: Request, role_data: RoleUpdate, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only admins can manage roles")
    if user_id == current_user["id"]:
        raise HTTPException(status_code=400, detail="Cannot change your own role")
    
    user_oid = validate_object_id(user_id, "user_id")
    new_role = role_data.role
    await db.users.update_one({"_id": user_oid}, {"$set": {"role": new_role}})
    
    # Broadcast role update
    for room_id in manager.active_connections:
        await manager.broadcast(room_id, {
            "type": "role_updated", 
            "user_id": user_id, 
            "new_role": new_role
        })
        
    return {"status": "success"}

# --- Slash Commands ---

@app.post("/api/commands")
@limiter.limit("20/minute")
async def execute_command(request: Request, cmd_req: CommandRequest, current_user: dict = Depends(get_current_user)):
    command = cmd_req.command.lower()
    args = cmd_req.args
    room_id = cmd_req.room_id
    
    if command == "help":
        response = "Available: /help, /rooms, /kick @user, /promote @user"
    elif command == "rooms":
        # Get count instead to prevent spamming
        rooms_count = await db.rooms.count_documents({})
        response = f"There are currently {rooms_count} rooms on the server."
    elif command == "kick":
        if current_user["role"] not in ["admin", "moderator"]:
            return {"status": "error", "message": "Permission denied"}
        if not args:
            return {"status": "error", "message": "Usage: /kick @username"}
        
        target_name = args[0].lstrip("@")
        target_user = await db.users.find_one({"display_name": target_name})
        if not target_user:
            return {"status": "error", "message": f"User '{target_name}' not found"}
            
        target_id = str(target_user["_id"])

        # Prevent kicking admins
        if target_user["role"] == "admin":
            return {"status": "error", "message": "Cannot kick an admin"}

        # 1. Persist ban in the room document
        room_oid = validate_object_id(room_id, "room_id")
        await db.rooms.update_one(
            {"_id": room_oid},
            {"$addToSet": {"banned_users": target_id}}
        )

        # 2. Broadcast the kick event (so frontend can react)
        await manager.broadcast(room_id, {
            "type": "user_kicked",
            "user_id": target_id,
            "user_name": target_name,
            "kicked_by": current_user["display_name"]
        })

        # 3. Force-disconnect the user's WebSocket(s)
        await manager.disconnect_user(room_id, target_id)

        response = f"Kicked {target_name} from the room"
    elif command == "promote":
        if current_user["role"] != "admin":
            return {"status": "error", "message": "Permission denied"}
        if not args:
            return {"status": "error", "message": "Usage: /promote @username"}
            
        target_name = args[0].lstrip("@")
        target_user = await db.users.find_one({"display_name": target_name})
        if not target_user:
            return {"status": "error", "message": f"User '{target_name}' not found"}
            
        new_role = "moderator" if target_user["role"] == "participant" else "admin"
        await db.users.update_one({"_id": target_user["_id"]}, {"$set": {"role": new_role}})
        
        # Broadcast role update globally
        for active_room in manager.active_connections:
            await manager.broadcast(active_room, {
                "type": "role_updated",
                "user_id": str(target_user["_id"]),
                "new_role": new_role
            })
            
        response = f"Promoted {target_name} to {new_role}"
    elif command == "demote":
        if current_user["role"] != "admin":
            return {"status": "error", "message": "Permission denied"}
        if not args:
            return {"status": "error", "message": "Usage: /demote @username"}
            
        target_name = args[0].lstrip("@")
        target_user = await db.users.find_one({"display_name": target_name})
        if not target_user:
            return {"status": "error", "message": f"User '{target_name}' not found"}
            
        if target_user["role"] == "participant":
            return {"status": "error", "message": f"User '{target_name}' is already a participant"}
            
        if target_user["role"] == "admin":
            return {"status": "error", "message": f"Cannot demote an admin"}
            
        new_role = "participant"
        await db.users.update_one({"_id": target_user["_id"]}, {"$set": {"role": new_role}})
        
        # Broadcast role update globally
        for active_room in manager.active_connections:
            await manager.broadcast(active_room, {
                "type": "role_updated",
                "user_id": str(target_user["_id"]),
                "new_role": new_role
            })
            
        response = f"Demoted {target_name} to {new_role}"
    else:
        response = f"Unknown: /{command}"
        
    return {"status": "success", "message": response}

# --- WebSocket ---

@app.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str, token: str = Query(...)):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        email: Optional[str] = payload.get("sub")
        if not email:
            raise JWTError()
        user = await db.users.find_one({"email": email})
        if not user:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
    except JWTError:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    # Check if user is banned from this room
    room_oid = validate_object_id(room_id, "room_id")
    room = await db.rooms.find_one({"_id": room_oid})
    if not room:
        await websocket.close(code=4004)
        return
        
    if str(user["_id"]) in room.get("banned_users", []):
        await websocket.close(code=4003)
        return
        
    is_private = room.get("is_private", False)
    members = room.get("members", [])
    if is_private and user["role"] != "admin" and str(user["_id"]) not in members:
        await websocket.close(code=4003)
        return

    user_id = str(user["_id"])
    await manager.connect(websocket, room_id, user_id)
    await manager.broadcast(room_id, {
        "type": "user_joined",
        "user": {
            "id": str(user["_id"]),
            "display_name": user["display_name"],
            "role": user["role"]
        }
    })
    
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, room_id)
        await manager.broadcast(room_id, {
            "type": "user_left",
            "user_id": str(user["_id"])
        })

# --- DM Routes ---

@app.get("/api/dm/channels")
@limiter.limit("20/minute")
async def get_dm_channels(request: Request, current_user: dict = Depends(get_current_user)):
    user_id = str(current_user["id"])
    channels = []
    async for channel in db.dm_channels.find({"participants": user_id}):
        channels.append({
            "id": str(channel["_id"]),
            "participants": channel["participants"],
            "created_at": channel["created_at"],
            "updated_at": channel.get("updated_at", channel["created_at"])
        })
    return channels

@app.post("/api/dm/channels")
@limiter.limit("10/minute")
async def create_dm_channel(request: Request, recipient_id: str = Query(...), current_user: dict = Depends(get_current_user)):
    user_id = str(current_user["id"])
    if user_id == recipient_id:
        raise HTTPException(status_code=400, detail="Cannot create DM with yourself")
        
    # Check if recipient exists
    try:
        recipient_oid = validate_object_id(recipient_id, "recipient_id")
        recipient = await db.users.find_one({"_id": recipient_oid})
        if not recipient:
             raise HTTPException(status_code=404, detail="User not found")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid user ID")

    participants = sorted([user_id, recipient_id])
    existing = await db.dm_channels.find_one({"participants": participants})
    if existing:
        return {
            "id": str(existing["_id"]),
            "participants": existing["participants"],
            "created_at": existing["created_at"]
        }
        
    now = datetime.now(timezone.utc)
    new_channel = {
        "participants": participants,
        "created_at": now,
        "updated_at": now
    }
    result = await db.dm_channels.insert_one(new_channel)
    return {
        "id": str(result.inserted_id),
        "participants": participants,
        "created_at": new_channel["created_at"]
    }

@app.get("/api/dm/channels/{channel_id}/messages")
@limiter.limit("30/minute")
async def get_dm_messages(channel_id: str, request: Request, current_user: dict = Depends(get_current_user)):
    channel_oid = validate_object_id(channel_id, "channel_id")
    channel = await db.dm_channels.find_one({"_id": channel_oid})
    if not channel or str(current_user["id"]) not in channel["participants"]:
        raise HTTPException(status_code=403, detail="Access denied")

    messages = []
    pipeline = [
        {"$match": {"channel_id": channel_oid}},
        {"$sort": {"created_at": -1}},
        {"$limit": 50},
        {
            "$lookup": {
                "from": "users",
                "localField": "sender_id",
                "foreignField": "_id",
                "as": "sender"
            }
        },
        {"$unwind": "$sender"}
    ]
    
    async for msg in db.dm_messages.aggregate(pipeline):
        messages.append({
            "id": str(msg["_id"]),
            "channel_id": str(msg["channel_id"]),
            "sender_id": str(msg["sender_id"]),
            "sender_name": msg["sender"]["display_name"],
            "content": msg["content"],
            "created_at": msg["created_at"].replace(tzinfo=timezone.utc)
        })
    return sorted(messages, key=lambda x: x["created_at"])

@app.post("/api/dm/channels/{channel_id}/messages")
@limiter.limit("60/minute")
async def send_dm_message(channel_id: str, request: Request, msg_in: MessageCreate, current_user: dict = Depends(get_current_user)):
    channel_oid = validate_object_id(channel_id, "channel_id")
    channel = await db.dm_channels.find_one({"_id": channel_oid})
    if not channel or str(current_user["id"]) not in channel["participants"]:
        raise HTTPException(status_code=403, detail="Access denied")

    now_dt = datetime.now(timezone.utc)
    msg_doc = {
        "channel_id": channel_oid,
        "sender_id": ObjectId(current_user["id"]),
        "content": msg_in.content,
        "created_at": now_dt
    }
    result = await db.dm_messages.insert_one(msg_doc)
    
    await db.dm_channels.update_one(
        {"_id": channel_oid},
        {"$set": {"updated_at": now_dt}}
    )
    
    temp_iso = msg_doc["created_at"].isoformat()
    if not temp_iso.endswith("Z"):
        temp_iso = temp_iso.replace("+00:00", "Z")
        if not temp_iso.endswith("Z"):
            temp_iso += "Z"
            
    message_data = {
        "id": str(result.inserted_id),
        "channel_id": channel_id,
        "sender_id": current_user["id"],
        "sender_name": current_user["display_name"],
        "content": msg_in.content,
        "created_at": temp_iso
    }
    
    await dm_manager.broadcast(channel_id, {"type": "new_dm", "message": message_data})
    
    return message_data

@app.websocket("/ws/dm/{channel_id}")
async def dm_websocket_endpoint(websocket: WebSocket, channel_id: str, token: str = Query(...)):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        email: Optional[str] = payload.get("sub")
        if not email:
            raise JWTError()
        user = await db.users.find_one({"email": email})
        if not user:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
    except JWTError:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    channel_oid = validate_object_id(channel_id, "channel_id")
    channel = await db.dm_channels.find_one({"_id": channel_oid})
    if not channel or str(user["_id"]) not in channel["participants"]:
        await websocket.close(code=4003)
        return

    user_id = str(user["_id"])
    await dm_manager.connect(websocket, channel_id, user_id)
    
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        dm_manager.disconnect(websocket, channel_id)

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=PORT, reload=True)

