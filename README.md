# SafeEcho

SafeEcho is a scam detection application that uses AI to analyze text and audio for potential threats.

## Prerequisites

- Python 3.8+
- pip

## Installation

1.  Navigate to the project root directory:
    ```bash
    cd d:\TP\SafeEcho
    ```

2.  Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Running the Application

1.  Start the backend server (which also serves the frontend):
    ```bash
    uvicorn backend.app:app --reload
    ```

2.  Open your browser and navigate to:
    http://127.0.0.1:8000

## Project Structure

-   `backend/`: Contains the FastAPI server and machine learning models.
-   `frontend/`: Contains the static frontend files (HTML, CSS, JS).
