-- GymAURA v18: global member-app username
-- Legacy members may keep username NULL until an admin/staff sets it from View Member.
ALTER TABLE members ADD COLUMN IF NOT EXISTS username VARCHAR(50);

CREATE UNIQUE INDEX IF NOT EXISTS uq_members_username
ON members (LOWER(username))
WHERE username IS NOT NULL;
