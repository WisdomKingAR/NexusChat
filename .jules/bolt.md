# Bolt's Performance Journal

## 2025-05-14 - Chat UI Re-render Bottleneck
**Learning:** In React chat applications, parent state updates (like message input field changes) trigger a full re-render of the entire message list if not memoized. With large chat histories, this leads to input lag and high CPU usage.
**Action:** Always extract message items into memoized components (`React.memo`) and memoize the rendered list (`useMemo`) to decouple message list rendering from input state updates.

## 2025-05-14 - MongoDB Compound Indexing for Chat
**Learning:** Fetching messages for a specific room sorted by time is a high-frequency query that benefits significantly from a compound index on `(room_id, created_at)`.
**Action:** Ensure compound indexes are created for common "filter + sort" query patterns to avoid in-memory sorting.
