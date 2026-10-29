
ALTER TABLE message ADD COLUMN emote_ids TEXT NOT NULL DEFAULT '{}' CHECK (json_valid(emote_ids));