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
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Apply migrations:
   ```bash
   python manage.py migrate
   ```
4. Run the server:
   ```bash
   python manage.py runserver
   ```
   The API will be available at `http://127.0.0.1:8000/`.

### AI Features Setup (Optional)
To enable AI-powered analysis:
1. Get a Google Gemini API Key.
2. Set the environment variable:
   - Windows (PowerShell): `$env:GEMINI_API_KEY="your_key_here"`
   - Linux/Mac: `export GEMINI_API_KEY="your_key_here"`
3. Restart the server.

### Frontend Setup
1. Navigate to the `frontend` directory.
2. Open `index.html` in any modern web browser.
   - Note: Ensure the backend server is running first.

## 🧠 Scoring Algorithm Explanation

The Smart Task Analyzer uses a weighted scoring system to determine task priority. The final score is calculated based on four key factors:

1.  **Urgency (Due Date)**:
    - Tasks due today get a base score of 100.
    - Overdue tasks receive a penalty boost (10 points per day overdue).
    - Tasks due soon (within 3 days) get a high score (80-50 range).
    - Tasks due further out receive a lower urgency score.

2.  **Importance**:
    - The user-defined importance (1-10) acts as a **multiplier**.
    - A task with Importance 10 multiplies the base score by 2.0x.
    - This ensures that even non-urgent but critical tasks rise to the top.

3.  **Effort (Quick Wins)**:
    - Tasks estimated to take less than 2 hours receive a **+20 point bonus**.
    - This encourages clearing small tasks quickly ("Quick Wins").
    - Tasks taking > 10 hours receive a small penalty (-10) to prioritize manageable work chunks.

4.  **Dependencies**:
    - If a task blocks other tasks, it receives a **+15 point bonus per blocked task**.
    - This ensures that bottlenecks are identified and prioritized.

**Circular Dependency Detection**:
The system performs a Depth-First Search (DFS) to detect circular dependencies (e.g., A blocks B, B blocks A). If a cycle is detected, the analysis is halted, and an error is returned to prevent logical deadlocks.

## 🛠 Design Decisions

-   **Django & DRF**: Chosen for robust data handling and rapid API development.
-   **Vanilla JS Frontend**: Kept lightweight and dependency-free to ensure fast load times and easy understanding.
-   **Stateless Analysis vs. Stateful Suggestions**:
    -   The `/analyze/` endpoint is designed to be flexible, accepting a raw JSON payload for immediate analysis without requiring prior database entry. However, to support the "Suggest" feature, tasks are persisted to the database during analysis.
-   **Dark Mode UI**: A modern, developer-friendly aesthetic using a dark color palette for reduced eye strain.

## ⚠️ Edge Case Strategy

-   **Circular Dependencies**: Explicitly handled with a cycle detection algorithm.
-   **Missing Data**: Default values are used (e.g., Importance defaults to 1).
-   **Invalid JSON**: The frontend catches JSON parsing errors before sending to the backend.
-   **Network Errors**: Graceful error messages are displayed if the backend is unreachable.

## ⏱ Time Breakdown

-   **Planning**: 15 mins
-   **Backend (Models & Logic)**: 45 mins
-   **API & Views**: 30 mins
-   **Frontend (UI & Logic)**: 45 mins
-   **Testing & Documentation**: 20 mins
-   **Total**: ~2.5 - 3 hours

## 🔮 Future Improvements

-   **User Accounts**: Multi-user support with authentication.
-   **Drag-and-Drop**: Interactive reordering of tasks.
-   **Email Notifications**: Alerts for overdue high-priority tasks.
-   **AI Description Analysis**: Use NLP to suggest importance based on task title/description.
