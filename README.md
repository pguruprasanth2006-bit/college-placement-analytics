# College Placement Analytics and Prediction System

An end-to-end, enterprise-grade, academic Python mini-project for college placement management, predictive eligibility evaluation, machine learning placement inference, and distributed data analysis.

---

## 1. Project Introduction

The **College Placement Analytics and Prediction System** is a full-stack web application designed for engineering colleges and universities to manage the complete campus recruitment lifecycle. The system integrates student record administration, company recruitment drive management, automated multi-criteria eligibility filtering, machine learning-driven student placement probability forecasting, and distributed big data analytics.

The system addresses critical challenges faced by placement training offices (TPOs):
- Manual matching of student criteria against company policies.
- Lack of data-backed insights on student employability strengths and weaknesses.
- Unreliable reporting on salary distribution and department placement success.
- Computational scalability limits when processing large historical placement archives.

---

## 2. Project Objectives

1. **Student Profile Administration**: Manage comprehensive academic and skill records with full validation (CGPA bounds, uniqueness constraints, arrears).
2. **Corporate Recruitment Coordination**: Register company hiring drives, package compensation, and academic criteria.
3. **Automated Eligibility Engine**: Instant qualification evaluation reporting exact rejection reasons (CGPA, arrears, departments, graduation year).
4. **Machine Learning Predictive Analytics**: Predict student placement likelihood using a trained Scikit-learn Random Forest Classifier.
5. **Statistical Reporting**: Compute KPI metrics, department rates, and salary distributions using Pandas and NumPy.
6. **Distributed Big Data Processing**: Execute high-throughput aggregation using PySpark DataFrames.
7. **Interactive Administrative Dashboard**: Visualize trends and key indicators through Chart.js charts and Bootstrap 5 UI.

---

## 3. Key Features

- **Centralized Admin Dashboard**: High-level KPI summary cards, dynamic Chart.js department breakdowns, year-on-year recruitment trends, and real-time placement logs.
- **Student Profile Management**: Full CRUD operations, search by name/register number, filters by department and batch year, and pagination.
- **Company & Drive Management**: Configure multi-department eligibility, minimum CGPA, maximum arrears, package (LPA), and roles.
- **Company Eligibility Engine**: Cross-matches registered candidates with company requirements, displaying both eligible pools and ineligible candidates with explicit disqualification causes.
- **Machine Learning Placement Predictor**:
  - Predicts placement likelihood (probability score and binary outcome).
  - Uses 6 predictive attributes: CGPA, standing arrears, aptitude score, technical score, communication score, and internship experience.
  - Displays feature importance weights, confusion matrix, accuracy, precision, recall, and F1-score.
  - Automatically persists all predictions to MySQL for longitudinal tracking.
- **PySpark Distributed Processing Engine**:
  - Distributed DataFrame aggregation over large historical datasets.
  - Calculates department aggregates, company statistics, salary distributions, and year trends.
  - Directly executable via live dashboard button or command line.
- **RESTful API Suite**: Complete JSON endpoints for students, companies, placements, analytics, eligibility checks, and predictions.
- **Secure Admin Authentication**: Password hashing using `werkzeug.security` with session protection across administrative routes.

---

## 4. Technology Stack

| Layer | Technologies |
|---|---|
| **Backend Framework** | Python 3.13, Flask 3.1, Application Factory Pattern, Flask Blueprints |
| **Database & ORM** | MySQL 9.x, SQLAlchemy 2.x, Flask-Migrate, PyMySQL |
| **Frontend & UI** | Jinja2 Templates, Bootstrap 5.3, Bootstrap Icons, HTML5, CSS3 |
| **Data Visualizations** | Chart.js 4.4 |
| **Data Science & Math** | Pandas 3.1, NumPy 2.5 |
| **Machine Learning** | Scikit-learn 1.9, Random Forest Classifier, Joblib |
| **Distributed Big Data** | Apache PySpark 4.3 (Java 25 / JVM local cluster) |
| **Testing Suite** | Pytest 9.2, Flask Test Client (isolated SQLite in-memory runner) |
| **Environment Management** | Python venv, python-dotenv |

---

## 5. System Architecture

The application adopts the **Flask Application Factory Pattern** combined with modular Blueprints, Service layers, and ORM abstractions:

```
college_placement_system/
│
├── app/
│   ├── __init__.py               # Application factory create_app() & blueprint registration
│   ├── extensions.py             # SQLAlchemy & Migrate instances
│   ├── auth.py                   # Login required decorator & session verification
│   │
│   ├── models/                   # SQLAlchemy Database Models
│   │   ├── __init__.py
│   │   ├── student.py            # Student model & profile relationships
│   │   ├── department.py         # Department model
│   │   ├── company.py            # Company model & company_departments association table
│   │   ├── placement.py          # Placement & application records
│   │   ├── prediction.py         # Persisted ML inference history
│   │   ├── eligibility.py        # Logged eligibility checks
│   │   └── user.py               # Admin user model with password hashing
│   │
│   ├── routes/                   # Blueprints for Web and API Routing
│   │   ├── __init__.py
│   │   ├── dashboard_routes.py   # Login, Logout, Dashboard view
│   │   ├── student_routes.py     # Student CRUD & detail views
│   │   ├── company_routes.py     # Company CRUD & drive definitions
│   │   ├── placement_routes.py   # Placements & interview tracking
│   │   ├── eligibility_routes.py # Eligibility matching interface
│   │   ├── analytics_routes.py   # Pandas/NumPy & PySpark views
│   │   ├── prediction_routes.py  # Model inference & interactive simulator
│   │   └── api_routes.py         # Full RESTful JSON API endpoints
│   │
│   ├── services/                 # Reusable Business Logic Services
│   │   ├── __init__.py
│   │   ├── eligibility_service.py# Evaluation rules engine
│   │   ├── analytics_service.py  # Pandas & NumPy statistics generator
│   │   ├── prediction_service.py # ML model loader & inference manager
│   │   └── spark_service.py      # PySpark executor & result cache reader
│   │
│   ├── templates/                # Jinja2 HTML5 Templates
│   │   ├── base.html             # Master layout with responsive sidebar
│   │   ├── login.html            # Admin login interface
│   │   ├── dashboard.html        # Main dashboard with KPI cards and Chart.js
│   │   ├── students.html         # Student directory with search/filters
│   │   ├── student_form.html     # Add/Edit student form with validations
│   │   ├── student_detail.html   # Student detail card with history
│   │   ├── companies.html        # Company cards & drive list
│   │   ├── company_form.html     # Company creation & department association
│   │   ├── placements.html       # Placement status list & stats
│   │   ├── placement_form.html   # Placement recording form
│   │   ├── eligibility.html      # Dual-pane eligible/ineligible pool view
│   │   ├── analytics.html        # Pandas/NumPy metrics & PySpark tabs
│   │   ├── prediction.html       # ML probability meter & metrics
│   │   └── errors/               # 404 and 500 error templates
│   │
│   └── static/                   # Static assets
│       ├── css/style.css         # Modern custom styling
│       ├── js/dashboard.js       # Chart.js initialization & UI scripts
│       └── images/               # Media & brand assets
│
├── ml/                           # Machine Learning Pipeline
│   ├── __init__.py
│   ├── train_model.py            # Random Forest training script
│   ├── evaluate_model.py         # Test set evaluation & report generator
│   └── saved_model/              # Serialized model (.joblib) & metrics (.json)
│
├── spark/                        # Distributed PySpark Module
│   ├── __init__.py
│   ├── placement_analysis.py     # SparkSession DataFrame aggregation
│   └── output/                   # Processed JSON outputs
│
├── data/
│   └── sample_placement_data.csv # 300 realistic student records across 5 depts
│
├── tests/                        # Automated Pytest Suite
│   ├── conftest.py               # Fixtures & in-memory test database
│   ├── test_students.py          # Student model & CRUD tests
│   ├── test_companies.py         # Company model & association tests
│   ├── test_eligibility.py       # Qualification & failure rule tests
│   ├── test_analytics.py         # Statistics & empty dataset tests
│   ├── test_prediction.py        # Model training & inference tests
│   ├── test_routes.py            # Route responses & auth tests
│   ├── test_spark.py             # PySpark DataFrame execution tests
│   └── test_api.py               # REST API endpoints verification
│
├── config.py                     # Centralized multi-environment configuration
├── seed_data.py                  # Database initialization & seeding script
├── run.py                        # Application entry point
├── requirements.txt              # Pinned Python package dependencies
├── .env.example                  # Environment configuration template
├── .gitignore                    # Version control ignore rules
└── README.md                     # Comprehensive documentation
```

---

## 6. Database ER Diagram

```mermaid
erDiagram
    Department ||--o{ Student : "enrolls"
    Department ||--o{ company_departments : "included_in"
    Company ||--o{ company_departments : "eligible_for"
    Student ||--o{ Placement : "participates_in"
    Company ||--o{ Placement : "offers"
    Student ||--o{ Prediction : "evaluated_by"
    Student ||--o{ Eligibility : "checked_for"
    Company ||--o{ Eligibility : "requires"

    Department {
        int id PK
        string department_name UK
        string department_code UK
        datetime created_at
    }

    company_departments {
        int company_id PK, FK
        int department_id PK, FK
    }

    Student {
        int id PK
        string register_number UK
        string name
        string email UK
        string phone
        int department_id FK
        float cgpa
        int arrears
        int graduation_year
        int aptitude_score
        int technical_score
        int communication_score
        int internship_experience
        text skills
        datetime created_at
    }

    Company {
        int id PK
        string company_name
        string job_role
        float minimum_cgpa
        int maximum_arrears
        float package
        int graduation_year
        datetime created_at
    }

    Placement {
        int id PK
        int student_id FK
        int company_id FK
        date placement_date
        string status
        float salary
        datetime created_at
    }

    Prediction {
        int id PK
        int student_id FK
        float probability
        string predicted_status
        string model_version
        datetime created_at
    }

    Eligibility {
        int id PK
        int student_id FK
        int company_id FK
        boolean is_eligible
        string rejection_reason
        datetime checked_at
    }

    AdminUser {
        int id PK
        string username UK
        string password_hash
        datetime created_at
    }
```

---

## 7. Installation and Setup Instructions

### Prerequisites
- **Python**: Version 3.11, 3.12, or 3.13.
- **Java**: Java 8, 11, 17, 21, or 25 installed and available on system path (required for PySpark).
- **MySQL**: MySQL Server 8.0, 8.4, or 9.x running on `localhost:3306`.
- **Git** (optional).

### Step 1: Clone or Navigate to the Workspace
```powershell
cd d:\pyProject\college_placement_system
```

### Step 2: Create and Activate Virtual Environment
```powershell
# Create virtual environment
python -m venv .venv

# Activate on Windows PowerShell
.\.venv\Scripts\Activate.ps1

# (Or on Linux/macOS)
# source .venv/bin/activate
```

### Step 3: Install Required Dependencies
```powershell
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables
Copy `.env.example` to `.env`:
```powershell
copy .env.example .env
```
Update your MySQL database credentials inside `.env`:
```env
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=super-secret-development-key-change-in-production

# MySQL Database Configuration
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_HOST=localhost
DB_PORT=3306
DB_NAME=college_placement_db
DATABASE_URL=mysql+pymysql://root:your_mysql_password@localhost:3306/college_placement_db

# Default Admin Credentials
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123

# Set to True if running in environments without MySQL
USE_SQLITE=False
```

### Step 5: Create the MySQL Database
Open MySQL command client or terminal:
```sql
CREATE DATABASE IF NOT EXISTS college_placement_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### Step 6: Initialize and Seed Database
Run the seeding script to create all tables and populate them with standard departments, companies, 300 student records, and historical placements:
```powershell
python seed_data.py
```

### Step 7: Train the Machine Learning Model
Train the Random Forest Classifier on historical data:
```powershell
python ml/train_model.py
```
This generates:
- `ml/saved_model/placement_model.joblib` (Random Forest binary)
- `ml/saved_model/model_metrics.json` (Accuracy, Precision, Recall, F1, Confusion Matrix, Feature Importances)

### Step 8: Execute PySpark Distributed Analysis
Run the standalone distributed analytics module:
```powershell
python spark/placement_analysis.py
```
This processes the dataset with Spark DataFrames and saves `spark/output/spark_analysis_results.json`.

---

## 8. Running the Application

Execute the application with:
```powershell
python run.py
```
Open your browser and navigate to:
```
http://127.0.0.1:5000
```
- **Login Credentials**:
  - Username: `admin`
  - Password: `admin123`

---

## 9. Running Automated Tests

Run the full Pytest test suite (36 tests verifying models, APIs, eligibility, analytics, ML inference, and PySpark):
```powershell
pytest -v
```
All tests utilize an isolated in-memory database to ensure zero disruption to live MySQL databases.

---

## 10. RESTful API Documentation

| Endpoint | Method | Description |
|---|---|---|
| `/api/students` | `GET` | Paginated list of students with filter support |
| `/api/students/<id>` | `GET` | Individual student details |
| `/api/students` | `POST` | Register a new student |
| `/api/students/<id>` | `PUT` | Update student details |
| `/api/students/<id>` | `DELETE` | Delete a student |
| `/api/companies` | `GET` | List all recruiting companies |
| `/api/companies` | `POST` | Register a new recruiting company drive |
| `/api/placements` | `GET` | List placement applications and selections |
| `/api/analytics/summary` | `GET` | High-level placement KPIs computed via NumPy |
| `/api/analytics/departments` | `GET` | Department-wise placement rate statistics |
| `/api/eligibility/check` | `POST` | Check student eligibility against company criteria |
| `/api/predictions/<student_id>` | `POST` | Run Random Forest placement prediction & persist |

---

## 11. Limitations and Future Enhancements

- **Real-Time Student Portal**: Future versions can introduce a dedicated student portal enabling students to self-apply for drives and upload resumes.
- **Natural Language Resume Parsing**: Integration with LLMs/Transformers to parse resumes directly into the student skill database.
- **Automated Email Notifications**: Trigger email alerts to eligible students when a new recruitment drive matching their profile is scheduled.
- **Deep Learning / XGBoost Benchmarking**: Incorporate gradient boosted decision trees (XGBoost/LightGBM) to benchmark alongside Random Forest.

