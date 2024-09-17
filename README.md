# CITANZ Membership Dashboard

This project provides a dashboard for managing and visualizing membership data using a Flask backend and a React frontend with TypeScript and Tailwind CSS. Additionally, a Streamlit app is also provided for similar functionalities.

## Table of Contents

- [CITANZ Membership Dashboard](#citanz-membership-dashboard)
  - [Table of Contents](#table-of-contents)
  - [Project Structure](#project-structure)
  - [Prerequisites](#prerequisites)
  - [Setup](#setup)
    - [Step 1: Clone the repository](#step-1-clone-the-repository)
    - [Backend (Flask)](#backend-flask)
    - [Frontend (React)](#frontend-react)
    - [Streamlit App](#streamlit-app)
  - [Running the Application](#running-the-application)
    - [Backend](#backend)
    - [Frontend](#frontend)
    - [Streamlit App](#streamlit-app-1)
  - [API Endpoints](#api-endpoints)
  - [Notes](#notes)

## Project Structure

```
CITA/
├── backend/
│   ├── data/
│   ├── app.py                    # Main Flask application
│   ├── data_processing.py         # Data processing logic
├── frontend/
│   ├── node_modules/
│   ├── public/
│   ├── src/
│   │   ├── assets/
│   │   ├── components/            # React components
│   │   ├── config/
│   │   ├── model/
│   │   ├── utils/
│   │   ├── App.tsx                # Main entry point of React app
│   │   ├── main.tsx               # Main React render file
│   ├── .env                       # Environment file for frontend API URL
│   ├── package.json
├── streamlit_app.py               # Streamlit-based dashboard
├── README.md
```

## Prerequisites

Ensure that you have the following installed on your machine:

-   Python 3
-   Node.js 

## Setup

### Step 1: Clone the repository

To begin, clone the project repository from GitHub:

```bash
git clone git@github.com:aemooooon/cita-member-dashboard.git
cd cita-member-dashboard
```

### Backend (Flask)

1. Navigate to the `backend` directory:

    ```bash
    cd backend
    ```

2. Set up a Python virtual environment (optional but recommended):

    ```bash
    python -m venv venv
    source venv/bin/activate  # For Linux/Mac
    .\venv\Scripts\activate    # For Windows
    ```

3. Install the required Python packages:

    ```bash
    pip install -r requirements.txt
    ```

4. Run the Flask backend:
    ```bash
    python app.py
    ```

By default, the Flask backend will run on `http://127.0.0.1:5000`.

### Frontend (React)

1. Navigate to the `frontend` directory:

    ```bash
    cd frontend
    ```

2. Install the required Node modules:

    ```bash
    npm install
    ```

3. Configure the `.env` file for API connection. Ensure that the `.env` file in `src` points to the Flask backend:

    ```bash
    VITE_API_BASE_URL=http://127.0.0.1:5000
    ```

4. Run the frontend development server:
    ```bash
    npm run dev
    ```

By default, the frontend will be available at `http://127.0.0.1:5173`.

### Streamlit App

1. Navigate back to the root directory of the project.

2. Set up the Python environment as shown in the [Backend Setup](#backend-flask).

3. Run the Streamlit app:
    ```bash
    streamlit run streamlit_app.py
    ```

By default, the Streamlit app will run at `http://127.0.0.1:8501`.

## Running the Application

### Backend

To run the Flask backend:

```bash
cd backend
python app.py
```

### Frontend

To run the React frontend:

```bash
cd frontend
npm run dev
```

### Streamlit App

To run the Streamlit dashboard:

```bash
streamlit run streamlit_app.py
```

## API Endpoints

The Flask backend provides the following API endpoints:

-   **`/api/key_metrics`** - Get total, active, and new members.
-   **`/api/region_distribution`** - Get region distribution of members.
-   **`/api/membership_status`** - Get the membership status.
-   **`/api/payment_distribution`** - Get the distribution of payments.
-   **`/api/renewal_funnel`** - Get the renewal funnel data.
-   **`/api/income_trend`** - Get the trend of income over time.
-   **`/api/activity_heatmap`** - Get the member activity heatmap data.
-   **`/api/nz_city_distribution`** - Get the city distribution for New Zealand.
-   **`/api/new_members`** - Get the data for new members.

## Notes

-   Ensure both the backend and frontend are running simultaneously to use the full functionality of the project.
-   If deploying to a server, remember to update the frontend `.env` file with the correct API base URL.
