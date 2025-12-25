# Product Requirements Document: Sit-to-Stand Movement Analysis

## Introduction/Overview

This feature adds a second analysis mode to the PNUH Lumbo-Pelvic Movement Analysis Dashboard, specifically designed to analyze and provide feedback on sit-to-stand movements for patients with lower back pain. The primary goal is to help patients maintain proper lumbar lordosis (요추전만) during the transition from sitting to standing, preventing compensatory movement patterns that can exacerbate pain.

**Problem Statement**: Many lower back pain patients lose their neutral lumbar curve (lumbar lordosis collapses) when standing up from a seated position, leading to increased spinal load and pain. This feature provides objective measurement and visual feedback to help patients and clinicians identify and correct these movement patterns.

## Goals

1. **Provide separate tab-based interface** for sit-to-stand movement analysis
2. **Visualize lumbar lordosis maintenance** throughout the sit-to-stand motion (target: ≤0°)
3. **Quantify pelvic rotation (hip hinge)** usage during the movement
4. **Measure trunk forward lean** to assess movement strategy
5. **Provide clear, actionable feedback** through individual metric scores
6. **Integrate seamlessly** with existing squat analysis workflow via tab navigation

## User Stories

**As a physical therapist**, I want to:
- Switch between squat and sit-to-stand analysis tabs to analyze different movement patterns from the same patient
- Segment continuous data into individual sit-to-stand repetitions for detailed analysis
- See individual performance scores for each repetition so I can track patient progress over time
- Compare lumbar lordosis, pelvic rotation, and trunk lean metrics so I can identify specific movement faults

**As a patient with lower back pain**, I want to:
- See visual feedback on whether I maintained proper lumbar curve during standing so I know if I performed the movement correctly
- Understand which repetitions were performed well vs. poorly so I can recognize the correct movement pattern
- View simple metrics that show my improvement over therapy sessions

**As a researcher**, I want to:
- Access detailed biomechanical data for each phase of the sit-to-stand movement
- Export statistical summaries of multiple repetitions for analysis
- Compare movement patterns between different patient populations

## Functional Requirements

### FR1: Tab-Based Navigation
1.1. The system SHALL provide a tab interface with two distinct analysis modes: "스쿼트 분석" and "앉았다 일어서기 분석"
1.2. The system SHALL display both tabs as separate, clickable options after file upload
1.3. The system SHALL maintain independent analysis results for each tab
1.4. The system SHALL preserve the existing squat analysis functionality without modification in its tab
1.5. Users SHALL manually select which tab to view (no automatic switching)

### FR2: Movement Repetition Detection
2.1. The system SHALL segment continuous sit-to-stand data into individual repetitions based on acceleration patterns
2.2. The system SHALL display the number of detected sit-to-stand repetitions to the user
2.3. The system SHALL analyze each repetition independently
2.4. The system SHALL support 1-20 repetitions per upload session

### FR3: Lumbar Lordosis Visualization Panel
3.1. The system SHALL display a time-series chart of relative lumbar lordosis angle (spine-pelvis) throughout the movement
3.2. The system SHALL highlight regions where lordosis angle exceeds 0° with red background shading
3.3. The system SHALL mark the target zone (≤0°) with green/amber coloring
3.4. The system SHALL show lordosis angle for each detected repetition separately or as overlay
3.5. The system SHALL display mean, max, min, and standard deviation of lordosis angle per repetition

### FR4: Pelvic Rotation (Hip Hinge) Panel
4.1. The system SHALL calculate pelvic rotation angle from pelvis sensor quaternion data
4.2. The system SHALL visualize pelvic rotation angle over time during sit-to-stand
4.3. The system SHALL compute total pelvic rotation range (hip hinge utilization)
4.4. The system SHALL display a metric score for hip hinge quality (0-100 scale)
4.5. The system SHALL show reference ranges for optimal pelvic rotation

### FR5: Trunk Forward Lean Panel
5.1. The system SHALL calculate trunk forward lean angle from spine sensor quaternion data
5.2. The system SHALL visualize trunk lean angle progression throughout the movement
5.3. The system SHALL identify peak forward lean angle
5.4. The system SHALL display trunk lean timing relative to movement phases
5.5. The system SHALL compute a trunk lean strategy score

### FR6: Statistical Summary
6.1. The system SHALL provide per-repetition statistics including:
    - Lumbar lordosis score (% of movement ≤0°)
    - Hip hinge utilization score (pelvic rotation range)
    - Trunk lean score (optimal forward lean pattern)
6.2. The system SHALL calculate aggregate statistics across all repetitions
6.3. The system SHALL display confidence intervals or variability metrics
6.4. The system SHALL provide a Shapiro-Wilk normality test for each metric

### FR7: Feedback Mechanism
7.1. The system SHALL provide individual scores (0-100) for each metric per repetition:
    - Lordosis Maintenance Score
    - Hip Hinge Score
    - Trunk Lean Strategy Score
7.2. The system SHALL NOT provide binary pass/fail judgments
7.3. The system SHALL display scores in an easy-to-read dashboard format
7.4. The system SHALL color-code scores (green: 80-100, yellow: 60-79, red: <60) for quick interpretation

### FR8: Data Handling
8.1. The system SHALL accept the same Movella DOT CSV format as squat analysis
8.2. The system SHALL validate quaternion data quality before analysis
8.3. The system SHALL handle missing data points gracefully
8.4. The system SHALL support analysis of 1-20 repetitions per upload

## Non-Goals (Out of Scope)

1. **Real-time feedback during movement** - This version focuses on post-movement analysis only
2. **Custom threshold configuration** - Uses fixed 0° lordosis threshold (no user adjustment)
3. **Automatic movement type detection** - Users manually select squat vs. sit-to-stand tab
4. **Video integration** - No video upload or synchronization with sensor data
5. **Predictive modeling** - No injury risk prediction or progression forecasting
6. **Multi-session comparison** - No historical trend analysis across different dates
7. **Automated exercise prescription** - No treatment recommendations based on results

## Design Considerations

### UI/UX Requirements
- **Tab Navigation**: Add horizontal tab selector at top of analysis results area after file upload
  - Tab 1: "스쿼트 분석" (existing functionality)
  - Tab 2: "앉았다 일어서기 분석" (new functionality)
  - Both tabs process the same uploaded data differently
  - Users manually click tabs to switch between analysis types
- **Panel Layout**: Three-column grid for sit-to-stand analysis
  - Left: Lumbar Lordosis Panel
  - Center: Pelvic Rotation (Hip Hinge) Panel
  - Right: Trunk Forward Lean Panel
- **Score Cards**: Visual metric cards below panels showing individual scores
- **Color Scheme**:
  - Lumbar lordosis: Green (≤0°), Red (>0°)
  - Hip hinge: Blue gradient
  - Trunk lean: Orange gradient
- **Responsive Design**: Stack panels vertically on mobile devices

### Visual Components
- Time-series line charts with phase markers (sitting → transition → standing)
- Gauge charts or radial progress indicators for scores
- Statistical tables with min/mean/max/SD
- Motion phase annotations (seat-off, mid-rise, standing)

## Technical Considerations

### Data Processing
- **Repetition Segmentation Algorithm**:
  - Use acceleration magnitude threshold to detect movement onset/offset
  - Identify individual sit-to-stand cycles from continuous data
  - Mark seat-off point from pelvis vertical acceleration peak
  - No automatic movement type classification (user selects tab)
- **Angle Calculations**:
  - Lumbar lordosis: Same as squat analysis (spine FE - pelvis FE)
  - Pelvic rotation: Pitch angle from pelvis quaternion
  - Trunk lean: Pitch angle from spine quaternion (absolute, not relative)
- **Score Computation**:
  - Lordosis Score: `(frames_with_angle_≤0 / total_frames) × 100`
  - Hip Hinge Score: Normalize pelvic rotation range to 0-100 scale (30-60° optimal)
  - Trunk Lean Score: Based on smooth acceleration and optimal peak timing

### Integration Points
- Extend `dashboard/services/statistics.py` with sit-to-stand specific functions
- Modify existing `analyze_movement` view to return both squat and sit-to-stand analysis
- Add tab switching logic in frontend JavaScript
- Reuse existing Plotly.js chart infrastructure
- Add new JavaScript module `sit-to-stand-charts.js` for sit-to-stand visualizations
- Store both analysis results in single API response for tab switching

### Performance
- Process up to 20 repetitions without significant delay (<3 seconds)
- Maintain sub-second response for single repetition analysis
- Optimize quaternion-to-Euler conversions with NumPy vectorization

## Success Metrics

### Technical Success
1. **Accuracy**: Repetition segmentation accuracy >95% for detecting individual sit-to-stand cycles
2. **Performance**: Analysis completes in <3 seconds for 10 repetitions (both squat and sit-to-stand)
3. **Reliability**: Handle 100 consecutive uploads without errors
4. **Coverage**: Successfully process data from 50 different patients

### User Success
1. **Usability**: Therapists can interpret results without training (user testing)
2. **Clinical Utility**: Feedback leads to measurable improvement in patient technique (measured via pre/post score comparison)
3. **Adoption**: 80% of squat analysis users also utilize sit-to-stand analysis within 1 month

### Business Success
1. **Feature Usage**: Sit-to-stand analysis used on 40% of uploaded sessions
2. **Session Duration**: Average analysis session length increases by 30%
3. **User Satisfaction**: >4.5/5 rating for sit-to-stand feature (user survey)

## Open Questions

1. **Movement Phase Definition**: How should we algorithmically define "seat-off", "mid-rise", and "standing" phases? Use time percentiles or biomechanical markers?
2. **Multi-Rep Display**: Should we show all repetitions on one chart (overlaid) or use a carousel/grid view?
3. **Score Weighting**: Are all three scores (lordosis, hip hinge, trunk lean) equally important, or should we weight them differently in an overall score?
4. **Reference Data**: Do we have normative data for healthy sit-to-stand patterns to show comparison ranges?
5. **Export Format**: Should sit-to-stand results export separately from squat results, or combine into one report?
6. **Tab Persistence**: Should the selected tab (squat vs. sit-to-stand) persist when uploading new files, or reset to default?

## Implementation Phases

### Phase 1: Core Analysis Engine (Week 1-2)
- Implement repetition segmentation algorithm for sit-to-stand
- Add sit-to-stand specific angle calculations (lordosis, pelvic rotation, trunk lean)
- Create scoring functions for three metrics
- Extend backend API to return both squat and sit-to-stand analyses
- Write unit tests for core logic

### Phase 2: Tab Navigation & UI Structure (Week 3)
- Add tab navigation component to analysis results area
- Implement tab switching logic in JavaScript
- Create three-panel layout structure for sit-to-stand tab
- Ensure squat analysis tab remains unchanged

### Phase 3: Sit-to-Stand Visualizations (Week 4)
- Implement lordosis visualization panel with time-series chart
- Create pelvic rotation (hip hinge) panel with metrics
- Build trunk forward lean panel with scoring
- Add score cards with color-coded feedback

### Phase 4: Integration & Testing (Week 5)
- Connect sit-to-stand frontend to backend API
- Add error handling and data validation
- Implement print/export functionality for both tabs
- User acceptance testing with therapists

### Phase 5: Documentation & Deployment (Week 6)
- Write user guide for sit-to-stand analysis
- Update deployment documentation
- Deploy to Synology NAS (Docker)
- Conduct initial training session
