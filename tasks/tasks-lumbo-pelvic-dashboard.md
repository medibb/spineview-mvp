# Tasks: Lumbo-Pelvic Flexion-Extension Analysis Dashboard

## Relevant Files

- `manage.py` - Django project management script
- `config/settings.py` - Django settings configuration
- `config/urls.py` - Main URL routing configuration
- `config/wsgi.py` - WSGI configuration for deployment
- `dashboard/__init__.py` - Dashboard app initialization
- `dashboard/views.py` - Main view handlers for dashboard
- `dashboard/urls.py` - Dashboard-specific URL routing
- `dashboard/forms.py` - File upload forms
- `dashboard/services/__init__.py` - Services module initialization
- `dashboard/services/csv_parser.py` - CSV file parsing logic with Movella DOT format handling
- `dashboard/services/quaternion.py` - Quaternion to Euler angle conversion
- `dashboard/services/fe_calculator.py` - Flexion-Extension angle calculation
- `dashboard/services/statistics.py` - Statistical analysis and metrics calculation
- `dashboard/templates/dashboard/base.html` - Base template with layout
- `dashboard/templates/dashboard/index.html` - Main dashboard page
- `dashboard/templates/dashboard/components/upload.html` - File upload component
- `dashboard/templates/dashboard/components/timeseries.html` - Time series chart component
- `dashboard/templates/dashboard/components/statistics.html` - Statistics display component
- `static/css/custom.css` - Custom CSS styles
- `static/js/charts.js` - Chart rendering logic (Plotly.js/Chart.js)
- `static/js/upload.js` - File upload handling and AJAX
- `requirements.txt` - Python dependencies
- `uploads/.gitkeep` - Placeholder for upload directory

## Instructions for Completing Tasks

**IMPORTANT:** As you complete each task, you must check it off in this markdown file by changing `- [ ]` to `- [x]`. This helps track progress and ensures you don't skip any steps.

Example:
- `- [ ] 1.1 Read file` → `- [x] 1.1 Read file` (after completing)

Update the file after completing each sub-task, not just after completing an entire parent task.

## Tasks

- [x] 0.0 Create feature branch
  - [x] 0.1 Create and checkout a new branch (e.g., `git checkout -b feature/lumbo-pelvic-dashboard`)

- [x] 1.0 Set up Django project structure and dependencies
  - [x] 1.1 Create requirements.txt with all necessary dependencies (Django 4.2+, NumPy, Pandas, SciPy)
  - [x] 1.2 Initialize Django project with `django-admin startproject config .`
  - [x] 1.3 Create dashboard app with `python manage.py startapp dashboard`
  - [x] 1.4 Create directory structure (services/, templates/, static/, uploads/)
  - [x] 1.5 Configure settings.py (INSTALLED_APPS, TEMPLATES, STATIC_FILES, MEDIA settings)
  - [x] 1.6 Create uploads/.gitkeep for upload directory

- [x] 2.0 Implement data processing services (CSV parsing, quaternion conversion, calculations)
  - [x] 2.1 Create dashboard/services/__init__.py
  - [x] 2.2 Implement csv_parser.py with Movella DOT format parsing (handle trailing commas, skip metadata)
  - [x] 2.3 Implement quaternion.py with quaternion to Euler angle conversion functions
  - [x] 2.4 Implement fe_calculator.py for Flexion-Extension angle calculations
  - [x] 2.5 Add time synchronization logic for spine and pelvis data
  - [x] 2.6 Implement relative FE angle calculation (spine - pelvis)

- [x] 3.0 Create backend API endpoints and views
  - [x] 3.1 Create dashboard/forms.py for file upload validation
  - [x] 3.2 Implement dashboard/views.py with main dashboard view
  - [x] 3.3 Create API endpoint for file upload (POST /api/upload/)
  - [x] 3.4 Create API endpoint for data analysis (POST /api/analyze/)
  - [x] 3.5 Implement JSON response formatting according to PRD specification
  - [x] 3.6 Configure dashboard/urls.py and integrate with config/urls.py

- [x] 4.0 Build frontend dashboard UI with Tailwind CSS
  - [x] 4.1 Create base.html template with Tailwind CSS CDN and overall layout
  - [x] 4.2 Create index.html main dashboard page structure
  - [x] 4.3 Create components/upload.html for drag-and-drop file upload
  - [x] 4.4 Create components/timeseries.html for chart containers
  - [x] 4.5 Create components/statistics.html for statistics cards display
  - [x] 4.6 Add custom CSS in static/css/custom.css for additional styling
  - [x] 4.7 Implement responsive grid layout (desktop/tablet/mobile)

- [x] 5.0 Implement interactive charts and visualizations
  - [x] 5.1 Add Plotly.js CDN to base template
  - [x] 5.2 Create static/js/charts.js for chart rendering logic
  - [x] 5.3 Implement main FE angle time series chart (spine, pelvis, relative)
  - [x] 5.4 Implement angular velocity (Gyr) time series chart
  - [x] 5.5 Implement acceleration (Acc) time series chart
  - [x] 5.6 Add interactive features (zoom, pan, hover tooltips, legend toggle)
  - [x] 5.7 Implement angle-angle plot (coordination scatter plot)

- [x] 6.0 Add statistical analysis and coordination metrics
  - [x] 6.1 Implement statistics.py with ROM, mean, std, max, min calculations
  - [x] 6.2 Add angular velocity analysis (peak, RMS, mean)
  - [x] 6.3 Add acceleration analysis (magnitude, variability, jerk)
  - [x] 6.4 Implement coordination analysis (R², correlation, contribution ratio)
  - [x] 6.5 Create distribution analysis (histogram, box plot data)
  - [x] 6.6 Add Shapiro-Wilk normality test

- [x] 7.0 Implement error handling and validation
  - [x] 7.1 Add file extension validator (CSV only)
  - [x] 7.2 Add file size validator (max 50MB)
  - [x] 7.3 Add required columns validator (Quat_W, X, Y, Z)
  - [x] 7.4 Add minimum rows validator (min 100 rows)
  - [x] 7.5 Add quaternion range validator (|q| ≈ 1)
  - [x] 7.6 Implement user-friendly error messages according to PRD
  - [x] 7.7 Add loading indicators and error display in frontend

- [x] 8.0 Testing and quality assurance
  - [x] 8.1 Test CSV parsing with real spine_dot.csv data
  - [x] 8.2 Test quaternion to Euler conversion accuracy
  - [x] 8.3 Test FE angle calculations
  - [x] 8.4 Test file upload flow (both files, one file, invalid file)
  - [x] 8.5 Test responsive layout on different screen sizes
  - [x] 8.6 Test chart interactivity (zoom, pan, hover)
  - [x] 8.7 Verify statistical calculations accuracy
  - [x] 8.8 End-to-end test: upload → analyze → visualize
