# Tech Stack Documentation
**Project**: NexusChat — Internal Communications Platform
**Version**: 2.0 | ACM ReCode 2026

---

## Full Stack Map

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND                                  │
│                                                                  │
│  React  ──  Tailwind CSS  ──  shadcn/ui  ──  anime.js  ──  Lenis │
│                                                                  │
│  UI Sources: uiverse.io · 21st.dev · 1Code · Dribbble           │
├─────────────────────────────────────────────────────────────────┤
│                        BACKEND (Supabase)                        │
│                                                                  │
│  Auth  ──  PostgreSQL  ──  Row Level Security  ──  Realtime     │
├─────────────────────────────────────────────────────────────────┤
│                        DEPLOYMENT                                │
│                                                                  │
│  GitHub  ──  Netlify (auto-deploy on push)                      │
└─────────────────────────────────────────────────────────────────┘
```

---

## 1. Core Framework

### React
- Version: 18+
- Routing: React Router v6
- State: `useState` + `useEffect` + `useContext` (no Redux — overkill for this scale)
- Pattern: Component-per-feature structure

### Tailwind CSS
- Utility-first styling
- Dark theme by default (configured in `tailwind.config.js`)
- Custom colour tokens from FRONTEND_GUIDELINES.md added to config

---

## 2. UI Component Library — shadcn/ui
**Source**: https://ui.shadcn.com/

shadcn/ui is your primary component system. Components are copied into your codebase (not installed as a black-box dependency), making them fully customisable to the dark theme.

### Components Used in NexusChat

| Component | Where Used | Install Command |
|---|---|---|
| `Button` | Send message, create room, login, all CTAs | `npx shadcn-ui@latest add button` |
| `Input` | Message input, room name, auth forms | `npx shadcn-ui@latest add input` |
| `Badge` | Role badges (Admin/Mod/Participant) | `npx shadcn-ui@latest add badge` |
| `Dialog` | Create room modal | `npx shadcn-ui@latest add dialog` |
| `AlertDialog` | Delete room/message confirmations | `npx shadcn-ui@latest add alert-dialog` |
| `DropdownMenu` | Role assignment dropdown (admin) | `npx shadcn-ui@latest add dropdown-menu` |
| `ScrollArea` | Message feed container | `npx shadcn-ui@latest add scroll-area` |
| `Tooltip` | Hover labels on icon buttons | `npx shadcn-ui@latest add tooltip` |
| `Separator` | Sidebar section dividers | `npx shadcn-ui@latest add separator` |
| `Avatar` | User initials circle | `npx shadcn-ui@latest add avatar` |
| `Toast` (Sonner) | All notification toasts | `npx shadcn-ui@latest add sonner` |

### Customising for Dark Theme
After installing each component, open its file in `src/components/ui/` and ensure it inherits from your CSS variables defined in `globals.css`. Do not hardcode colours in components.

---

## 3. UI Elements Library — uiverse.io
**Source**: https://uiverse.io/

uiverse.io provides open-source, copy-paste CSS and Tailwind elements. No npm install — just copy the HTML/CSS.

### Elements to Use in NexusChat

| Element Type | Where Used | What to Search on uiverse.io |
|---|---|---|
| Animated online dot | User list presence indicator | Search: "pulse dot" or "online indicator" |
| Send button | Message input send button | Search: "send button" or "animated button" |
| Loading skeleton | Room/message loading state | Search: "skeleton loader" |
| Alert/banner | Reconnecting notification | Search: "alert banner" or "notification" |
| Empty state card | No rooms / no messages state | Search: "empty state" |
| Typing indicator | "Jamie is typing..." (P2) | Search: "typing indicator" or "dot loader" |

**Workflow**: Browse uiverse.io → find element → click "Get Code" → choose Tailwind or CSS → paste into your component file.

---

## 4. AI Component Generator — 21st.dev + 1Code
**Source**: https://21st.dev/home | https://github.com/21st-dev/1Code

21st.dev is a React component library + AI generator. 1Code is their AI agent that generates components from a text description.

### When to Use in NexusChat

Use 21st.dev when you need a complex component fast and don't want to build it from scratch:

- **Message bubble component** — describe it, get the code
- **Sidebar room list item** — describe active/inactive states
- **User list with avatars and badges** — describe the visual
- **Admin panel layout** — describe the manage users section

**Workflow with 1Code**:
1. Go to https://21st.dev/home
2. Describe your component in natural language
3. Get React + Tailwind code
4. Paste into your project
5. Adjust colours to match FRONTEND_GUIDELINES.md colour tokens

---

## 5. Smooth Scroll — Lenis
**Source**: https://lenis.darkroom.engineering/ | https://github.com/darkroomengineering/lenis

Lenis is a lightweight smooth scroll library by Darkroom Engineering. Adds buttery inertia-based scrolling.

### Install
```bash
npm install @studio-freight/lenis
```

### Usage in NexusChat — Message Feed Only
```javascript
// src/hooks/useLenis.js
import { useEffect, useRef } from 'react'
import Lenis from '@studio-freight/lenis'

export const useLenisScroll = (containerRef) => {
  const lenisRef = useRef(null)

  useEffect(() => {
    if (!containerRef.current) return

    const lenis = new Lenis({
      wrapper: containerRef.current,
      content: containerRef.current,
      duration: 0.8,
      easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
      smoothWheel: true,
    })

    lenisRef.current = lenis

    function raf(time) {
      lenis.raf(time)
      requestAnimationFrame(raf)
    }
    requestAnimationFrame(raf)

    return () => lenis.destroy()
  }, [containerRef])

  return lenisRef
}

// To scroll to bottom on new message:
lenisRef.current?.scrollTo(containerRef.current?.scrollHeight, { duration: 0.6 })
```

**Important**: Apply Lenis ONLY to the message list container. Do not apply to the full page or it will interfere with React Router navigation.

---

## 6. Animations — anime.js
**Source**: https://animejs.com/

Anime.js is a lightweight (17kb) JavaScript animation library. Handles complex animations with a clean API.

### Install
```bash
npm install animejs
```

### Animations in NexusChat

```javascript
import anime from 'animejs'

// New message appears
export const animateNewMessage = (element) => {
  anime({
    targets: element,
    opacity: [0, 1],
    translateY: [8, 0],
    duration: 250,
    easing: 'easeOutQuad'
  })
}

// Empty input shake (validation feedback)
export const animateInputShake = (element) => {
  anime({
    targets: element,
    translateX: [-6, 6, -4, 4, -2, 2, 0],
    duration: 400,
    easing: 'easeInOutSine'
  })
}

// Role badge update pulse
export const animateBadgePulse = (element) => {
  anime({
    targets: element,
    scale: [1, 1.15, 1],
    duration: 300,
    easing: 'easeOutElastic(1, 0.5)'
  })
}

// Modal open
export const animateModalOpen = (element) => {
  anime({
    targets: element,
    opacity: [0, 1],
    scaleY: [0.96, 1],
    duration: 200,
    easing: 'easeOutQuad'
  })
}
```

---

## 7. Design Inspiration — Dribbble
**Source**: https://dribbble.com/

Use Dribbble for visual reference only — not for code. Before building any component, search Dribbble for reference.

### Search Terms for NexusChat
- "dark chat app UI"
- "internal messaging dashboard dark"
- "Slack dark theme redesign"
- "team chat sidebar design"
- "role badge UI component"

**How to use**: Screenshot 2-3 references. Share with your Canva designer teammate so slides match the app aesthetic. Reference them while styling components.

---

## 8. Backend — Supabase (Your Entire Backend)

| Supabase Feature | Used For |
|---|---|
| Auth | User registration, login, session management |
| PostgreSQL | profiles, rooms, messages tables |
| Row Level Security | Role-based permission enforcement at DB level |
| Realtime | Live message delivery, room updates |
| Auto-generated REST API | All CRUD operations via supabase-js client |

**No custom backend server. No Node.js. No Express. Supabase handles everything.**

### Why NOT Firebase
Firebase is in your toolkit but is redundant here. Supabase provides:
- Auth ✅
- Database ✅
- Real-time ✅
- RLS (permissions) ✅ — Firebase does not have this natively

Using both creates duplicate infrastructure and credential management complexity. **Supabase only for NexusChat.**

---

## 9. Deployment — Netlify

### Setup (Do this BEFORE 9 PM tonight)
1. Push project to GitHub
2. Go to netlify.com → New site from Git → Connect GitHub repo
3. Build command: `npm run build`
4. Publish directory: `build`
5. Add environment variables in Netlify dashboard:
   - `REACT_APP_SUPABASE_URL`
   - `REACT_APP_SUPABASE_ANON_KEY`
6. Click Deploy — get live URL immediately

### Auto-Deploy
Every `git push` to main triggers a new Netlify build. Commit often.

---

## 10. Full Package List

```bash
# Core
npm install @supabase/supabase-js react-router-dom

# shadcn/ui setup
npx create-next-app@latest --typescript --tailwind --eslint
# OR for Create React App:
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p

# shadcn CLI
npx shadcn-ui@latest init

# Animations & Scroll
npm install animejs @studio-freight/lenis

# Notifications (shadcn Sonner toast)
npm install sonner

# Date formatting
npm install date-fns
```

---

## 11. skills.sh

**Note**: skills.sh (https://skills.sh/) is a developer skill assessment platform. It is not applicable to this build. No integration needed for NexusChat.

---

## 12. Constraints & Limits

| Service | Limit | Impact on Demo |
|---|---|---|
| Supabase DB | 500MB | None |
| Supabase Realtime | 200 connections | None |
| Supabase Auth | Unlimited users | None |
| Netlify bandwidth | 100GB/month | None |
| anime.js bundle size | ~17KB | Negligible |
| Lenis bundle size | ~4KB | Negligible |
