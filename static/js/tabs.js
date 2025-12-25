/**
 * Tab Switching Logic for Squat vs. Sit-to-Stand Analysis
 */

/**
 * Switch between analysis tabs
 * @param {string} tabName - 'squat' or 'sitToStand'
 */
function switchTab(tabName) {
    // Get tab buttons
    const squatTabBtn = document.getElementById('squatTab');
    const sitToStandTabBtn = document.getElementById('sitToStandTab');

    // Get content containers
    const squatContent = document.getElementById('squatContent');
    const sitToStandContent = document.getElementById('sitToStandContent');

    if (tabName === 'squat') {
        // Activate squat tab
        squatTabBtn.classList.remove('tab-inactive');
        squatTabBtn.classList.add('tab-active');
        sitToStandTabBtn.classList.remove('tab-active');
        sitToStandTabBtn.classList.add('tab-inactive');

        // Show squat content, hide sit-to-stand content
        squatContent.classList.remove('hidden');
        sitToStandContent.classList.add('hidden');

    } else if (tabName === 'sitToStand') {
        // Activate sit-to-stand tab
        sitToStandTabBtn.classList.remove('tab-inactive');
        sitToStandTabBtn.classList.add('tab-active');
        squatTabBtn.classList.remove('tab-active');
        squatTabBtn.classList.add('tab-inactive');

        // Show sit-to-stand content, hide squat content
        sitToStandContent.classList.remove('hidden');
        squatContent.classList.add('hidden');

        // Render sit-to-stand charts if data is available and not yet rendered
        if (window.analysisData && window.analysisData.sit_to_stand_analysis) {
            console.log('Attempting to render sit-to-stand analysis...', window.analysisData.sit_to_stand_analysis);

            // Check if already rendered to avoid re-rendering
            if (!window.sitToStandRendered) {
                if (typeof renderSitToStandAnalysis === 'function') {
                    renderSitToStandAnalysis(window.analysisData.sit_to_stand_analysis);
                    window.sitToStandRendered = true;
                } else {
                    console.error('renderSitToStandAnalysis function not found');
                }
            } else {
                console.log('Sit-to-stand charts already rendered');
            }
        } else {
            console.error('No sit-to-stand analysis data available:', window.analysisData);
        }
    }
}

/**
 * Show tab navigation after successful file upload
 */
function showTabNavigation() {
    const tabNav = document.getElementById('tabNavigation');
    if (tabNav) {
        tabNav.classList.remove('hidden');
    }

    // Default to squat tab
    switchTab('squat');
}

/**
 * Hide tab navigation (e.g., when clearing results)
 */
function hideTabNavigation() {
    const tabNav = document.getElementById('tabNavigation');
    if (tabNav) {
        tabNav.classList.add('hidden');
    }
}
