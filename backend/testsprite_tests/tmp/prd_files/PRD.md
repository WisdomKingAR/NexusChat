# Product Requirements Document (PRD)
**Project**: NexusChat — Internal Communications Platform
**Version**: 2.0 | ACM ReCode 2026 — Full Stack Track
**Last Updated**: 14 March 2026
**Owner**: Aaryan Raorane
**Deadline**: 15 March 2026, 12:00 PM IST

---

## 1. Problem Statement

Distributed engineering organizations depend on third-party platforms (Slack, Discord, Teams) for internal communication — platforms they don't control. The result: sensitive conversations on external servers, rigid permission models, no custom commands, and zero extensibility.

NexusChat is a lightweight, self-hosted internal messaging platform where roles, rooms, real-time communication, and system commands are fully owned by the organization. It looks and feels premium. It behaves with strict hierarchy.

---

## 2. Goals & Objectives

### Business Goals
- Deliver a working, visually impressive full-stack platform within 15 hours
- Demonstrate role-based access control that genuinely restricts behaviour — not just hides UI
- Deploy a live URL accessible by judges before 12:00 PM IST, March 15

### User Goals
- Exchange messages in real-time without page refresh
- Know instantly what role you and others hold
- Admins exercise full control; participants are meaningfully restricted

---

## 3. Success Metrics
- Messages appear across two open browser tabs in under 500ms
- Role restrictions enforced at DB level (Supabase RLS), not just frontend
- Minimum 3 rooms operational simultaneously
- Minimum 2 slash commands functional
- Smooth scroll experience on message feed (Lenis)
- Animations on message appearance (anime.js) — not jarring, subtle
- Live Netlify deployment URL functional at submission time

---

## 4. Target Users & Personas

### Primary Persona: Alex (Admin)
- **Role**: System Administrator
- **Pain Points**: Cannot revoke permissions quickly; no audit trail on sensitive rooms
- **Goals**: Create rooms, assign roles, delete messages, run system commands
- **Technical Proficiency**: High

### Secondary Persona: Morgan (Moderator)
- **Role**: Team Lead
- **Goals**: Delete messages in their room, manage room membership, use mod-level commands
- **Technical Proficiency**: Medium

### Tertiary Persona: Jamie (Participant)
- **Role**: Engineer
- **Goals**: Join rooms, send and receive messages instantly
- **Technical Proficiency**: Medium

---

## 5. Features & Requirements

### P0 — Must Have (Demo Survival)

**1. User Authentication**
- User Story: As a user, I want to log in so my identity is verified before I access any room
- Acceptance Criteria:
  - [ ] Register with email + password
  - [ ] Login and receive a persistent session
  - [ ] Unauthenticated users blocked from all routes
  - [ ] Session survives page refresh

**2. Role System (Admin / Moderator / Participant)**
- User Story: As an admin, I want to assign roles so that not everyone has equal power
- Acceptance Criteria:
  - [ ] Three roles: admin, moderator, participant
  - [ ] Admin can promote/demote users
  - [ ] Moderator cannot access admin controls
  - [ ] Participant cannot delete messages or manage rooms
  - [ ] Role displayed as a colour-coded badge (shadcn/ui Badge component)

**3. Room Management**
- User Story: As an admin, I want to create rooms so teams have dedicated channels
- Acceptance Criteria:
  - [ ] Admin creates rooms via shadcn Dialog modal
  - [ ] Admin deletes rooms with confirmation modal
  - [ ] All users see new rooms appear in sidebar in real-time
  - [ ] Rooms persist after refresh

**4. Real-Time Messaging**
- User Story: As a participant, I want messages to appear instantly
- Acceptance Criteria:
  - [ ] Message in Tab A appears in Tab B in under 500ms
  - [ ] Message history loads on room join
  - [ ] Messages show sender name, role badge, timestamp
  - [ ] Message appears with anime.js fade-in animation
  - [ ] No page refresh required

**5. Smooth Scroll Experience**
- User Story: As a user, I want the message feed to scroll smoothly
- Acceptance Criteria:
  - [ ] Lenis applied to message feed scroll container
  - [ ] Auto-scrolls to bottom on new message with smooth motion
  - [ ] Does not interfere with page navigation

**6. Live Deployment**
- Acceptance Criteria:
  - [ ] Netlify URL accessible without local setup
  - [ ] No console errors in production build

### P1 — Should Have (Score Boosters)

**7. Slash Commands (Extended)**
- `/help` — lists commands (everyone)
- `/rooms` — lists all rooms (everyone)
- `/kick @user` — removes user from room (mod+)
- `/promote @user` — promotes to moderator (admin only)
- `/demote @user` — demotes to participant (admin only)
- `/invite @user` — invites to private room (admin/room owner)
- Commands display as styled bot messages using uiverse.io system message style

**8. Message Deletion by Role**
- Delete icon visible on hover — admin and moderator only
- Deletion reflects instantly across all connected clients

**9. Online Presence Indicator**
- Green animated dot (uiverse.io CSS pulse animation) next to active users
- Disappears within 30 seconds of user going offline

**10. Personal Direct Messages (DMs)**
- User Story: As a user, I want to message individuals privately
- Acceptance Criteria:
  - [ ] 1-on-1 private chat interface
  - [ ] Real-time updates for both participants
  - [ ] Persistent history

**11. Invite-Only Channels**
- User Story: As an admin, I want private rooms for specific members
- Acceptance Criteria:
  - [ ] Room visibility restricted to invited members
  - [ ] Admin/Owner can manage invitations

### P2 — Nice to Have (Only if time allows)
- Message reactions (emoji)
- Typing indicator ("Jamie is typing...")
- Room search/filter

---

## 6. Explicitly OUT OF SCOPE
- Video or voice calling
- File uploads or media sharing
- Email notifications
- Mobile app (web only, desktop-first)
- End-to-end encryption
- Message threading/replies
- Third-party OAuth (Google, GitHub)
- Push notifications
- skills.sh integration (not relevant to this build)

---

## 7. User Scenarios

### Scenario 1: Admin sets up the system
1. Admin registers → assigned admin role automatically (first user = admin logic or manual Supabase assignment)
2. Admin creates 3 rooms: General, Engineering, Leadership (via shadcn Dialog)
3. Rooms appear in sidebar for all connected users instantly

### Scenario 2: Real-time message exchange
1. User A types message → presses Enter
2. User B sees it appear with anime.js fade-in — no refresh
3. Moderator hovers message → delete icon appears → clicks → message disappears for both users
4. Message feed scrolls smoothly via Lenis

### Scenario 3: Role restriction demo (Judge moment)
1. Two tabs open — Tab A: Admin, Tab B: Participant
2. Participant has no delete button, no admin panel
3. Admin promotes participant to moderator via Manage Users panel
4. Moderator tab updates — delete button now visible — without page refresh

---

## 8. Non-Functional Requirements
- **Performance**: Messages < 500ms; page load < 2s; Lenis scroll at 60fps
- **Security**: Supabase RLS enforces all permissions server-side
- **Accessibility**: WCAG 2.1 AA — keyboard nav, visible focus, 4.5:1 contrast
- **Scalability**: 3 simultaneous rooms, 10 concurrent users for demo purposes

---

## 9. Dependencies & Constraints
- Supabase free tier (500MB DB, 200 realtime connections)
- Netlify free tier (100GB bandwidth)
- 15 hours build time
- Team: Aaryan (dev), Researcher/Support, Designer (Canva)

---

## 10. Timeline
- **MVP (Round 1)**: March 15, 2026, 12:00 PM — all P0 live and deployed
- **V1 (Round 2)**: April 3, 2026 — P1 complete, UI polished, performance optimised

---

## 11. Ralph Loop Extension (Robustness & Security)

### 11.1 Security Hardening Protocol
- **Rate Limiting**: Implementation of IP + User based rate limiting on all public endpoints (Supabase built-in or Edge Functions for auth attempts).
- **Input Validation**: Strict schema-based validation & sanitization on all user inputs (Database `CHECK` constraints, Trigges, and Frontend Type checking).
- **Secure Key Handling**: Zero hard-coded keys; all Supabase keys must be in environment variables (`.env`, Netlify Envs).
- **OWASP Alignment**: Following Best Practices for Broken Access Control (RLS), Injection (Prepared Statements), and Security Misconfiguration.

### 11.2 Premium UI/UX Enforcement (Antigravity Standard)
- **Library Compliance**:
  - `Lenis`: MANDATORY for all scroll containers.
  - `21st.dev`: MANDATORY for complex UI components (MessageBubbles, Sidebars).
  - `uiverse.io`: MANDATORY for micro-interactions (Pulse dots, styled system messages).
  - `animejs`: MANDATORY for all entry/exit animations and state transitions.
  - `shadcn/ui`: MANDATORY core design system.
- **Micro-animations**: Every state change (room switch, message send, role update) must have a subtle animation.

### 11.3 Edge Case Matrix (The "I'm in danger" Check)
| Scenario | Impact | Mitigation |
|---|---|---|
| Latency Spike | Jarring UI | Optimistic UI updates + Loading skeletons |
| Connection Loss | Lost messages | Offline persistence check + Reconnection toasts |
| Malicious Injection | SQL/XSS | Database-level sanitization & React safe rendering |
| Role Escalation Attempt | Data breach | Strict RLS (Row Level Security) on all tables |
