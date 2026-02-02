# Steam Library Akinator
#### Video Demo:  https://youtu.be/IERDHeNDAj0

#### Description:
The Steam Library Akinator is a web-based implementation of the classic "20 Questions" game, specifically tailored for video games. It utilizes a dynamically growing Binary Decision Tree to guess which video game the user is thinking of. Unlike a static trivia game, this application uses "Online Supervised Learning"—if the AI fails to guess the correct game, it asks the user to teach it. The user inputs the correct game title and provides a new distinguishing question, which permanently expands the database's decision tree, making the AI smarter for every subsequent player.

This project was built using Python (Flask), SQLite, and the RAWG.io Video Game API. It features a responsive UI with Bootstrap, real-time game validation to prevent database pollution, and visual enhancements like fetching game box art dynamically.

### Key Features
* **Dynamic Learning Engine:** The core of the project is a self-expanding binary tree. Users can add nodes to the tree without any administrator intervention.
* **API Validation Layer:** To ensure data integrity, the app connects to the RAWG.io API. Users cannot add fake games (e.g., "Super Mario Fake 99"); the system verifies the game exists before learning it.
* **Fuzzy Matching & Confirmation:** The application handles typos by finding the closest match in the API and asking the user for confirmation (e.g., correcting "skyrim" to "The Elder Scrolls V: Skyrim").
* **Undo Functionality:** Users can traverse back up the decision tree if they misclicked, utilizing a session-based history stack.
* **Visual Polish:** The application fetches and displays high-quality box art for games once guessed, providing a polished user experience.
* **Live Statistics Dashboard:** A dedicated `/stats` route allows users to visualize the growth of the neural network, tracking the total number of games and decision nodes learned.

### File Descriptions

#### `app.py`
This is the main controller file for the Flask application. It handles all routing and logic.
* **Database connection:** Initializes the connection to `game.db` using the CS50 SQL library.
* **`index` and `game` routes:** These manage the game loop. The `game` route checks the current `node_id` stored in the user's session. If the node is a question (`is_question=1`), it renders `question.html`. If it is a leaf node (`is_question=0`), it fetches the image URL and renders `guess.html`.
* **`answer` route:** This is the traversal logic. It takes the user's "Yes/No" input and updates the session's `current_node_id` to either the `yes_id` or `no_id` child of the current node. It also pushes the previous node to a `history` list to support the Undo feature.
* **`check_game` and `confirm_game` routes:** These handle the validation logic. When the user stumps the AI, `check_game` queries the RAWG API. `confirm_game` commits the verified name to the session.
* **`add_question` route:** This executes the database transaction to split a leaf node. It inserts two new nodes (the new game and the old game) and updates the current node to become a question.
* **`stats` route:** Queries the database for the total count of leaf nodes (games) and internal nodes (questions) to display the "Brain Monitor."

#### `schema.sql`
This file defines the structure of the SQLite database.
* **`nodes` table:** The primary table containing the binary tree.
    * `id`: Unique identifier for the node.
    * `text`: The content of the node (either a question string or a game title).
    * `is_question`: A boolean integer (1 or 0) distinguishing internal nodes from leaf nodes.
    * `yes_id` / `no_id`: Self-referencing foreign keys pointing to the child nodes.
* The schema also includes the initial "Seed Data," populating the tree with 15 initial nodes covering major genres (FPS, RPG, MOBA) to ensure the game functions immediately upon initialization.

#### `game.db`
The SQLite database generated from `schema.sql`. It stores the persistent state of the decision tree. As users play the game, this file grows in size, permanently remembering every new game taught to it.

#### `templates/` directory
* **`layout.html`:** The master template containing the Bootstrap CDN links, navbar, and custom CSS for the dark mode theme. It ensures visual consistency across all pages.
* **`question.html`:** Displays the current question and Yes/No buttons. It also includes the "Question Counter" badge.
* **`guess.html`:** Displays the final guess. It includes logic to render the game's box art if an image URL is passed from the backend.
* **`lose.html`:** The form where users input the game they were thinking of when the AI fails.
* **`confirm.html`:** The "Did you mean?" page that presents the API's search result to the user for verification.
* **`add_question.html`:** The input form where users provide the distinguishing question to split the tree node.
* **`stats.html`:** A dashboard displaying database metrics (total games, total questions) and a list of recently added games.

### Design Choices

#### 1. Binary Tree vs. Tag System
Initially, I considered a tag-based system (assigning tags like "RPG" or "Multiplayer" to games and filtering a list). However, I chose a **Binary Decision Tree** because it is more efficient O(log n) and better represents the CS50 curriculum's focus on data structures. A tree structure also allows for the "infinite growth" mechanic, whereas a tag system would require constant manual database updates to add new games.

#### 2. The Validation Problem
One of the biggest challenges in user-generated content is "garbage data." If a user types "My Cool Game" into the database, the game breaks for everyone else.
* *Attempt 1:* I initially thought about just trusting the user, but realized this would ruin the experience quickly.
* *Attempt 2:* I considered downloading a static CSV dataset of games. This was safer, but it limited the game to only older titles and removed the "magic" of finding obscure new games.
* *Final Solution:* I integrated the **RAWG.io API**. This offers the best of both worlds: access to a database of 500,000+ games that is professionally maintained, while still allowing the user to "teach" the local database any of those games dynamically.

#### 3. Handling User Typos
A major design hurdle was handling user input errors. If the database has "God of War" and a user types "god of war" (lowercase), a strict string comparison would fail, creating duplicate entries. I implemented a two-step validation:
1.  **Search:** The app searches the API with the user's raw input.
2.  **Normalization:** The app discards the user's input and uses the *official* title returned by the API (e.g., "Counter-Strike 2" instead of "cs2"). This ensures the database remains clean and standardized.

#### 4. The "Undo" Stack
During testing, I found it frustrating to accidentally click "Yes" and have to restart the entire game. I implemented a `session["history"]` list that behaves as a Stack (LIFO). Every time the user moves down the tree, the current Node ID is appended to the list. Clicking "Undo" simply pops the last ID and redirects, a classic example of Stack usage in navigation.
