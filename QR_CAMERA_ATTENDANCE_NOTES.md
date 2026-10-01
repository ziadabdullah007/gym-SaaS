# QR Camera Attendance — v16 update

## Web attendance
- Open Camera starts the browser camera scanner (rear-facing camera preferred on mobile/tablet).
- A decoded QR credential is sent to `POST /api/v1/attendance/check-in` as `qr_token`.
- Successful check-in follows the existing guest-registration prompt and attendance refresh.
- Manual member check-in and USB scanners that type token contents remain available.
- Camera access requires browser permission and a secure context (HTTPS or localhost). Camera availability depends on the device/browser.

## Member QR
- Staff issues/rotates the opaque credential from the member profile.
- The one-time returned token is rendered as a QR image, can be copied, and can be downloaded as SVG.
- Flutter can later render the same credential returned through a properly authenticated member-self endpoint. OTP is not implemented in this web update.

## Install
Run `npm install` in `frontend` then `npm run build`. Dependencies include `html5-qrcode` and `qrcode.react`.


### Rotating QR (60-second lifetime)
The authenticated staff web profile requests `POST /api/v1/members/{member_id}/entry-qr` automatically on page open and every 60 seconds. The backend returns a signed token with `expires_in: 60`; attendance check-in validates signature, gym scope, and expiry. Flutter should request a fresh token through a member-authenticated self endpoint when that authentication flow is implemented; do not persist or share QR screenshots. OTP remains out of scope.
