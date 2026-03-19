# NexusChat SPEC.md — Canonical Specification

> **Status: FINALIZED**
> **Project**: NexusChat
> **Backend**: Supabase-only (Auth, PostgreSQL, Realtime, RLS)
> **Frontend**: React, Tailwind CSS, shadcn/ui, anime.js, Lenis

## 1. Core Feature Set (P0/P1)
- **Authentication**: Email/Password via Supabase Auth.
- **Role Hierarchy**: Admin, Moderator, Participant (Badges).
- **Real-Time Messaging**: Sub-500ms delivery via Supabase Realtime Channels.
- **Room Management**: Dynamic creation/deletion of channels.
- **Direct Messaging (DM)**: Private 1-on-1 chats.
- **Invite-Only Channels**: Restricted access rooms.
- **Slash Commands**: `/help`, `/rooms`, `/kick`, `/promote`, `/demote`, `/invite`.

## 2. Security & Robustness (Ralph Loop Extension)
- **RLS (Row Level Security)**: MANDATORY at the database level for all tables (`profiles`, `rooms`, `messages`, `room_members`).
- **Rate Limiting**: IP + User based on all public endpoints.
- **Input Validation**: DB-level `CHECK` constraints and frontend type-safety.
- **Secure Handling**: Environment variables for all keys; no hardcoding.

## 3. UI/UX Excellence
- **Scroll**: Lenis (MANDATORY).
- **Animations**: anime.js for all transitions (MANDATORY).
- **Components**: shadcn/ui + 21st.dev components + uiverse.io micro-interactions.

## 4. Verification Requirements
- Real-time flow verified across 2+ browser tabs.
- RLS policies verified via Supabase SQL Editor/Tests.
- Role-based UI visibility verified per persona.

---
*Authorized by Aaryan Raorane — %DATE%*
