# GymFlow Pro — Mobile App / Attendance API Contract (v16 draft)

This contract documents the implemented backend pieces in this package and the planned member activation integration. All paths are relative to the GymFlow API base URL.

## Member app access

- Newly created members receive `app_access_enabled: true` by default.
- Staff can disable access through the member update API by setting `app_access_enabled: false`. Disabling access clears the stored QR credential hash.
- Member activation by mobile number + OTP is **not implemented in this package yet**. It requires the agreed SMS delivery provider/configuration and member-session flow. Do not build a separate Flutter database/auth system; coordinate the contract before connecting activation.

## Entry QR credential

### Issue or rotate a QR credential (staff/admin session)
`POST /api/v1/members/{member_id}/entry-qr`

Response:
```json
{
  "member_id": "<uuid>",
  "qr_token": "<opaque-random-token>",
  "message": "..."
}
```

The token is returned only at issue time. Store it securely and encode the token string as the QR contents. Issuing a replacement invalidates the previous token. The token is not a member ID and contains no personal information.

The eventual member self-service endpoint should expose the current credential only after OTP-authenticated member session validation. That endpoint is pending until member OTP/session auth is implemented.

## Staff attendance

### Check in by QR
`POST /api/v1/attendance/check-in`
```json
{ "qr_token": "<scanned-token>" }
```

### Manual fallback check-in
`POST /api/v1/attendance/check-in`
```json
{ "member_id": "<member-uuid>" }
```

Exactly one of `qr_token` or `member_id` is required. The backend derives the gym from the authenticated staff account, validates member/subscription/payment eligibility, records a visit, and rejects repeated scans within 90 seconds. The backend does not require check-out for the initial visit-based flow.

### Register guests after a successful check-in
`POST /api/v1/attendance/{attendance_id}/guests`
```json
{
  "guests": [
    { "name": "Guest Name", "phone": "01000000000", "age": 25, "weight": 70 }
  ]
}
```

The backend verifies the attendance belongs to the staff member's gym, checks invitation allowance, and increments invitation usage per guest visit. Guest registration is a separate operation: a guest-save failure does not roll back the member's already-recorded visit.

## Important behavior

- Attendance `source` is `qr` or `manual`.
- Each attendance row stores the subscription used at check-in where available.
- Subscription/payment eligibility remains backend-enforced. Outstanding balance during the allowed grace period is permitted; overdue balance blocks entry according to the existing subscription state.
- The legacy check-out endpoint remains for compatibility with historical records, but the initial member visit workflow does not require check-out.
- The mobile app must use backend APIs and must never connect directly to Supabase/PostgreSQL or authorize access using a client-supplied member ID.
