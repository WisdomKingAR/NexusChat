# NexusChat ROADMAP.md — Waves of Work

## Wave 1: Foundation (Supabase & Auth)
- [ ] Connect Supabase Project URL + Key.
- [ ] Implement/Verify `AuthContext.jsx` with Supabase Auth.
- [ ] Setup `profiles` table and `handle_new_user` trigger.
- [ ] Define and apply RLS policies for `profiles`.

## Wave 2: Real-time Communication
- [ ] Setup `rooms` and `messages` tables.
- [ ] Implement Real-time message subscription in `ChatPanel.jsx`.
- [ ] Enable optimistic UI updates for message sending.

## Wave 3: Feature Restoration (Critical)
- [ ] Restore Direct Messaging (DM) flow and `DmChatPanel.jsx`.
- [ ] Implement Invite-Only room logic and `room_members` table.
- [ ] Verification: Test DM flow between test users.

## Wave 4: Role Management & Commands
- [ ] Implement `/help`, `/rooms`, `/kick`, `/promote`, `/demote`.
- [ ] Integrate Role badges in messages and sidebar.
- [ ] Restrict UI elements based on `isAdmin` / `isMod` / `canModerate` flags.

## Wave 5: Premium Polish & Verification
- [ ] Integrate Lenis and anime.js across the app.
- [ ] Apply uiverse.io micro-interactions.
- [ ] Conduct final Ralph Loop Security Audit (Rate limiting, sanitization).
- [ ] End-to-End browser verification (2 tabs).
