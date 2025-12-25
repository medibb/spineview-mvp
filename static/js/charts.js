// Chart rendering with Plotly.js

function updateCharts(data) {
    // Check if Plotly is loaded
    if (typeof Plotly === 'undefined') {
        console.error('Plotly is not loaded yet. Retrying in 500ms...');
        setTimeout(() => updateCharts(data), 500);
        return;
    }

    console.log('updateCharts called with data:', data);
    console.log('Data keys:', Object.keys(data));
    console.log('time_series exists?', !!data.time_series);
    console.log('angular_velocity exists?', !!data.angular_velocity);
    console.log('acceleration exists?', !!data.acceleration);
    console.log('statistics exists?', !!data.statistics);

    if (!data.time_series) {
        console.error('ERROR: time_series is missing from data!');
        showError('차트 데이터 구조 오류: time_series가 없습니다.');
        return;
    }

    if (!data.time_series.time) {
        console.error('ERROR: time_series.time is missing!');
        showError('차트 데이터 구조 오류: time 배열이 없습니다.');
        return;
    }

    console.log('Rendering charts with Plotly...');
    console.log('Time array length:', data.time_series.time.length);

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
        name: '요추',
        line: { color: '#3B82F6', width: 2 }
    };

    const trace2 = {
        x: timeSeries.time,
        y: timeSeries.pelvis_fe,
        type: 'scatter',
        mode: 'lines',
        name: '골반',
        line: { color: '#10B981', width: 2 }
    };

    const trace3 = {
        x: timeSeries.time,
        y: timeSeries.relative_fe,
        type: 'scatter',
        mode: 'lines',
        name: '요추전만각도',
        line: { color: '#F59E0B', width: 2 }
    };

    // Create shapes for regions where relative_fe > 0 (red background)
    const shapes = [];
    let inRedRegion = false;
    let regionStart = null;

    for (let i = 0; i < timeSeries.relative_fe.length; i++) {
        const value = timeSeries.relative_fe[i];
        const time = timeSeries.time[i];

        if (value > 0 && !inRedRegion) {
            // Start of red region
            regionStart = time;
            inRedRegion = true;
        } else if (value <= 0 && inRedRegion) {
            // End of red region
            shapes.push({
                type: 'rect',
                xref: 'x',
                yref: 'paper',
                x0: regionStart,
                x1: time,
                y0: 0,
                y1: 1,
                fillcolor: 'rgba(239, 68, 68, 0.1)',
                line: { width: 0 },
                layer: 'below'
            });
            inRedRegion = false;
        }
    }

    // If still in red region at the end
    if (inRedRegion) {
        shapes.push({
            type: 'rect',
            xref: 'x',
            yref: 'paper',
            x0: regionStart,
            x1: timeSeries.time[timeSeries.time.length - 1],
            y0: 0,
            y1: 1,
            fillcolor: 'rgba(239, 68, 68, 0.1)',
            line: { width: 0 },
            layer: 'below'
        });
    }

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
        shapes: shapes,
        margin: { l: 50, r: 30, t: 30, b: 50 },
        hovermode: 'x unified',
        showlegend: true,
        legend: {
            orientation: 'h',
            yanchor: 'bottom',
            y: 1.02,
            xanchor: 'left',
            x: 0
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
    // Calculate unified x-axis range for spine and pelvis
    const spineEdges = distribution.spine.histogram.bin_edges;
    const pelvisEdges = distribution.pelvis.histogram.bin_edges;

    const spinePelvisMin = Math.min(
        Math.min(...spineEdges),
        Math.min(...pelvisEdges)
    );
    const spinePelvisMax = Math.max(
        Math.max(...spineEdges),
        Math.max(...pelvisEdges)
    );

    // Default to relative (요추전만) distribution
    renderDistributionForType('relative', distribution, spinePelvisMin, spinePelvisMax);

    // Setup selector
    const selector = document.getElementById('distributionSelector');
    selector.addEventListener('change', (e) => {
        renderDistributionForType(e.target.value, distribution, spinePelvisMin, spinePelvisMax);
    });
}

function renderDistributionForType(type, distribution, xMin, xMax) {
    const data = distribution[type];

    // For relative (요추전만), split data into two traces: normal and over zero
    let traces = [];

    if (type === 'relative') {
        // Find bins and create color-coded bars
        const binEdges = data.histogram.bin_edges;
        const counts = data.histogram.counts;

        // Calculate bin width for proper bar width
        const binWidth = binEdges.length > 1 ? binEdges[1] - binEdges[0] : 1;

        // Create all bin centers and colors
        const allX = [];
        const allY = [];
        const colors = [];

        for (let i = 0; i < counts.length; i++) {
            const binCenter = (binEdges[i] + binEdges[i + 1]) / 2;
            allX.push(binCenter);
            allY.push(counts[i]);

            // Color based on bin center position
            if (binCenter > 0) {
                colors.push('#EF4444'); // Red for over zero
            } else {
                colors.push('#F59E0B'); // Amber for normal range
            }
        }

        // Single trace with individual bar colors
        traces.push({
            x: allX,
            y: allY,
            type: 'bar',
            marker: {
                color: colors
            },
            width: binWidth * 0.9,
            showlegend: false
        });
    } else {
        // For spine and pelvis, use single trace
        const binEdges = data.histogram.bin_edges;
        const counts = data.histogram.counts;
        const binWidth = binEdges.length > 1 ? binEdges[1] - binEdges[0] : 1;

        const binCenters = [];
        for (let i = 0; i < counts.length; i++) {
            binCenters.push((binEdges[i] + binEdges[i + 1]) / 2);
        }

        traces = [{
            x: binCenters,
            y: counts,
            type: 'bar',
            name: 'Distribution',
            marker: {
                color: type === 'spine' ? '#3B82F6' : '#10B981'
            },
            width: binWidth * 0.9
        }];
    }

    // Determine x-axis range
    let xAxisRange;
    if (type === 'relative') {
        // For relative, calculate its own range from bin edges
        const relativeEdges = data.histogram.bin_edges;
        const relativeMin = Math.min(...relativeEdges);
        const relativeMax = Math.max(...relativeEdges);
        xAxisRange = [relativeMin, relativeMax];
    } else {
        // For spine and pelvis, use unified range
        xAxisRange = [xMin, xMax];
    }

    const layout = {
        xaxis: {
            title: 'Angle (degrees)',
            showgrid: true,
            gridcolor: '#E5E7EB',
            range: xAxisRange
        },
        yaxis: {
            title: 'Frequency',
            showgrid: true,
            gridcolor: '#E5E7EB'
        },
        margin: { l: 50, r: 30, t: 20, b: 50 },
        showlegend: false,
        barmode: 'overlay',
        annotations: type === 'relative' ? [
            {
                x: 1,
                y: 1.1,
                xref: 'paper',
                yref: 'paper',
                text: '<span style="color: #F59E0B;">■</span> 정상 범위  <span style="color: #EF4444;">■</span> 0도 초과 (주의)',
                showarrow: false,
                xanchor: 'right',
                font: { size: 11 }
            }
        ] : []
    };

    const config = {
        responsive: true,
        displayModeBar: false
    };

    Plotly.newPlot('distributionChart', traces, layout, config);

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
