// Chart rendering with Plotly.js

function updateCharts(data) {
    // Check if Plotly is loaded
    if (typeof Plotly === 'undefined') {
        console.error('Plotly is not loaded yet. Retrying in 500ms...');
        setTimeout(() => updateCharts(data), 500);
        return;
    }

    console.log('Rendering charts with Plotly...');
    renderMainTimeSeries(data.time_series);
    renderAngularVelocity(data.angular_velocity, data.time_series.time);
    renderAcceleration(data.acceleration, data.time_series.time);
    renderDistribution(data.statistics.distribution);
    renderAngleAnglePlot(data.time_series, data.statistics.coordination);
    console.log('All charts rendered successfully');
}

function renderMainTimeSeries(timeSeries) {
    const trace1 = {
        x: timeSeries.time,
        y: timeSeries.spine_fe,
        type: 'scatter',
        mode: 'lines',
        name: '척추 FE',
        line: { color: '#3B82F6', width: 2 }
    };

    const trace2 = {
        x: timeSeries.time,
        y: timeSeries.pelvis_fe,
        type: 'scatter',
        mode: 'lines',
        name: '골반 FE',
        line: { color: '#10B981', width: 2 }
    };

    const trace3 = {
        x: timeSeries.time,
        y: timeSeries.relative_fe,
        type: 'scatter',
        mode: 'lines',
        name: '상대 FE',
        line: { color: '#F59E0B', width: 2 }
    };

    const layout = {
        xaxis: {
            title: 'Time (s)',
            showgrid: true,
            gridcolor: '#E5E7EB'
        },
        yaxis: {
            title: 'Angle (degrees)',
            showgrid: true,
            gridcolor: '#E5E7EB'
        },
        margin: { l: 50, r: 30, t: 30, b: 50 },
        hovermode: 'x unified',
        showlegend: true,
        legend: {
            orientation: 'h',
            yanchor: 'bottom',
            y: 1.02,
            xanchor: 'right',
            x: 1
        }
    };

    const config = {
        responsive: true,
        displayModeBar: true,
        modeBarButtonsToRemove: ['select2d', 'lasso2d']
    };

    Plotly.newPlot('mainTimeSeriesChart', [trace1, trace2, trace3], layout, config);
}

function renderAngularVelocity(angularVelocity, time) {
    const spineData = angularVelocity.spine;

    const traces = [];

    if (spineData.gyr_x && spineData.gyr_x.length > 0) {
        traces.push({
            x: time,
            y: spineData.gyr_x,
            type: 'scatter',
            mode: 'lines',
            name: 'Gyr_X',
            line: { color: '#EF4444', width: 1.5 }
        });
    }

    if (spineData.gyr_y && spineData.gyr_y.length > 0) {
        traces.push({
            x: time,
            y: spineData.gyr_y,
            type: 'scatter',
            mode: 'lines',
            name: 'Gyr_Y (시상면)',
            line: { color: '#10B981', width: 2 }
        });
    }

    if (spineData.gyr_z && spineData.gyr_z.length > 0) {
        traces.push({
            x: time,
            y: spineData.gyr_z,
            type: 'scatter',
            mode: 'lines',
            name: 'Gyr_Z',
            line: { color: '#3B82F6', width: 1.5 }
        });
    }

    const layout = {
        xaxis: {
            title: 'Time (s)',
            showgrid: true,
            gridcolor: '#E5E7EB'
        },
        yaxis: {
            title: 'Angular Velocity (deg/s)',
            showgrid: true,
            gridcolor: '#E5E7EB'
        },
        margin: { l: 50, r: 30, t: 30, b: 50 },
        hovermode: 'x unified',
        showlegend: true,
        legend: { x: 1, xanchor: 'right', y: 1 }
    };

    const config = {
        responsive: true,
        displayModeBar: false
    };

    Plotly.newPlot('angularVelocityChart', traces, layout, config);
}

function renderAcceleration(acceleration, time) {
    const spineData = acceleration.spine;

    const traces = [];

    if (spineData.acc_x && spineData.acc_x.length > 0) {
        traces.push({
            x: time,
            y: spineData.acc_x,
            type: 'scatter',
            mode: 'lines',
            name: 'Acc_X',
            line: { color: '#EF4444', width: 1.5 }
        });
    }

    if (spineData.acc_y && spineData.acc_y.length > 0) {
        traces.push({
            x: time,
            y: spineData.acc_y,
            type: 'scatter',
            mode: 'lines',
            name: 'Acc_Y',
            line: { color: '#10B981', width: 1.5 }
        });
    }

    if (spineData.acc_z && spineData.acc_z.length > 0) {
        traces.push({
            x: time,
            y: spineData.acc_z,
            type: 'scatter',
            mode: 'lines',
            name: 'Acc_Z',
            line: { color: '#3B82F6', width: 1.5 }
        });
    }

    const layout = {
        xaxis: {
            title: 'Time (s)',
            showgrid: true,
            gridcolor: '#E5E7EB'
        },
        yaxis: {
            title: 'Acceleration (m/s²)',
            showgrid: true,
            gridcolor: '#E5E7EB'
        },
        margin: { l: 50, r: 30, t: 30, b: 50 },
        hovermode: 'x unified',
        showlegend: true,
        legend: { x: 1, xanchor: 'right', y: 1 }
    };

    const config = {
        responsive: true,
        displayModeBar: false
    };

    Plotly.newPlot('accelerationChart', traces, layout, config);
}

function renderDistribution(distribution) {
    // Default to spine distribution
    renderDistributionForType('spine', distribution);

    // Setup selector
    const selector = document.getElementById('distributionSelector');
    selector.addEventListener('change', (e) => {
        renderDistributionForType(e.target.value, distribution);
    });
}

function renderDistributionForType(type, distribution) {
    const data = distribution[type];

    const trace = {
        x: data.histogram.bin_edges,
        y: data.histogram.counts,
        type: 'bar',
        name: 'Distribution',
        marker: {
            color: type === 'spine' ? '#3B82F6' : (type === 'pelvis' ? '#10B981' : '#F59E0B')
        }
    };

    const layout = {
        xaxis: {
            title: 'Angle (degrees)',
            showgrid: true,
            gridcolor: '#E5E7EB'
        },
        yaxis: {
            title: 'Frequency',
            showgrid: true,
            gridcolor: '#E5E7EB'
        },
        margin: { l: 50, r: 30, t: 20, b: 50 },
        showlegend: false
    };

    const config = {
        responsive: true,
        displayModeBar: false
    };

    Plotly.newPlot('distributionChart', [trace], layout, config);

    // Update normality test info
    const normalityEl = document.getElementById('normalityTest');
    if (data.normality_test.p_value !== null) {
        const isNormal = data.normality_test.is_normal ? '정규분포' : '비정규분포';
        normalityEl.innerHTML = `
            <strong>Shapiro-Wilk 검정:</strong>
            p-value = ${data.normality_test.p_value}
            (${isNormal})
        `;
    } else {
        normalityEl.innerHTML = '<em>정규성 검정 불가</em>';
    }
}

function renderAngleAnglePlot(timeSeries, coordination) {
    const trace = {
        x: timeSeries.pelvis_fe,
        y: timeSeries.spine_fe,
        type: 'scatter',
        mode: 'markers',
        name: 'Data points',
        marker: {
            size: 4,
            color: timeSeries.time,
            colorscale: 'Viridis',
            showscale: false,
            opacity: 0.6
        }
    };

    // Regression line
    const regressionTrace = {
        x: coordination.regression_line.x,
        y: coordination.regression_line.y,
        type: 'scatter',
        mode: 'lines',
        name: 'Regression line',
        line: { color: '#EF4444', width: 2, dash: 'dash' }
    };

    const layout = {
        xaxis: {
            title: 'Pelvis FE (degrees)',
            showgrid: true,
            gridcolor: '#E5E7EB'
        },
        yaxis: {
            title: 'Spine FE (degrees)',
            showgrid: true,
            gridcolor: '#E5E7EB'
        },
        margin: { l: 50, r: 30, t: 20, b: 50 },
        showlegend: false
    };

    const config = {
        responsive: true,
        displayModeBar: false
    };

    Plotly.newPlot('angleAnglePlot', [trace, regressionTrace], layout, config);
}
