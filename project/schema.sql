DROP TABLE IF EXISTS nodes;

-- 1. Create the Table
CREATE TABLE nodes (
    id INTEGER PRIMARY KEY,
    text TEXT NOT NULL,
    is_question INTEGER NOT NULL,
    yes_id INTEGER,
    no_id INTEGER,
    FOREIGN KEY (yes_id) REFERENCES nodes(id),
    FOREIGN KEY (no_id) REFERENCES nodes(id)
);

-- 2. Insert LAYER 4 (The Answers) FIRST
-- These have no dependencies (yes_id/no_id are NULL), so they are safe to create first.
INSERT INTO nodes (id, text, is_question, yes_id, no_id) VALUES
(8, 'Counter-Strike 2', 0, NULL, NULL),
(9, 'Call of Duty: Warzone', 0, NULL, NULL),
(10, 'League of Legends', 0, NULL, NULL),
(11, 'Rocket League', 0, NULL, NULL),
(12, 'Elden Ring', 0, NULL, NULL),
(13, 'Cyberpunk 2077', 0, NULL, NULL),
(14, 'Resident Evil 4 Remake', 0, NULL, NULL),
(15, 'Stardew Valley', 0, NULL, NULL);

-- 3. Insert LAYER 3 (Specific Vibes)
-- Now we can point to IDs 8-15 because they exist.
INSERT INTO nodes (id, text, is_question, yes_id, no_id) VALUES
(4, 'Is it a tactical shooter (slow-paced, high stakes)?', 1, 8, 9),
(5, 'Is it a MOBA (like League of Legends)?', 1, 10, 11),
(6, 'Is it set in a High Fantasy world (swords, magic)?', 1, 12, 13),
(7, 'Is it a Horror or Survival game?', 1, 14, 15);

-- 4. Insert LAYER 2 (Genre Splits)
-- Now we can point to IDs 4-7.
INSERT INTO nodes (id, text, is_question, yes_id, no_id) VALUES
(2, 'Is it a First-Person Shooter (FPS)?', 1, 4, 5),
(3, 'Is it an RPG (Role-Playing Game)?', 1, 6, 7);

-- 5. Insert LAYER 1 (The Root) LAST
-- Now we can point to IDs 2 and 3.
INSERT INTO nodes (id, text, is_question, yes_id, no_id) VALUES
(1, 'Is it primarily a Multiplayer / Online game?', 1, 2, 3);
