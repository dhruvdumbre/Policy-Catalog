# Policy Catalog

A web-based insurance policy management application built with **Python, Flask, SQLite, HTML, CSS, and JavaScript**. The application provides policy CRUD operations, an analytics dashboard, CSV-based data ingestion, and automated data quality auditing.

## Features

### 1. Policy Management (CRUD)
- **Create:** Add new insurance policy types.
- **Read:** View all policies and browse policy details.
- **Update:** Modify existing policy information.
- **Delete:** Remove policies from the catalog.
- **Validation:** Validate policy names, categories, premiums, and coverage amounts.
- **Persistent storage:** Store policy records in an SQLite database.

### 2. Analytics Dashboard
- View the total number of policies and categories.
- Analyze minimum and maximum premium statistics.
- Explore policy distribution and coverage metrics.
- Visualize policy data using interactive charts.

### 3. CSV Import & ETL Pipeline
- Upload policy data through a CSV file.
- Validate the file structure and required columns.
- Transform and normalize imported values.
- Detect duplicate records within the uploaded file and against existing records.
- Preview valid and invalid records before importing.
- Import valid records into the SQLite database.

### 4. Data Quality Engine
- Audit policy records for data quality issues.
- Detect missing policy names and categories.
- Identify invalid categories and numeric values.
- Check premium ranges and coverage constraints.
- Identify duplicate policy name/category combinations.
- Calculate a data quality score and summarize affected records.
- Export audit findings as a CSV report.

The data quality audit is designed to report issues without modifying existing records.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Application logic and data processing |
| Flask | Web application and REST API |
| SQLite | Relational database |
| HTML5 | Page structure |
| CSS3 | Styling and responsive layouts |
| JavaScript | Frontend interactions and API communication |
| Plotly.js | Interactive data visualizations |
| Pandas | Data analysis |
| Python `csv` module | CSV processing and report generation |

## Project Structure

```text
policy_catalog/
├── app.py                    # Flask application and API routes
├── main.py                   # Command-line application
├── database.py               # SQLite database operations
├── analytics.py              # Analytics calculations
├── etl.py                    # CSV import and ETL processing
├── data_quality.py           # Data quality auditing
├── templates/
│   ├── dashboard.html        # Main dashboard
│   ├── index.html            # Policy listing and management
│   ├── analytics.html        # Analytics dashboard
│   ├── import.html           # CSV import interface
│   └── quality.html          # Data quality report
├── static/
│   ├── css/
│   │   └── style.css         # Application styling
│   └── js/
│       ├── dashboard.js      # Dashboard functionality
│       ├── script.js         # Policy management interactions
│       ├── analytics.js      # Analytics functionality
│       ├── import.js         # CSV import interactions
│       └── quality.js        # Data quality interface
├── policy_catalog.db         # Local database, generated at runtime
├── requirements.txt          # Python dependencies, if maintained
└── README.md                 # Project documentation
```

*The structure above describes the expected project layout. Keep only the files that actually exist in your repository.*

## Prerequisites

- Python 3
- pip
- A web browser
- Git (optional, for version control)

## Installation

### 1. Clone the repository

```powershell
git clone https://github.com/dhruvdumbre/Policy-Catalog.git
cd Policy-Catalog
```

### 2. Create a virtual environment

```powershell
python -m venv .venv
```

Activate it in Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

If the project has a `requirements.txt` file:

```powershell
pip install -r requirements.txt
```

Otherwise, install the packages required by the application. For the current Flask and Pandas implementation, this will typically include:

```powershell
pip install Flask pandas
```

Plotly.js is loaded through a CDN in the analytics page, so a separate Python Plotly package is not required for that frontend charting setup.

## Running the Application

Start the Flask application from the project directory:

```powershell
python app.py
```

Open the local application in your browser:

**http://127.0.0.1:5000**

The database is initialized by the application according to its database initialization logic.

To run the original command-line interface, if required:

```powershell
python main.py
```

## Application Pages

| Page | Route | Purpose |
|---|---|---|
| Dashboard | `/` | Overview and quick actions |
| All Policies | `/policies` | Browse and manage policy records |
| Analytics | `/analytics` | View policy statistics and charts |
| CSV Import | `/import` | Upload, preview, and import CSV data |
| Data Quality | `/quality` | Audit records and export quality findings |

## Policy Data Fields

| Field | Description |
|---|---|
| `policy_type_id` | Automatically generated policy identifier |
| `name` | Name of the insurance policy type |
| `category` | Insurance category |
| `min_premium` | Minimum premium amount |
| `max_premium` | Maximum premium amount |
| `coverage_amount` | Coverage amount offered by the policy |

## Validation Rules

- Policy names must not be empty.
- A policy name must be unique within its category.
- Categories must belong to the configured list: `Motor`, `Health`, `Life`, `Travel`, `Home`, or `Other`.
- Premium amounts must be positive numbers.
- The minimum premium must be lower than the maximum premium.
- Coverage must be positive.
- The current validation logic checks that coverage is at least the maximum premium.

## CSV Import Format

The CSV file must contain these column names:

```csv
name,category,min_premium,max_premium,coverage_amount
Family Health Plus,Health,5000,15000,500000
Secure Life Plan,Life,3000,12000,1000000
Vehicle Protect,Motor,2500,8000,300000
```

Follow the import page's validation results before committing records. Use fictional test data rather than real customer or policyholder information.

## API Endpoints

The application exposes REST-style endpoints for its web interface.

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/policies` | GET | Retrieve policy records |
| `/api/analytics` | GET | Retrieve analytics data |
| `/api/import/preview` | POST | Validate and preview a CSV upload |
| `/api/import/commit` | POST | Import approved records |
| `/api/quality` | GET | Retrieve the data quality audit |
| `/api/quality/report.csv` | GET | Download quality findings as CSV |

The policy CRUD API may include additional routes for creating, updating, and deleting records; refer to `app.py` for the exact methods and endpoint paths.

## Testing Checklist

- [ ] Create a policy with valid data.
- [ ] View the policy list and confirm the new record appears.
- [ ] Update a policy and verify the changes.
- [ ] Delete a policy and verify its removal.
- [ ] Confirm invalid inputs are rejected.
- [ ] Confirm analytics reflect the current database records.
- [ ] Upload a valid CSV and inspect its preview.
- [ ] Test missing columns, invalid numeric values, and duplicate records.
- [ ] Import valid rows and confirm they are saved.
- [ ] Run the data quality audit.
- [ ] Download and inspect the quality report.
- [ ] Restart the application and verify database persistence.

## Data and Security Notes

- The SQLite database is local application data and should generally not be committed to Git.
- Do not commit passwords, API keys, `.env` files, or real customer information.
- Use fictional records for development and demonstrations.
- CSV uploads should be tested with valid and invalid input files.

## Future Enhancements

- Automated unit and integration tests.
- Improved error handling and import summaries.
- Additional analytics and category-level comparisons.
- Pagination and advanced policy filtering.
- Automated data quality checks during ingestion.
- Deployment using a production-ready WSGI server.

## Author

**Dhruv Dumbre**

GitHub: [dhruvdumbre](https://github.com/dhruvdumbre)

Repository: [Policy-Catalog](https://github.com/dhruvdumbre/Policy-Catalog)

---

This project demonstrates practical skills in Python development, REST APIs, relational databases, CRUD operations, ETL workflows, data validation, analytics, and data quality management.
