/**
 * Sit-to-Stand Analysis Chart Rendering
 * Uses Plotly.js for interactive visualizations
 */

/**
 * Main entry point for rendering all sit-to-stand analysis charts
 * @param {Object} data - Sit-to-stand analysis data from backend
 */
function renderSitToStandAnalysis(data) {
    // Check if Plotly is loaded
    if (typeof Plotly === 'undefined') {
        console.error('Plotly is not loaded yet. Retrying in 500ms...');
        setTimeout(() => renderSitToStandAnalysis(data), 500);
        return;
    }

    console.log('Rendering sit-to-stand charts with Plotly...', data);

    // Validate data structure
    if (!data) {
        console.error('No sit-to-stand data provided');
        return;
    }

    if (!data.lordosis_data || !data.pelvic_rotation_data || !data.trunk_lean_data || !data.scores) {
        console.error('Incomplete sit-to-stand data structure:', data);
        return;
    }

    try {
        // Render individual panels
        renderLordosisChart(data.lordosis_data);
        renderHipHingeChart(data.pelvic_rotation_data);
        renderTrunkLeanChart(data.trunk_lean_data);

        // Render score cards
        renderScoreCards(data.scores);

        console.log('All sit-to-stand charts rendered successfully');
    } catch (error) {
        console.error('Error rendering sit-to-stand charts:', error);
        if (typeof showError === 'function') {
            showError('앉았다 일어서기 차트 렌더링 중 오류가 발생했습니다: ' + error.message);
        }
    }
}

/**
 * Render lumbar lordosis angle chart with red/green background zones
 * @param {Object} data - Lordosis data { angles, time, stats }
 */
function renderLordosisChart(data) {
    if (!data || !data.time || !data.angles || !data.stats) {
        console.error('Invalid lordosis data:', data);
        return;
    }

    const trace = {
        x: data.time,
        y: data.angles,
        type: 'scatter',
        mode: 'lines',
        name: '요추전만 각도',
        line: { color: '#F59E0B', width: 2 }
    };

    // Create background shapes for regions where angle > 0 (red) and <= 0 (green)
    const shapes = [];
    let currentRegionType = null; // 'red' or 'green'
    let regionStart = null;

    for (let i = 0; i < data.angles.length; i++) {
        const value = data.angles[i];
        const time = data.time[i];
        const isOverZero = value > 0;

        if (i === 0) {
            // Start first region
            currentRegionType = isOverZero ? 'red' : 'green';
            regionStart = time;
        } else {
            const prevOverZero = data.angles[i - 1] > 0;

            // Check if region type changed
            if (isOverZero !== prevOverZero) {
                // End current region
                shapes.push({
                    type: 'rect',
                    xref: 'x',
                    yref: 'paper',
                    x0: regionStart,
                    x1: time,
                    y0: 0,
                    y1: 1,
                    fillcolor: currentRegionType === 'red'
                        ? 'rgba(239, 68, 68, 0.1)'
                        : 'rgba(16, 185, 129, 0.05)',
                    line: { width: 0 },
                    layer: 'below'
                });

                // Start new region
                currentRegionType = isOverZero ? 'red' : 'green';
                regionStart = time;
            }
        }
    }

    // Close last region
    if (regionStart !== null && data.time.length > 0) {
        shapes.push({
            type: 'rect',
            xref: 'x',
            yref: 'paper',
            x0: regionStart,
            x1: data.time[data.time.length - 1],
            y0: 0,
            y1: 1,
            fillcolor: currentRegionType === 'red'
                ? 'rgba(239, 68, 68, 0.1)'
                : 'rgba(16, 185, 129, 0.05)',
            line: { width: 0 },
            layer: 'below'
        });
    }

    // Add horizontal line at y=0 (target threshold)
    shapes.push({
        type: 'line',
        xref: 'paper',
        yref: 'y',
        x0: 0,
        x1: 1,
        y0: 0,
        y1: 0,
        line: {
            color: '#6B7280',
            width: 1,
            dash: 'dash'
        }
    });

    const layout = {
        xaxis: {
            title: 'Time (s)',
            showgrid: true,
            gridcolor: '#E5E7EB'
        },
        yaxis: {
            title: 'Lordosis Angle (degrees)',
            showgrid: true,
            gridcolor: '#E5E7EB'
        },
        shapes: shapes,
        margin: { l: 50, r: 30, t: 20, b: 50 },
        hovermode: 'x unified',
        showlegend: false,
        annotations: [
            {
                x: 1,
                y: 1.1,
                xref: 'paper',
                yref: 'paper',
                text: '<span style="color: #10B981;">■</span> 목표 범위 (≤0°)  <span style="color: #EF4444;">■</span> 주의 (>0°)',
                showarrow: false,
                xanchor: 'right',
                font: { size: 11 }
            }
        ]
    };

    const config = {
        responsive: true,
        displayModeBar: false
    };

    Plotly.newPlot('lordosisChart', [trace], layout, config);

    // Update statistics display
    document.getElementById('lordosis-mean').textContent = `${data.stats.mean}°`;
    document.getElementById('lordosis-max').textContent = `${data.stats.max}°`;
    document.getElementById('lordosis-min').textContent = `${data.stats.min}°`;
    document.getElementById('lordosis-std').textContent = `${data.stats.std}°`;
}

/**
 * Render pelvic rotation (hip hinge) chart with optimal range markers
 * @param {Object} data - Pelvic rotation data { angles, time, range, peak }
 */
function renderHipHingeChart(data) {
    if (!data || !data.time || !data.angles || !data.range || data.peak === undefined) {
        console.error('Invalid hip hinge data:', data);
        return;
    }

    const trace = {
        x: data.time,
        y: data.angles,
        type: 'scatter',
        mode: 'lines',
        name: '골반 회전',
        line: { color: '#3B82F6', width: 2 }
    };

    // Find y-axis range
    const minAngle = Math.min(...data.angles);
    const maxAngle = Math.max(...data.angles);
    const yPadding = (maxAngle - minAngle) * 0.1;

    const layout = {
        xaxis: {
            title: 'Time (s)',
            showgrid: true,
            gridcolor: '#E5E7EB'
        },
        yaxis: {
            title: 'Pelvic Rotation (degrees)',
            showgrid: true,
            gridcolor: '#E5E7EB',
            range: [minAngle - yPadding, maxAngle + yPadding]
        },
        shapes: [
            // Optimal range background (30-60°)
            {
                type: 'rect',
                xref: 'paper',
                yref: 'y',
                x0: 0,
                x1: 1,
                y0: 30,
                y1: 60,
                fillcolor: 'rgba(59, 130, 246, 0.1)',
                line: { width: 0 },
                layer: 'below'
            },
            // Lower bound line (30°)
            {
                type: 'line',
                xref: 'paper',
                yref: 'y',
                x0: 0,
                x1: 1,
                y0: 30,
                y1: 30,
                line: {
                    color: '#3B82F6',
                    width: 1,
                    dash: 'dash'
                }
            },
            // Upper bound line (60°)
            {
                type: 'line',
                xref: 'paper',
                yref: 'y',
                x0: 0,
                x1: 1,
                y0: 60,
                y1: 60,
                line: {
                    color: '#3B82F6',
                    width: 1,
                    dash: 'dash'
                }
            }
        ],
        margin: { l: 50, r: 30, t: 20, b: 50 },
        hovermode: 'x unified',
        showlegend: false,
        annotations: [
            {
                x: 1,
                y: 1.1,
                xref: 'paper',
                yref: 'paper',
                text: '최적 범위: 30-60°',
                showarrow: false,
                xanchor: 'right',
                font: { size: 11, color: '#3B82F6' }
            }
        ]
    };

    const config = {
        responsive: true,
        displayModeBar: false
    };

    Plotly.newPlot('hipHingeChart', [trace], layout, config);

    // Update statistics display
    document.getElementById('hip-range').textContent = `${data.range}°`;
    document.getElementById('hip-peak').textContent = `${data.peak}°`;
}

/**
 * Render trunk forward lean chart with peak annotation
 * @param {Object} data - Trunk lean data { angles, time, peak, peak_time }
 */
function renderTrunkLeanChart(data) {
    if (!data || !data.time || !data.angles || data.peak === undefined || data.peak_time === undefined) {
        console.error('Invalid trunk lean data:', data);
        return;
    }

    const trace = {
        x: data.time,
        y: data.angles,
        type: 'scatter',
        mode: 'lines',
        name: '체간 기울임',
        line: { color: '#F97316', width: 2 }
    };

    // Find y-axis range
    const minAngle = Math.min(...data.angles);
    const maxAngle = Math.max(...data.angles);
    const yPadding = (maxAngle - minAngle) * 0.1;

    const layout = {
        xaxis: {
            title: 'Time (s)',
            showgrid: true,
            gridcolor: '#E5E7EB'
        },
        yaxis: {
            title: 'Trunk Lean (degrees)',
            showgrid: true,
            gridcolor: '#E5E7EB',
            range: [minAngle - yPadding, maxAngle + yPadding]
        },
        shapes: [
            // Optimal range background (20-45°)
            {
                type: 'rect',
                xref: 'paper',
                yref: 'y',
                x0: 0,
                x1: 1,
                y0: 20,
                y1: 45,
                fillcolor: 'rgba(249, 115, 22, 0.1)',
                line: { width: 0 },
                layer: 'below'
            }
        ],
        margin: { l: 50, r: 30, t: 20, b: 50 },
        hovermode: 'x unified',
        showlegend: false,
        annotations: [
            {
                x: 1,
                y: 1.1,
                xref: 'paper',
                yref: 'paper',
                text: '최적 범위: 20-45°',
                showarrow: false,
                xanchor: 'right',
                font: { size: 11, color: '#F97316' }
            },
            // Peak marker
            {
                x: data.peak_time,
                y: data.peak,
                xref: 'x',
                yref: 'y',
                text: `최대: ${data.peak}°`,
                showarrow: true,
                arrowhead: 2,
                arrowsize: 1,
                arrowwidth: 2,
                arrowcolor: '#F97316',
                ax: 0,
                ay: -40,
                font: { size: 11, color: '#F97316' },
                bgcolor: 'white',
                bordercolor: '#F97316',
                borderwidth: 1,
                borderpad: 4
            }
        ]
    };

    const config = {
        responsive: true,
        displayModeBar: false
    };

    Plotly.newPlot('trunkLeanChart', [trace], layout, config);

    // Update statistics display
    document.getElementById('trunk-peak').textContent = `${data.peak}°`;
    document.getElementById('trunk-peak-time').textContent = `${data.peak_time}초`;
}

/**
 * Render score cards with color-coded feedback
 * @param {Object} scores - { lordosis, hip_hinge, trunk_lean }
 */
function renderScoreCards(scores) {
    if (!scores) {
        console.error('No scores data provided');
        return;
    }

    // Update lordosis score
    if (scores.lordosis !== undefined) {
        updateScoreCard('lordosis', scores.lordosis);
    }

    // Update hip hinge score
    if (scores.hip_hinge !== undefined) {
        updateScoreCard('hipHinge', scores.hip_hinge);
    }

    // Update trunk lean score
    if (scores.trunk_lean !== undefined) {
        updateScoreCard('trunkLean', scores.trunk_lean);
    }
}

/**
 * Update individual score card with color coding
 * @param {string} type - 'lordosis', 'hipHinge', or 'trunkLean'
 * @param {number} score - Score value (0-100)
 */
function updateScoreCard(type, score) {
    const scoreElement = document.getElementById(`${type}Score`);
    const cardElement = document.getElementById(`${type}ScoreCard`);

    if (!scoreElement || !cardElement) {
        console.warn(`Score card elements not found for ${type}`);
        return;
    }

    // Update score value
    scoreElement.textContent = score;

    // Determine color based on score
    let bgColor, textColor, borderColor;

    if (score >= 80) {
        // Green - Excellent
        bgColor = 'bg-green-50';
        textColor = 'text-green-600';
        borderColor = 'border-green-200';
    } else if (score >= 60) {
        // Yellow - Good
        bgColor = 'bg-yellow-50';
        textColor = 'text-yellow-600';
        borderColor = 'border-yellow-200';
    } else {
        // Red - Needs improvement
        bgColor = 'bg-red-50';
        textColor = 'text-red-600';
        borderColor = 'border-red-200';
    }

    // Remove old color classes
    cardElement.classList.remove(
        'bg-green-50', 'bg-yellow-50', 'bg-red-50',
        'border-green-200', 'border-yellow-200', 'border-red-200'
    );
    scoreElement.classList.remove(
        'text-green-600', 'text-yellow-600', 'text-red-600'
    );

    // Add new color classes
    cardElement.classList.add(bgColor, borderColor, 'border-2');
    scoreElement.classList.add(textColor);
}
