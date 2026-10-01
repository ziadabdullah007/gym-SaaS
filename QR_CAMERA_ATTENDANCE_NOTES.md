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
