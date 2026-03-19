# Backend Structure Documentation
**Project**: NexusChat — Internal Communications Platform
**Version**: 2.0 | ACM ReCode 2026

---

## Architecture

There is **no custom backend server** in this project. Supabase is your entire backend. All data operations go through the Supabase JS client. All permissions are enforced via Row Level Security at the database level — server-side, not in frontend code.

**Critical distinction**: Hiding a button in React is UI. An RLS policy is security. You need both, but only one actually protects the data.

---

## 1. Database Schema

### `profiles` table
```sql
CREATE TABLE profiles (
  id            UUID REFERENCES auth.users PRIMARY KEY,
  email         TEXT NOT NULL,
  display_name  TEXT NOT NULL,
  role          TEXT NOT NULL DEFAULT 'participant'
                CHECK (role IN ('admin', 'moderator', 'participant')),
  created_at    TIMESTAMPTZ DEFAULT NOW()
);
```

### `rooms` table
```sql
CREATE TABLE rooms (
  id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  name        TEXT UNIQUE NOT NULL,
  created_by  UUID REFERENCES profiles(id),
  created_at  TIMESTAMPTZ DEFAULT NOW()
);
```

### `messages` table
```sql
CREATE TABLE messages (
  id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  room_id     UUID REFERENCES rooms(id) ON DELETE CASCADE NOT NULL,
  sender_id   UUID REFERENCES profiles(id) NOT NULL,
  content     TEXT NOT NULL,
  created_at  TIMESTAMPTZ DEFAULT NOW()
);
```

---

## 2. Auto-Profile Trigger

Runs automatically when a new user signs up via Supabase Auth:

```sql
CREATE OR REPLACE FUNCTION handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO profiles (id, email, display_name, role)
  VALUES (
    NEW.id,
    NEW.email,
    SPLIT_PART(NEW.email, '@', 1),
    'participant'
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER on_auth_user_created
AFTER INSERT ON auth.users
FOR EACH ROW EXECUTE FUNCTION handle_new_user();
```

**First admin setup**: After registering your first account, manually update your role in Supabase Table Editor: `role = 'admin'`.

---

## 3. Row Level Security

Enable on all tables first:
```sql
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE rooms    ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
```

### profiles policies
```sql
-- Read: any authenticated user
CREATE POLICY "profiles_select" ON profiles
FOR SELECT USING (auth.uid() IS NOT NULL);

-- Self-update display_name
CREATE POLICY "profiles_self_update" ON profiles
FOR UPDATE USING (auth.uid() = id)
WITH CHECK (auth.uid() = id);

-- Admin-only role update
CREATE POLICY "profiles_admin_role_update" ON profiles
FOR UPDATE USING (
  (SELECT role FROM profiles WHERE id = auth.uid()) = 'admin'
);
```

### rooms policies
```sql
-- Read: any authenticated user
CREATE POLICY "rooms_select" ON rooms
FOR SELECT USING (auth.uid() IS NOT NULL);

-- Insert: admin only
CREATE POLICY "rooms_admin_insert" ON rooms
FOR INSERT WITH CHECK (
  (SELECT role FROM profiles WHERE id = auth.uid()) = 'admin'
);

-- Delete: admin only
CREATE POLICY "rooms_admin_delete" ON rooms
FOR DELETE USING (
  (SELECT role FROM profiles WHERE id = auth.uid()) = 'admin'
);
```

### messages policies
```sql
-- Read: any authenticated user
CREATE POLICY "messages_select" ON messages
FOR SELECT USING (auth.uid() IS NOT NULL);

-- Insert: any authenticated user (their own messages only)
CREATE POLICY "messages_insert" ON messages
FOR INSERT WITH CHECK (auth.uid() = sender_id);

-- Delete: admin and moderator only
CREATE POLICY "messages_mod_delete" ON messages
FOR DELETE USING (
  (SELECT role FROM profiles WHERE id = auth.uid()) IN ('admin', 'moderator')
);
```

---

## 4. Realtime Configuration

In Supabase dashboard → Table Editor:
- **messages** table → Enable Realtime ✅
- **rooms** table → Enable Realtime ✅
- **profiles** table → Enable Realtime ✅ (for role change updates)

---

## 5. Supabase Client

```javascript
// src/lib/supabase.js
import { createClient } from '@supabase/supabase-js'

export const supabase = createClient(
  process.env.REACT_APP_SUPABASE_URL,
  process.env.REACT_APP_SUPABASE_ANON_KEY
)
```

---

## 6. Auth Operations

```javascript
// Register
const { data, error } = await supabase.auth.signUp({ email, password })

// Login
const { data, error } = await supabase.auth.signInWithPassword({ email, password })

// Logout
await supabase.auth.signOut()

// Get current user + profile
const { data: { user } } = await supabase.auth.getUser()
const { data: profile } = await supabase
  .from('profiles').select('*').eq('id', user.id).single()

// Auth state listener (use in AuthContext)
supabase.auth.onAuthStateChange((event, session) => {
  if (session) { /* fetch profile, set state */ }
  else { /* clear state, redirect to login */ }
})
```

---

## 7. Data Operations

### Rooms
```javascript
// Fetch all rooms
const { data: rooms } = await supabase
  .from('rooms').select('*').order('created_at', { ascending: true })

// Create room (admin — RLS enforces)
const { error } = await supabase
  .from('rooms').insert({ name: roomName, created_by: user.id })

// Delete room (admin — RLS enforces, cascades to messages)
const { error } = await supabase
  .from('rooms').delete().eq('id', roomId)
```

### Messages
```javascript
// Fetch history with sender profile joined
const { data: messages } = await supabase
  .from('messages')
  .select(`
    id, content, created_at, sender_id,
    profiles ( display_name, role )
  `)
  .eq('room_id', roomId)
  .order('created_at', { ascending: true })

// Send message
const { error } = await supabase
  .from('messages')
  .insert({ room_id: roomId, sender_id: user.id, content: text })

// Delete message (mod/admin — RLS enforces)
const { error } = await supabase
  .from('messages').delete().eq('id', messageId)
```

### Profiles
```javascript
// Fetch all users for sidebar list
const { data: users } = await supabase
  .from('profiles').select('id, display_name, role')

// Admin: update role
const { error } = await supabase
  .from('profiles').update({ role: newRole }).eq('id', targetUserId)
```

---

## 8. Realtime Subscription — THE Critical Piece

```javascript
// In your Chat component — inside useEffect
useEffect(() => {
  if (!selectedRoom) return

  // 1. Load history first
  fetchMessages(selectedRoom.id)

  // 2. Subscribe to live changes
  const channel = supabase
    .channel(`room:${selectedRoom.id}`)
    .on('postgres_changes', {
      event: 'INSERT',
      schema: 'public',
      table: 'messages',
      filter: `room_id=eq.${selectedRoom.id}`
    }, async (payload) => {
      // Fetch sender profile (not included in payload)
      const { data: profile } = await supabase
        .from('profiles')
        .select('display_name, role')
        .eq('id', payload.new.sender_id)
        .single()

      const newMsg = { ...payload.new, profiles: profile }
      setMessages(prev => [...prev, newMsg])
      // Trigger anime.js animation on the new element after render
    })
    .on('postgres_changes', {
      event: 'DELETE',
      schema: 'public',
      table: 'messages',
      filter: `room_id=eq.${selectedRoom.id}`
    }, (payload) => {
      setMessages(prev => prev.filter(m => m.id !== payload.old.id))
    })
    .subscribe()

  // 3. Cleanup — CRITICAL: without this, stale subscriptions stack up
  return () => supabase.removeChannel(channel)

}, [selectedRoom?.id])
```

---

## 9. Slash Command Parser

```javascript
// src/utils/commandParser.js
export const parseCommand = (input, currentUser, rooms) => {
  if (!input.trim().startsWith('/')) return null

  const parts = input.trim().split(' ')
  const cmd = parts[0].toLowerCase()
  const args = parts.slice(1)

  const COMMANDS = {
    '/help': {
      allowedRoles: ['admin', 'moderator', 'participant'],
      handler: () => ({
        type: 'system',
        content: 'Commands: /help · /rooms · /kick @user (mod+) · /promote @user (admin)'
      })
    },
    '/rooms': {
      allowedRoles: ['admin', 'moderator', 'participant'],
      handler: () => ({
        type: 'system',
        content: `Rooms: ${rooms.map(r => '#' + r.name).join(' · ')}`
      })
    },
    '/kick': {
      allowedRoles: ['admin', 'moderator'],
      handler: (args) => ({ type: 'kick', target: args[0] })
    },
    '/promote': {
      allowedRoles: ['admin'],
      handler: (args) => ({ type: 'promote', target: args[0] })
    }
  }

  const command = COMMANDS[cmd]

  if (!command) {
    return { type: 'error', content: `Unknown command "${cmd}". Type /help for a list.` }
  }

  if (!command.allowedRoles.includes(currentUser.role)) {
    return { type: 'error', content: "You don't have permission to use this command." }
  }

  return command.handler(args)
}
```

---

## 10. Error Handling

```javascript
// Standard pattern for all Supabase calls
const { data, error } = await supabase.from('table').operation()

if (error) {
  switch (error.code) {
    case '42501': toast.error("You don't have permission to do this."); break
    case '23505': toast.error("That name already exists."); break
    case 'PGRST116': toast.error("Not found."); break
    default:
      toast.error("Something went wrong. Try again.")
      console.error('[Supabase Error]', error)
  }
  return
}
// proceed with success
```

---

## 11. Security Checklist

Before submitting to judges, verify:
- [ ] RLS enabled on profiles, rooms, messages
- [ ] All 7 RLS policies created
- [ ] RLS policies tested: try insert as participant — should be blocked
- [ ] `.env` is in `.gitignore` — keys are NOT in GitHub
- [ ] Supabase anon key used in frontend (NOT the service_role key)
- [ ] No `select *` on tables — always specify columns
- [ ] Realtime enabled on messages, rooms, profiles tables
- [ ] Cascade delete working — delete room → messages disappear
