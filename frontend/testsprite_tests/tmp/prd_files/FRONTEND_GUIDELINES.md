# Frontend Guidelines
**Project**: NexusChat — Internal Communications Platform
**Version**: 2.0 | ACM ReCode 2026

---

## Design Philosophy

NexusChat is an **internal engineering tool**. The aesthetic must feel:
- Dark, focused, professional — like a tool engineers actually want to use
- Slack-inspired sidebar layout — judges recognise this pattern immediately
- Role hierarchy immediately visible — no guessing who has power
- Animated but not distracting — every animation serves a purpose

**Primary design references**: Search Dribbble for "dark internal chat dashboard" and "team messaging sidebar dark theme" before building. Screenshot 2-3 references. Design to that bar.

---

## 1. Colour System

Add these to `tailwind.config.js` under `theme.extend.colors` and to `src/styles/globals.css` as CSS variables:

```css
:root {
  /* Backgrounds */
  --bg-primary:      #0f0f10;   /* Darkest — app root background */
  --bg-secondary:    #1a1a1f;   /* Sidebar background */
  --bg-tertiary:     #25252d;   /* Cards, message area, modals */
  --bg-hover:        #2e2e38;   /* Hover states on interactive items */
  --bg-active:       #32324030; /* Active room — semi-transparent accent */

  /* Text */
  --text-primary:    #f0f0f5;   /* Main readable text */
  --text-secondary:  #9090a0;   /* Timestamps, labels, captions */
  --text-muted:      #606070;   /* Placeholder text */

  /* Brand Accent */
  --accent:          #7c6aff;   /* Purple — CTAs, active states, focus rings */
  --accent-hover:    #6a58ee;
  --accent-subtle:   #7c6aff20; /* Active room bg tint */

  /* Role Colours — must be immediately distinguishable at a glance */
  --role-admin:      #ff6b6b;   /* Red */
  --role-moderator:  #ffd166;   /* Amber */
  --role-participant:#78c2ad;   /* Teal */

  /* System Status */
  --online:          #43d08a;   /* Green — presence dot */
  --offline:         #606070;   /* Grey */
  --error:           #ff4f4f;
  --success:         #43d08a;
  --warning:         #ffd166;
  --info:            #7c6aff;

  /* Borders */
  --border:          #2a2a35;
  --border-strong:   #3a3a48;
}
```

---

## 2. Typography

```css
/* Import in index.html or globals.css */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

body { font-family: 'Inter', system-ui, sans-serif; }

/* Scale */
--text-xs:    12px;  /* Timestamps, role badge text */
--text-sm:    14px;  /* Secondary text, labels */
--text-base:  16px;  /* Messages, body text */
--text-lg:    18px;  /* Section headers */
--text-xl:    22px;  /* Page/panel titles */
```

---

## 3. Layout Structure

```
┌────────────────────────────────────────────────────────────────┐
│  HEADER                                                        │
│  ⬡ NexusChat                         Aaryan [ADMIN]  Logout   │
├───────────────────┬────────────────────────────────────────────┤
│                   │  CHAT HEADER                               │
│  SIDEBAR 260px    │  # engineering                             │
│  ─────────────    ├────────────────────────────────────────────┤
│  ROOMS            │                                            │
│  ─────────        │  MESSAGE AREA                              │
│  # general    ●   │  (Lenis smooth scroll container)           │
│  # engineering    │                                            │
│  # leadership     │  [AV] Aaryan [ADMIN]           9:34 PM    │
│                   │       Message here...               [🗑]   │
│  + New Room       │                                            │
│  (admin only)     │  [JV] Jamie  [PARTICIPANT]     9:35 PM    │
│                   │       Another message...                   │
│  ─────────────    │                                            │
│  ONLINE NOW       ├────────────────────────────────────────────┤
│  ● Aaryan  [A]    │  INPUT BAR                                 │
│  ● Morgan  [M]    │  [ Message #engineering... /help ]  [Send] │
│  ○ Jamie   [P]    │                                            │
└───────────────────┴────────────────────────────────────────────┘

[A] = red Admin badge  [M] = amber Mod badge  [P] = teal Participant badge
```

---

## 4. Component Specifications

### 4.1 — RoleBadge (shadcn `Badge` customised)
```jsx
// Variant map
const roleStyles = {
  admin:       'bg-red-950/50 text-red-400 border border-red-800/60',
  moderator:   'bg-amber-950/50 text-amber-400 border border-amber-800/60',
  participant: 'bg-teal-950/50 text-teal-400 border border-teal-800/60',
}

// Usage
<Badge className={`text-xs font-semibold uppercase tracking-wide px-2 py-0.5 ${roleStyles[role]}`}>
  {role}
</Badge>
```

---

### 4.2 — MessageBubble Component
```
Structure (flex row):
  Left:    Avatar (shadcn Avatar, 36px circle, user initials, bg coloured by role)
  Right:
    Row 1: DisplayName (semibold) + RoleBadge + Timestamp (muted, xs)
    Row 2: Message text (base size, primary colour)
    Row 3: Delete icon button (ONLY if canModerate — hidden by default, show on row hover)

Hover:   bg-hover on entire row
Delete:  text-error icon, tooltip "Delete message" (shadcn Tooltip)
```

**Get base structure from 21st.dev** — search "chat message bubble dark" — then customise colours to match tokens above.

---

### 4.3 — SystemMessage Component (Bot/Slash Command Output)
```
Structure (flex row, centered):
  Icon: 🤖 or ⚡ (18px)
  Text: "NexusBot" label (muted, xs, semibold) + message content (italic, secondary)
  No delete button
  No avatar
  Background: bg-tertiary/50, border-l-2 border-accent

Source: Adapt from uiverse.io — search "system message" or "info card"
```

---

### 4.4 — RoomItem (Sidebar)
```
Structure: flex row, padding 8px 16px
Left:  # symbol + room name (text-sm, text-primary)
Right: unread badge (P2 only)

States:
  Default:  transparent bg, text-secondary
  Hover:    bg-hover, text-primary
  Active:   bg-accent-subtle, text-primary, left border 3px var(--accent)

Get animation reference from uiverse.io — search "sidebar item active"
```

---

### 4.5 — OnlinePresenceDot
```
Source: uiverse.io — search "pulse dot" or "online indicator"

Online:  12px circle, bg-green, animated CSS pulse ring
Offline: 12px circle, bg-muted, no animation

// Embed next to user display name in sidebar user list
<span className="relative flex h-3 w-3">
  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
  <span className="relative inline-flex rounded-full h-3 w-3 bg-green-500"></span>
</span>
```

---

### 4.6 — MessageInput
```
Component: shadcn Input + shadcn Button in flex row

Input:
  Placeholder: "Message #room-name... (try /help for commands)"
  bg-tertiary, border-border, text-primary
  Focus: border-accent, subtle accent glow (box-shadow: 0 0 0 2px var(--accent)/20)
  On "/" detection: show command hint dropdown (P1 enhancement)

Send Button:
  shadcn Button, variant="default", bg-accent
  Keyboard: Enter = submit
  Validation fail: anime.js shake animation on input

Source for enhanced version: Browse 21st.dev for "chat input component dark"
```

---

### 4.7 — Modals (shadcn Dialog + AlertDialog)

**Create Room Modal** (shadcn `Dialog`):
```
Title: "Create New Room"
Body:  shadcn Input for room name, placeholder "e.g. design, backend, general"
Footer: Cancel (ghost Button) + Create (default Button, accent bg)
Animation: anime.js scaleY + opacity on open
```

**Delete Confirmation** (shadcn `AlertDialog`):
```
Title: "Delete [Room Name]?"
Body:  "This will permanently delete all messages in this room."
Footer: Cancel (ghost) + Delete (destructive red Button)
```

---

### 4.8 — Toast Notifications (shadcn Sonner)
```javascript
import { toast } from 'sonner'

// Usage patterns
toast.success("Room created successfully")
toast.success("Message deleted")
toast.error("You don't have permission to do this")
toast.error("Failed to connect. Retrying...")
toast.warning("Room will be permanently deleted")
toast.info("Jamie was promoted to Moderator")
```

Config: position `bottom-right`, duration 3500ms success / 5000ms error

---

## 5. Animations Reference (anime.js)

Import once in a utils file:
```javascript
// src/utils/animations.js
import anime from 'animejs'

export const animations = {
  messageAppear: (el) => anime({
    targets: el,
    opacity: [0, 1],
    translateY: [8, 0],
    duration: 250,
    easing: 'easeOutQuad'
  }),

  inputShake: (el) => anime({
    targets: el,
    translateX: [-5, 5, -3, 3, -1, 1, 0],
    duration: 380,
    easing: 'easeInOutSine'
  }),

  badgePulse: (el) => anime({
    targets: el,
    scale: [1, 1.12, 1],
    duration: 280,
    easing: 'easeOutElastic(1, 0.6)'
  }),

  modalOpen: (el) => anime({
    targets: el,
    opacity: [0, 1],
    scale: [0.97, 1],
    duration: 180,
    easing: 'easeOutQuad'
  }),

  sidebarRoomHighlight: (el) => anime({
    targets: el,
    backgroundColor: ['transparent', 'var(--accent-subtle)'],
    duration: 200,
    easing: 'easeOutQuad'
  })
}
```

**Rule**: Animations must be under 350ms. Anything longer feels sluggish during a live demo.

---

## 6. Smooth Scroll — Lenis Integration

```javascript
// Apply to message list container only — see TECH_STACK.md for full code
// Key rule: wrap ScrollArea content with Lenis wrapper ref

const messageContainerRef = useRef(null)
const lenis = useLenisScroll(messageContainerRef)

// On new message:
useEffect(() => {
  if (messages.length > 0 && lenis.current) {
    lenis.current.scrollTo(messageContainerRef.current?.scrollHeight, {
      duration: 0.5
    })
  }
}, [messages.length])
```

---

## 7. Spacing (Tailwind)

| Token | Value | Usage |
|---|---|---|
| `p-1` / `gap-1` | 4px | Tight internal padding |
| `p-2` / `gap-2` | 8px | Component internal spacing |
| `p-4` / `gap-4` | 16px | Standard section padding |
| `p-6` / `gap-6` | 24px | Generous section spacing |
| `p-8` / `gap-8` | 32px | Page-level padding |

---

## 8. Interaction States

| Element | Default | Hover | Active/Focus | Disabled |
|---|---|---|---|---|
| Primary Button | accent bg | accent-hover | scale-95 | opacity-40, cursor-not-allowed |
| Danger Button | error bg | error/80 | scale-95 | opacity-40 |
| Ghost Button | transparent | bg-hover | bg-active | opacity-40 |
| Room sidebar item | transparent | bg-hover | accent-subtle + left border | — |
| Input | border-border | border-strong | border-accent + glow | opacity-40 |
| Delete icon | hidden | visible (on row hover) | text-error | — |
| Avatar | solid role colour | slight brightness increase | — | — |

---

## 9. Responsive Behaviour

- Desktop-first (judges view on laptop)
- Breakpoint: `md` (768px) — sidebar collapses to icons only
- Below 768px: hamburger opens sidebar as overlay
- Message area: always full-width of available space

---

## 10. Accessibility Minimums
- All buttons have `aria-label` if icon-only
- All form inputs have associated `label` elements
- Focus ring visible on all focusable elements (`outline: 2px solid var(--accent)`)
- Colour is never the only indicator — always paired with text or icon
- Contrast ratio: minimum 4.5:1 for all body text

---

## 11. Quick Component Source Guide

| Component Need | Where to Get It |
|---|---|
| Polished base components (Button, Input, Dialog, Badge) | https://ui.shadcn.com/ |
| Animated CSS elements (pulse dot, loader, alerts) | https://uiverse.io/ |
| Complex React components (message bubble, sidebar item) | https://21st.dev/home |
| Dark chat app visual reference | https://dribbble.com/ — "dark chat UI" |
| Smooth scroll on message feed | Lenis — https://lenis.darkroom.engineering/ |
| All micro-animations | anime.js — https://animejs.com/ |
