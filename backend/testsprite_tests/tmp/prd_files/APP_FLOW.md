# Application Flow Documentation
**Project**: NexusChat — Internal Communications Platform
**Version**: 2.0 | ACM ReCode 2026

---

## 1. Entry Points

| Entry | Behaviour |
|---|---|
| Direct URL `/` | Redirect → `/login` if no session, `/dashboard` if session exists |
| `/login` | Default entry for all users |
| `/register` | New user signup |
| Any protected route without session | Redirect to `/login` with "Session expired" toast |

---

## 2. Core User Flows

### Flow 1: User Registration
**Entry**: `/register`

#### Happy Path
1. **Page: `/register`**
   - Components: shadcn `Input` (email, password, display name) + shadcn `Button`
   - Validation: Email format, password min 8 chars
   - Submit → `supabase.auth.signUp()`
2. **System**: Creates auth user → trigger auto-creates `profiles` row with role = `participant`
3. **Redirect** → `/dashboard`

#### Error States
- Invalid email → shadcn inline form error under field
- Password < 8 chars → inline error
- Email already exists → toast: "Account exists. Log in instead."

---

### Flow 2: User Login
**Entry**: `/login`

#### Happy Path
1. **Page: `/login`**
   - Components: shadcn `Input` + `Button` + link to `/register`
   - Submit → `supabase.auth.signInWithPassword()`
2. **Session created** → Redirect to `/dashboard`

#### Error States
- Wrong credentials → toast error: "Invalid credentials" (do not specify which field)
- Network error → toast error: "Connection failed. Try again."

---

### Flow 3: Dashboard & Room Selection
**Entry**: `/dashboard` (authenticated)

#### Layout on Load
```
[Header]
[Sidebar: Room List] | [Main Panel: "Select a room to start chatting"]
[Sidebar: User List] |
```

#### Room Selection
1. User clicks room in sidebar
2. Previous realtime subscription unsubscribed (cleanup)
3. Message history fetched for new room
4. New realtime subscription created for new room
5. Message list renders with Lenis smooth scroll container
6. Auto-scroll to bottom with smooth motion

#### Role-Specific UI Differences

| UI Element | Admin | Moderator | Participant |
|---|---|---|---|
| "+" Create Room button | ✅ | ❌ | ❌ |
| Room trash icon | ✅ | ❌ | ❌ |
| Message delete button | ✅ | ✅ | ❌ |
| Manage Users panel | ✅ | ❌ | ❌ |
| Slash `/kick` command | ✅ | ✅ | ❌ |
| Slash `/promote` command | ✅ | ❌ | ❌ |

---

### Flow 4: Real-Time Messaging
**Entry**: Inside any room on `/dashboard`

#### Happy Path
1. User types in shadcn `Input` at bottom of chat
2. Presses Enter or clicks Send (`Button` from shadcn)
3. If message starts with `/` → route to command parser (skip DB insert)
4. Otherwise → `supabase.from('messages').insert()`
5. Supabase Realtime broadcasts INSERT event to all room subscribers
6. Each subscriber receives event → anime.js fade-in animation on new message
7. Lenis smooth-scrolls to bottom

#### Message Display Format
```
┌──────────────────────────────────────────────────────────┐
│  [A]  Aaryan Raorane  [ADMIN]               9:34 PM  [🗑] │
│       Message content here...                             │
│                                                           │
│  [J]  Jamie Singh     [PARTICIPANT]         9:35 PM       │
│       Another message here...                             │
└──────────────────────────────────────────────────────────┘
```
- Avatar: Circle with user initials, coloured by role
- Role badge: shadcn `Badge` component, coloured by role
- Delete icon: Only rendered for admin/moderator, appears on row hover
- Animation: Each new message fades in via anime.js (opacity 0→1, translateY 8px→0, 250ms)

#### Edge Cases
- Empty message → don't submit, brief shake animation on input (anime.js)
- WebSocket disconnects → yellow banner "Reconnecting..." (uiverse.io alert style)
- Very long message → word-wrap, no horizontal scroll

---

### Flow 5: Admin — Room Management

#### Create Room
1. Admin clicks "+" button (sidebar, admin-only)
2. shadcn `Dialog` modal opens: room name `Input` + Create `Button`
3. Validation: name required, no duplicate names
4. Insert into `rooms` table
5. New room appears in sidebar for ALL users via Realtime subscription on `rooms` table

#### Delete Room
1. Admin clicks trash icon next to room name
2. shadcn `AlertDialog` (confirmation): "Delete [Room Name]? All messages will be permanently deleted."
3. Admin clicks "Delete" → delete from `rooms` (cascade deletes all messages)
4. Users currently in that room → redirect to empty state

---

### Flow 6: Admin — Role Management
**Entry**: Manage Users panel (admin-only button in header or sidebar)

1. Admin opens panel → sees list of all users with shadcn `Badge` showing current role
2. Each user has a shadcn `DropdownMenu` with role options
3. Admin selects new role → `supabase.from('profiles').update()`
4. User's badge updates on next render or realtime profile subscription

---

### Flow 7: Slash Commands

#### Command Detection
```
User types:  /help
Frontend:    Detects leading "/"
             Parses command name + args
             Does NOT insert into messages table
             Executes command handler
             Posts styled system message to chat UI (not to DB)
```

#### Supported Commands

| Command | Roles | Output |
|---|---|---|
| `/help` | All | Lists all commands in system message |
| `/rooms` | All | Lists all rooms |
| `/kick @username` | Mod + Admin | Removes user from room |
| `/promote @username` | Admin only | Promotes to moderator |

#### System Message Style (uiverse.io inspired)
```
┌────────────────────────────────────────────┐
│  🤖  NexusBot                  9:36 PM     │
│  Available commands:                       │
│  /help · /rooms · /kick · /promote        │
└────────────────────────────────────────────┘
```
- Grey/muted background, italic text, bot icon
- No delete button (system messages are not in DB)
- Fade-in via anime.js same as regular messages

---

## 3. Navigation Map

```
/ ──────────────────── Auth check
                           ├── No session ──── /login
                           └── Session ──────── /dashboard

/login ─────────────────── Submit ──────────── /dashboard
                           Register link ───── /register

/register ──────────────── Submit ──────────── /dashboard
                           Login link ──────── /login

/dashboard ─────────────── Sidebar: Room list (realtime)
           │                         User list (realtime)
           │                         + Create Room (admin)
           │
           ├── Chat Panel ─────────── Message history
           │                          Realtime subscription
           │                          Message input
           │                          Delete (admin/mod)
           │                          Slash commands
           │
           └── Manage Users ────────── Role dropdowns (admin)

/* ──────────────────────── 404 page + home link
```

---

## 4. Screen Inventory

| Screen | Route | Access | Key Components Used |
|---|---|---|---|
| Login | `/login` | Public | shadcn Input, Button |
| Register | `/register` | Public | shadcn Input, Button |
| Dashboard | `/dashboard` | Authenticated | Full app shell |
| 404 | `/*` | Public | Simple message + link |

---

## 5. Animation & Scroll Behaviour

### Lenis (Smooth Scroll)
- Applied to: Message feed scroll container only
- Behaviour: Smooth inertia-based scroll
- Auto-scroll: On new message, call `lenis.scrollTo('bottom')` with `{ duration: 0.6 }`
- Do NOT apply Lenis to full-page scroll (only the message list container)

### Anime.js Animations
| Trigger | Animation | Duration |
|---|---|---|
| New message appears | fadeIn + translateY(8px → 0) | 250ms ease-out |
| Modal opens | scaleY(0.95 → 1) + opacity(0 → 1) | 200ms |
| Toast notification | slideIn from right | 300ms |
| Empty input shake | translateX(±6px, 3 cycles) | 400ms |
| Role badge update | pulse + colour transition | 300ms |

---

## 6. Error & Empty States

| Situation | Component | Message |
|---|---|---|
| No rooms yet | uiverse.io empty state card | "No rooms yet. Ask your admin to create one." |
| No messages in room | Centered muted text | "No messages yet. Say hello! 👋" |
| Connection lost | uiverse.io alert banner (yellow) | "Connection lost. Reconnecting..." |
| Session expired | Toast + redirect | "Session expired. Please log in again." |
| Unauthorized action | Toast (red) | "You don't have permission to do this." |
| Unknown slash command | System message | "Unknown command. Type /help for a list." |
