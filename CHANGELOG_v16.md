# GymFlow Pro v16 — QR Attendance Foundation

## Implemented
- New members receive `app_access_enabled = true` by default.
- Staff can issue/rotate an opaque entry QR credential from the member profile. Only the SHA-256 hash is stored; the raw token is returned once. Reissuing invalidates the previous token.
- Attendance check-in accepts either a scanned `qr_token` or manual `member_id` fallback.
- Backend validates gym membership, active subscription dates, and payment state before recording a visit.
- Attendance stores its source (`qr` or `manual`) and the subscription used at check-in.
- Duplicate scans within 90 seconds are rejected.
- Guest registration is a separate post-check-in endpoint, so a guest registration error does not undo a successful member visit.
- Attendance UI now supports QR-token scanner input or manual lookup, and asks about guests only after check-in succeeds.
- The initial visit flow no longer requires check-out. Legacy check-out API remains for compatibility.
- Disabling Member App access clears the current QR credential hash.

## Database migration required
Apply `backend/gym-saas-backend/migrations_v16_attendance_member_qr.sql` to the existing PostgreSQL database after taking a backup. Do not deploy the code before the migration is applied.

## Not included yet
- SMS OTP provider integration and member session authentication. This requires selecting/configuring an SMS provider and coordinating the activation API with the Flutter developer.
- Member-authenticated self-service endpoint to retrieve/rotate the entry QR. The current QR issuance endpoint is staff/admin-authenticated; the future OTP/session flow should securely expose the member's own QR.
- Camera scanning UI in the web staff page. The attendance input supports QR scanners that type the decoded token; Flutter/camera scanning can send the same decoded token to the check-in API.
- Full automated integration tests against a configured PostgreSQL database and frontend production build. Frontend dependency installation timed out in this environment; `vite` was unavailable for build verification.
