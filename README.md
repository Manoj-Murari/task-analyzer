# Smart Task Analyzer

A full-stack application that intelligently prioritizes tasks using a custom scoring algorithm. Built with Django (Backend) and Vanilla JS (Frontend).

## 🚀 Installation & Run Instructions

### Prerequisites
- Python 3.10+
- pip

### Backend Setup
1. Navigate to the `backend` directory:
   ```bash
   cd backend
````

2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Apply migrations:
    ```bash
    python manage.py migrate
    ```
4.  Run the server:
    ```bash
    python manage.py runserver
    ```
    The API will be available at `http://127.0.0.1:8000/`.

### AI Features Setup (Optional)

To enable AI-powered analysis:

1.  Get a Google Gemini API Key.
2.  Set the environment variable:
      - Windows (PowerShell): `$env:GEMINI_API_KEY="your_key_here"`
      - Linux/Mac: `export GEMINI_API_KEY="your_key_here"`
3.  Restart the server.

### Frontend Setup

1.  Navigate to the `frontend` directory.
2.  Open `index.html` in any modern web browser.
      - Note: Ensure the backend server is running first.

## 🧠 Scoring Algorithm & Strategies

The Smart Task Analyzer uses a weighted scoring system to determine task priority. The final score is calculated based on four key factors, which are weighted differently depending on the selected **Strategy**.

### Core Factors:

1.  **Urgency (Due Date)**:

      - Tasks due today get a base score of 100.
      - Overdue tasks receive a penalty boost (10 points per day overdue).
      - Tasks due soon (within 3 days) get a high score (80-50 range).

2.  **Importance**:

      - The user-defined importance (1-10) acts as a **multiplier**.
      - Standard multiplier: 1.1x to 2.0x.

3.  **Effort (Quick Wins)**:

      - Tasks estimated to take less than 2 hours receive a **+20 point bonus**.
      - Tasks taking \> 10 hours receive a small penalty (-10).

4.  **Dependencies**:

      - If a task blocks other tasks, it receives a **+15 point bonus per blocked task**.

### Strategies (Critical Thinking Implementation):

  - **Smart Balance (Default)**: Balances all factors evenly.
  - **Fastest Wins**: Prioritizes low-effort tasks (Quick Win bonus increased to +40). Importance is largely ignored to focus on clearing the queue.
  - **High Impact**: Prioritizes Importance above all else. The importance multiplier is increased (up to 3.0x), allowing critical tasks to outrank even urgent ones.
  - **Deadline Driven**: Urgency scores are multiplied by 1.5x, strictly prioritizing due dates over effort or importance.

## ❓ Answers to Critical Considerations (PDF)

*As requested in the assignment instructions:*

**1. How do you handle tasks with due dates in the past?**
Overdue tasks are treated as critical emergencies. In the scoring algorithm, they receive a base Urgency score of 100, plus an additional 10 points for every day they are overdue. This ensures that a task overdue by 5 days (Score 150+) will almost always appear at the very top of the list, alerting the user immediately.

**2. What if a task has missing or invalid data?**
I utilized Django REST Framework's `Serializer` validation to handle this strictly at the entry point:

  - **Missing Fields**: Requests missing `title` or `due_date` return a `400 Bad Request` with a clear error message.
  - **Invalid Types**: Non-numeric values for `estimated_hours` or `importance` are caught automatically.
  - **Defaults**: Optional fields like `dependencies` default to an empty list, and `importance` defaults to 1 if omitted, ensuring the algorithm always has valid data to work with.

**3. How do you detect circular dependencies?**
I implemented a cycle detection algorithm using **Depth-First Search (DFS)** in `scoring.py`.

  - The system builds an adjacency list of dependencies.
  - It traverses the graph, maintaining a `path` set of nodes currently in the recursion stack.
  - If the traversal encounters a node that is already in the current `path`, a circular dependency (A -\> B -\> A) is confirmed.
  - [cite\_start]The API then aborts the analysis and returns a specific `400` error, identifying exactly which task caused the cycle[cite: 38].

**4. Should your algorithm be configurable?**
Yes. Different users have different working styles. I implemented a **Strategy Pattern** via a frontend dropdown. This passes a `strategy` parameter ('fastest', 'impact', 'deadline') to the backend, which dynamically adjusts the weights and multipliers in the scoring logic. [cite\_start]This satisfies the "Critical Thinking" requirement to support different prioritization modes[cite: 39].

**5. How do you balance competing priorities (urgent vs important)?**
The "Smart Balance" strategy uses Urgency as the *base score* and Importance as a *multiplier*.

  - A highly urgent task (Score 100) with low importance (x1.0) = **100**.
  - A moderately urgent task (Score 60) with high importance (x2.0) = **120**.
    [cite\_start]This mathematical relationship ensures that while deadlines are crucial, high-value strategic work effectively "leapfrogs" urgent busywork when the importance difference is significant[cite: 40].

## 🛠 Design Decisions

  - **Stateless Analysis Endpoint**: The `/analyze/` endpoint was designed to accept a raw list of JSON tasks. This allows the frontend to send "what-if" scenarios without polluting the database.
  - **Database Persistence for Suggestions**: The `/suggest/` endpoint relies on the database (`Task` model). This separates the concern of "analyzing a scratchpad list" vs "managing my persistent task list."
  - **Vanilla JS Frontend**: I chose Vanilla JS to keep the project lightweight and dependency-free, ensuring it is easy to run and review without a complex build pipeline (like Webpack/Vite).

## ⏱ Time Breakdown

  - **Planning & Architecture**: 20 mins
  - **Backend Core (Models & Scoring)**: 60 mins
  - **API Development (Views & Serializers)**: 45 mins
  - **Frontend Implementation**: 45 mins
  - **Strategy & Bonus Logic**: 30 mins
  - **Testing & Documentation**: 30 mins
  - **Total**: \~3 hours 50 mins

## 🔮 Future Improvements

  - **User Accounts**: Multi-user support with authentication.
  - **Drag-and-Drop**: Interactive reordering of tasks.
  - **Email Notifications**: Alerts for overdue high-priority tasks.
  - **AI Description Analysis**: Use NLP to suggest importance based on task title/description.

<!-- end list -->

