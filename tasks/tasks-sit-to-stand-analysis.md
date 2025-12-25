# Tasks: Sit-to-Stand Movement Analysis

## Relevant Files

### Backend Files
- `dashboard/services/sit_to_stand.py` - New service module for sit-to-stand specific analysis logic (repetition segmentation, angle calculations, scoring)
- `dashboard/services/statistics.py` - Extend with sit-to-stand statistical functions
- `dashboard/views.py` - Modify analyze_movement view to return both squat and sit-to-stand analyses
- `dashboard/forms.py` - Reuse existing CSV validation (no changes needed)

### Frontend Files
- `dashboard/templates/dashboard/index.html` - Add tab navigation UI after file upload
- `dashboard/templates/dashboard/sit_to_stand.html` - New template for sit-to-stand analysis panel layout
- `static/js/tabs.js` - New JavaScript module for tab switching logic
- `static/js/sit-to-stand-charts.js` - New module for sit-to-stand visualizations (lordosis, hip hinge, trunk lean)
- `static/js/upload.js` - Modify to handle dual analysis response
- `static/css/custom.css` - Add styles for tab navigation and sit-to-stand panels

### Notes
- No unit tests required per project conventions (no existing test files)
- Reuse existing Plotly.js infrastructure from squat analysis
- Both analyses will be computed from the same uploaded CSV files

## Instructions for Completing Tasks

**IMPORTANT:** As you complete each task, you must check it off in this markdown file by changing `- [ ]` to `- [x]`. This helps track progress and ensures you don't skip any steps.

Example:
- `- [ ] 1.1 Read file` → `- [x] 1.1 Read file` (after completing)

Update the file after completing each sub-task, not just after completing an entire parent task.

## Tasks

- [x] 0.0 Feature branch already created (feature/sit-to-stand)

- [ ] 1.0 Implement backend sit-to-stand analysis engine
  - [ ] 1.1 Read existing `dashboard/services/statistics.py` to understand squat analysis structure
  - [ ] 1.2 Create new file `dashboard/services/sit_to_stand.py`
  - [ ] 1.3 Implement function to calculate lumbar lordosis angle (spine FE - pelvis FE)
  - [ ] 1.4 Implement function to calculate pelvic rotation (pitch angle from pelvis quaternion)
  - [ ] 1.5 Implement function to calculate trunk forward lean (pitch angle from spine quaternion)
  - [ ] 1.6 Implement lordosis maintenance score calculation (% of frames ≤0°)
  - [ ] 1.7 Implement hip hinge score calculation (normalize pelvic rotation range 30-60° to 0-100)
  - [ ] 1.8 Implement trunk lean strategy score calculation
  - [ ] 1.9 Create main `analyze_sit_to_stand()` function that returns all metrics and scores

- [ ] 2.0 Extend API to return dual analysis results
  - [ ] 2.1 Read `dashboard/views.py` to understand current `analyze_movement` view
  - [ ] 2.2 Import sit-to-stand analysis functions in views.py
  - [ ] 2.3 Modify `analyze_movement` view to call both squat and sit-to-stand analysis
  - [ ] 2.4 Update JSON response structure to include both `squat_analysis` and `sit_to_stand_analysis` keys
  - [ ] 2.5 Ensure backward compatibility with existing squat-only frontend code

- [ ] 3.0 Implement tab navigation UI structure
  - [ ] 3.1 Read `dashboard/templates/dashboard/index.html` to understand current structure
  - [ ] 3.2 Add tab navigation HTML after file upload section, before `#analysisResults`
  - [ ] 3.3 Create two tab buttons: "스쿼트 분석" and "앉았다 일어서기 분석"
  - [ ] 3.4 Add CSS classes for active/inactive tab states in `static/css/custom.css`
  - [ ] 3.5 Create `static/js/tabs.js` for tab switching logic
  - [ ] 3.6 Implement `switchTab(tabName)` function to show/hide content based on selected tab
  - [ ] 3.7 Link tabs.js in base.html script includes

- [ ] 4.0 Create sit-to-stand panel layout
  - [ ] 4.1 Create new file `dashboard/templates/dashboard/sit_to_stand.html`
  - [ ] 4.2 Add three-column grid container for main panels (lordosis, hip hinge, trunk lean)
  - [ ] 4.3 Create lordosis panel div with chart container and statistics table
  - [ ] 4.4 Create pelvic rotation panel div with chart container and metrics display
  - [ ] 4.5 Create trunk lean panel div with chart container and score display
  - [ ] 4.6 Add score cards section below panels (3 cards for 3 metrics)
  - [ ] 4.7 Include sit_to_stand.html template in index.html within a hidden div (shown when tab is active)

- [ ] 5.0 Implement lumbar lordosis visualization panel
  - [ ] 5.1 Read `static/js/charts.js` to understand existing Plotly chart patterns
  - [ ] 5.2 Create `static/js/sit-to-stand-charts.js` file
  - [ ] 5.3 Implement `renderLordosisChart(data)` function using Plotly
  - [ ] 5.4 Add time-series line chart showing lordosis angle over time
  - [ ] 5.5 Add red background shading for regions where angle > 0°
  - [ ] 5.6 Add green/amber background for target zone (≤0°)
  - [ ] 5.7 Display mean, max, min, SD statistics in panel
  - [ ] 5.8 Link sit-to-stand-charts.js in base.html

- [ ] 6.0 Implement pelvic rotation (hip hinge) panel
  - [ ] 6.1 Implement `renderHipHingeChart(data)` function in sit-to-stand-charts.js
  - [ ] 6.2 Create time-series chart for pelvic rotation angle progression
  - [ ] 6.3 Mark optimal rotation range (30-60°) with reference lines
  - [ ] 6.4 Display total pelvic rotation range metric
  - [ ] 6.5 Show hip hinge quality score (0-100)
  - [ ] 6.6 Use blue gradient color scheme for chart

- [ ] 7.0 Implement trunk forward lean panel
  - [ ] 7.1 Implement `renderTrunkLeanChart(data)` function in sit-to-stand-charts.js
  - [ ] 7.2 Create time-series chart for trunk lean angle over time
  - [ ] 7.3 Mark peak forward lean angle with annotation
  - [ ] 7.4 Display trunk lean timing information
  - [ ] 7.5 Show trunk lean strategy score
  - [ ] 7.6 Use orange gradient color scheme for chart

- [ ] 8.0 Add score cards with color-coded feedback
  - [ ] 8.1 Implement `renderScoreCards(scores)` function in sit-to-stand-charts.js
  - [ ] 8.2 Create 3 score card components (Lordosis, Hip Hinge, Trunk Lean)
  - [ ] 8.3 Implement color coding: green (80-100), yellow (60-79), red (<60)
  - [ ] 8.4 Add score value display with large readable numbers
  - [ ] 8.5 Add metric name labels and icons
  - [ ] 8.6 Style score cards with Tailwind CSS classes

- [ ] 9.0 Connect frontend to backend API
  - [ ] 9.1 Read `static/js/upload.js` to understand current API call handling
  - [ ] 9.2 Modify upload.js success callback to store both squat and sit-to-stand data
  - [ ] 9.3 Update `analysisData` global variable structure to hold both analyses
  - [ ] 9.4 Call sit-to-stand chart rendering functions when sit-to-stand tab is activated
  - [ ] 9.5 Ensure squat analysis tab continues to work with existing charts.js functions
  - [ ] 9.6 Add error handling for missing sit-to-stand data in API response

- [ ] 10.0 Testing and validation
  - [ ] 10.1 Test file upload with real CSV data
  - [ ] 10.2 Verify squat analysis tab shows correct existing functionality
  - [ ] 10.3 Verify sit-to-stand tab shows all three panels with charts
  - [ ] 10.4 Verify score cards display correct values with proper color coding
  - [ ] 10.5 Test tab switching functionality (no errors, smooth transitions)
  - [ ] 10.6 Verify lordosis angle highlights (red >0°, green ≤0°) work correctly
  - [ ] 10.7 Test with edge cases (very short movement, missing data points)
  - [ ] 10.8 Verify print functionality works for both tabs
