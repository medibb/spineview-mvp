# MVP Specification  
## CSV-based Lumbo–Pelvic Flexion–Extension Dashboard

### 1. Purpose
This MVP aims to build a minimal Django-based dashboard that parses two Movella DOT IMU CSV files
(spine and pelvis), computes flexion–extension (FE) angles for each sensor, calculates relative FE
(spine minus pelvis), and visualizes all three signals as time-series plots.

Real-time streaming, databases, and clinical-grade biomechanical accuracy are explicitly out of scope.

---

### 2. Input Data

#### 2.1 Files
- Two CSV files:
  - spine_dot.csv
  - pelvis_dot.csv

#### 2.2 CSV Structure (Movella DOT format)
- The CSV contains a **metadata block at the top** (multiple rows).
- The actual data table starts **after the metadata**, with a header row containing:

Required columns:
- SampleTimeFine
- Quat_W
- Quat_X
- Quat_Y
- Quat_Z

Optional columns (ignored in this MVP):
- FreeAcc_X
- FreeAcc_Y
- FreeAcc_Z

The parser must skip metadata rows and detect the actual header.

---

### 3. Computation Logic

#### 3.1 Flexion–Extension Angle
- FE angle is derived from quaternion data.
- Only sagittal-plane motion is considered.
- A simplified quaternion-to-FE conversion is acceptable.
- High biomechanical accuracy is not required.

Outputs:
- FE_spine(t)
- FE_pelvis(t)

#### 3.2 Relative FE
Relative FE is defined as:

Relative_FE(t) = FE_spine(t) − FE_pelvis(t)

This represents a minimal lumbo–pelvic coordination metric.

---

### 4. Outputs

The dashboard must visualize three time-series signals:
1. Spine FE angle (degrees)
2. Pelvis FE angle (degrees)
3. Relative FE angle (degrees)

- X-axis: SampleTimeFine (or derived time)
- Y-axis: Angle (degrees)

---

### 5. Dashboard Requirements

- Single-page Django view
- CSV upload for spine and pelvis
- One line chart with three curves
- Chart.js for visualization
- No database
- No real-time streaming

---

### 6. Tech Stack

Backend:
- Python 3.10
- Django
- pandas
- numpy

Frontend:
- Django templates
- Chart.js (CDN)

---

### 7. Definition of Done

- CSV files load without error
- Metadata rows are skipped correctly
- FE_spine, FE_pelvis, and Relative_FE are computed
- All three curves render correctly on a single chart
