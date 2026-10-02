-- GymFlow v17: member app password and one-time reset code support
ALTER TABLE members ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255);
ALTER TABLE members ADD COLUMN IF NOT EXISTS password_reset_code_hash VARCHAR(255);
ALTER TABLE members ADD COLUMN IF NOT EXISTS password_reset_expires_at TIMESTAMPTZ;
