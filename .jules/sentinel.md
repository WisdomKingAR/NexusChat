## 2025-05-15 - Information Disclosure via User List
**Vulnerability:** The `/api/users` endpoint was returning full user objects, including sensitive email addresses, to any authenticated user.
**Learning:** Over-reliance on a single Pydantic model (`UserProfile`) for both private and public data. FastAPI's `response_model` only filters what's in the model, so if the model includes sensitive fields, they will be leaked if they are present in the returned data.
**Prevention:** Always use separate models for public data (e.g., `UserPublicProfile`) and ensure that the controller logic also only retrieves or constructs the necessary fields. Use model inheritance to keep models DRY while maintaining strict data separation.
