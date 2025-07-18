# Shopify Insights Fetcher 🛍️

A robust backend application built with FastAPI that asynchronously scrapes public data from Shopify stores, persists the insights in a MySQL database, and automatically identifies and queues competitors for analysis.

This project was developed as part of a GenAI Developer Intern assignment, demonstrating best practices in backend development, including clean architecture, OOP principles, and handling long-running, asynchronous tasks.

---
## ✨ Key Features

- **Asynchronous Scraping**: Uses FastAPI's `BackgroundTasks` to handle time-consuming scraping jobs without blocking the API.
- **Database Persistence**: Stores all scraped data in a MySQL database using SQLAlchemy ORM.
- **Comprehensive Data Extraction**: Gathers a wide range of insights, including:
  - Full Product Catalogs (`/products.json`)
  - Hero Products & Brand Context
  - Policies (Privacy, Refund/Return)
  - FAQs and Contact Details
  - Social Media Handles
- **Automated Competitor Analysis**: After scraping a primary brand, the system automatically identifies and queues its main competitors for scraping.
- **RESTful API**: Provides clean, well-documented endpoints to start jobs and retrieve results.

---
## 🛠️ Technology Stack

- **Backend**: Python, FastAPI
- **Database**: MySQL
- **ORM**: SQLAlchemy
- **Data Parsing**: BeautifulSoup4, Requests
- **Server**: Uvicorn

---
## 🚀 Getting Started

Follow these instructions to get a local copy up and running for development and testing purposes.

### Prerequisites

- Python 3.9+
- A running MySQL server

### Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/YOUR_USERNAME/shopify-insights-fetcher.git](https://github.com/YOUR_USERNAME/shopify-insights-fetcher.git)
    cd shopify-insights-fetcher
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    # For Windows
    python -m venv venv
    .\venv\Scripts\activate

    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Create a `requirements.txt` file:**
    Before installing, it's good practice to create this file. Run the following command in your terminal:
    ```bash
    pip freeze > requirements.txt
    ```
    Now, install all dependencies from the file you just created:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure the Database:**
    - Open the `app/database.py` file.
    - Update the `SQLALCHEMY_DATABASE_URL` with your MySQL credentials (remember to URL-encode your password if it contains special characters).
    ```python
    SQLALCHEMY_DATABASE_URL = "mysql+pymysql://USER:PASSWORD@HOST/DB_NAME"
    ```

5.  **Run the Server:**
    The application will automatically create the necessary tables in your database on the first run.
    ```bash
    uvicorn app.main:app --reload
    ```
    The server will be running at `http://127.0.0.1:8000`.

---
## 📖 API Usage

Access the interactive API documentation (Swagger UI) at `http://127.0.0.1:8000/docs`.

### 1. Create a Scraping Job

- **Endpoint**: `POST /create-scrape-job`
- **Status Code**: `202 Accepted`
- **Description**: Starts a scraping job in the background and returns a job ID instantly.

**Request Body:**
```json
{
  "website_url": "[https://memy.co.in](https://memy.co.in)"
}


