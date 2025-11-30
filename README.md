# Smart Task Analyzer

A full-stack application designed to intelligently prioritize tasks by assigning a priority score based on multiple factors. The system implements a custom, configurable scoring algorithm to help users identify which tasks they should work on first.

Built with **Python/Django (Backend)** and **Vanilla JS/HTML/CSS (Frontend)**.

-----

## 🚀 Installation & Run Instructions (Local Development)

### Prerequisites

  - Python 3.10+
  - pip

### 1\. Backend Setup

1.  Navigate to the `backend` directory.
2.  Install dependencies (Django, DRF, CORS Headers):
    ```bash
    pip install -r requirements.txt
    ```
3.  Apply migrations to set up the SQLite database:
    ```bash
    python manage.py migrate
    ```
4.  Run the Django server in one terminal:
    ```bash
    python manage.py runserver
    ```
    The API will be available at `http://127.0.0.1:8000/api/tasks/`.

### 2\. Frontend Setup

The frontend communicates with the API using JavaScript `fetch`. To avoid CORS policy errors with `file://` protocol, the frontend must be served via a simple HTTP server:

1.  **Open a second terminal** and navigate to the `frontend` directory.
2.  Start a simple web server (requires Python 3.x):
    ```bash
    python -m http.server 8080
    ```
3.  Open your browser and navigate to: **`http://localhost:8080/index.html`**

-----

## 🧠 Priority Scoring Algorithm Explanation

The core challenge of this assignment is the **`Smart Balance`** scoring function, which converts four competing factors into a single, comprehensive priority score. The final score determines the ranking, with a higher score indicating higher priority.

### 1\. Urgency (Due Date) - Base Score (40%)

Urgency provides the initial base score, emphasizing tasks that are expiring.

  * **Overdue:** Base score of 100 + **10 points for every day overdue**.
  * **Due Today:** Base score of **100 points**.
  * **Due Soon (1-3 days):** High base score (80 down to 50 points).
  * *Implementation:* Uses `datetime.date.today()` to calculate days until due.

### 2\. Importance - Multiplier (30%)

The user-defined importance (1-10) is applied as a **multiplier** to the Urgency score.

  * **Formula:** Multiplier = 1 + (`importance` / 10).
  * **Effect:** An importance of 10 results in a 2.0x multiplier, ensuring critical tasks are ranked highly even if their deadline is moderate.

### 3\. Dependencies - Bottleneck Bonus (20%)

The system checks how many *other* tasks list the current task as a dependency.

  * If a task is blocking one or more tasks, it receives a **+15 point bonus per blocked task**.
  * This ensures bottlenecks are cleared first, preventing downstream work stoppage.

### 4\. Effort (Quick Wins) - Flat Bonus/Penalty (10%)

Effort is used to encourage quick tasks or penalize massive ones.

  * **Quick Win:** Tasks $\le 2$ hours receive a **+20 point bonus**.
  * **High Effort:** Tasks $> 10$ hours receive a **-10 point penalty**.

-----

## ❓ Answers to Critical Considerations (Critical Thinking)

*As required by the assignment, here is the documentation of design decisions made for critical edge cases:*

**Q: How do you handle tasks with due dates in the past?**
A: Overdue tasks are treated as a critical priority. The algorithm assigns a base score of 100 points and then applies an aggressive **+10 point bonus for every day** the task is past its due date. This mathematically guarantees that overdue tasks climb to the top of the priority list immediately.

**Q: What if a task has missing or invalid data?**
A: Data integrity is ensured by the Django REST Framework Serializers (`TaskInputSerializer`).

  - Missing required fields (like `title` or `due_date`) are rejected with a `400 Bad Request`.
  - If optional fields like `importance` or `estimated_hours` are missing, they default to `1` and `0` respectively, allowing the calculation to proceed without crashing.

**Q: How do you detect circular dependencies?**
A: Before scoring, the system performs a **Depth-First Search (DFS)** cycle detection in the `detect_circular_dependencies` function. If a cycle (e.g., A depends on B, and B depends on A) is found, the analysis is halted, and the API returns a `400 Bad Request` with an explicit error message, preventing logic deadlocks.

**Q: How do you balance competing priorities (urgent vs important)?**
A: The core **`Smart Balance`** strategy handles this: Urgency sets the base score, and Importance applies the multiplier. This prevents a high-urgency, low-importance task from automatically overriding a high-importance task that is slightly less urgent (e.g., a critical task with a deadline next week often outranks a minor task due tomorrow).

**Q: Should your algorithm be configurable?**
A: Yes. The system includes a **Strategy Dropdown** that passes a parameter (`strategy`) to the backend. This allows the user to switch between different weighting mechanisms (e.g., **Fastest Wins**, **Deadline Driven**, **High Impact**) by adjusting the multipliers and bonuses in `scoring.py`.

-----

## 🛠 Design Decisions

  - **Backend:** **Django & DRF** was chosen for its rapid API development capabilities, robust data modeling (`Task` model handles Many-to-Many dependencies), and built-in features like the admin interface and ORM.
  - **Frontend:** **Vanilla JavaScript** was used to keep the frontend lightweight and dependency-free, prioritizing code clarity and ease of review.
  - **API Design:** The `/analyze/` endpoint is designed to be **stateless for input** (accepts raw JSON payload) but triggers a **state change** by saving the tasks to the DB to enable the persistence needed for the `/suggest/` feature.
  - **Vercel Compatibility:** Database configuration in `settings.py` automatically switches to an **in-memory SQLite DB** when deployed to Vercel, allowing the application to function correctly in a serverless environment (though data is ephemeral).

-----

## ⏱ Time Breakdown

  - **Planning & Architecture**: 20 mins
  - **Backend Core (Models & Scoring)**: 60 mins
  - **API Development (Views & Serializers)**: 45 mins
  - **Frontend Implementation**: 45 mins
  - **Critical Thinking (Strategy & Cycle Detection)**: 60 mins
  - **Testing & Documentation**: 30 mins
  - **Total**: **\~4 hours 0 minutes** (Focusing on quality over speed)

-----

## 🔮 Future Improvements (Bonus Challenges)

  - **Dependency Graph Visualization:** Implement a D3.js or similar library view to visually display dependencies and highlight the critical path or circular dependencies.
  - **Date Intelligence:** Adjust urgency calculations to recognize and avoid weekends and holidays.
  - **User Accounts:** Add a robust authentication system to allow multiple users to manage their own task lists.
  - **Unit Tests:** Expand test coverage for all scoring edge cases beyond the basic tests provided in `tests.py`.