// File upload handling

let spineFileData = null;
let pelvisFileData = null;

// Initialize upload handlers when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('Upload.js loaded and initializing...');
    setupDropZones();
    setupFormSubmit();
    console.log('Upload handlers set up successfully');
});

function setupDropZones() {
    // Spine file upload
    const spineDropZone = document.getElementById('spineDropZone');
    const spineFileInput = document.getElementById('spineFile');

    spineDropZone.addEventListener('click', () => spineFileInput.click());
    spineFileInput.addEventListener('change', (e) => handleFileSelect(e, 'spine'));

    // Drag and drop for spine
    spineDropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        spineDropZone.classList.add('drop-zone-active');
    });

    spineDropZone.addEventListener('dragleave', () => {
        spineDropZone.classList.remove('drop-zone-active');
    });

    spineDropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        spineDropZone.classList.remove('drop-zone-active');
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            spineFileInput.files = files;
            handleFileSelect({ target: spineFileInput }, 'spine');
        }
    });

    // Pelvis file upload
    const pelvisDropZone = document.getElementById('pelvisDropZone');
    const pelvisFileInput = document.getElementById('pelvisFile');

    pelvisDropZone.addEventListener('click', () => pelvisFileInput.click());
    pelvisFileInput.addEventListener('change', (e) => handleFileSelect(e, 'pelvis'));

    // Drag and drop for pelvis
    pelvisDropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        pelvisDropZone.classList.add('drop-zone-active');
    });

    pelvisDropZone.addEventListener('dragleave', () => {
        pelvisDropZone.classList.remove('drop-zone-active');
    });

    pelvisDropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        pelvisDropZone.classList.remove('drop-zone-active');
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            pelvisFileInput.files = files;
            handleFileSelect({ target: pelvisFileInput }, 'pelvis');
        }
    });
}

function handleFileSelect(event, fileType) {
    const file = event.target.files[0];
    if (!file) return;

    // Validate file extension
    if (!file.name.endsWith('.csv')) {
        showError('CSV 파일만 업로드 가능합니다.');
        return;
    }

    // Store file
    if (fileType === 'spine') {
        spineFileData = file;
        updateFileInfo('spine', file.name, null, null);
    } else {
        pelvisFileData = file;
        updateFileInfo('pelvis', file.name, null, null);
    }

    // Enable analyze button if both files are selected
    checkAnalyzeButton();
}

function updateFileInfo(fileType, filename, samples, duration) {
    const prefix = fileType === 'spine' ? 'spine' : 'pelvis';

    document.getElementById(`${prefix}FileContent`).classList.add('hidden');
    document.getElementById(`${prefix}FileInfo`).classList.remove('hidden');
    document.getElementById(`${prefix}FileName`).textContent = filename;

    if (samples !== null && duration !== null) {
        document.getElementById(`${prefix}Samples`).textContent = samples;
        document.getElementById(`${prefix}Duration`).textContent = duration;
    }
}

function checkAnalyzeButton() {
    const analyzeButton = document.getElementById('analyzeButton');
    if (spineFileData && pelvisFileData) {
        analyzeButton.disabled = false;
    } else {
        analyzeButton.disabled = true;
    }
}

function setupFormSubmit() {
    const form = document.getElementById('uploadForm');
    form.addEventListener('submit', async function(e) {
        e.preventDefault();

        if (!spineFileData || !pelvisFileData) {
            showError('척추와 골반 파일을 모두 업로드해주세요.');
            return;
        }

        // Show loading
        showLoading();

        // Create FormData
        const formData = new FormData();
        formData.append('spine_file', spineFileData);
        formData.append('pelvis_file', pelvisFileData);

        try {
            // Call analyze API
            const response = await fetch('/api/analyze/', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (data.status === 'success') {
                // Store analysis data globally
                window.analysisData = data.data;

                // Update UI
                hideLoading();
                showSuccess('분석이 완료되었습니다!');

                // Show results
                document.getElementById('analysisResults').classList.remove('hidden');

                // Update charts and statistics
                updateCharts(data.data);
                updateStatistics(data.data.statistics);
                updateFooter(data.data.metadata);

            } else {
                hideLoading();
                showError(data.message || '분석 중 오류가 발생했습니다.');
            }

        } catch (error) {
            hideLoading();
            showError('서버와 통신 중 오류가 발생했습니다: ' + error.message);
            console.error('Analysis error:', error);
        }
    });
}

function updateStatistics(stats) {
    // Update spine statistics
    document.getElementById('stat-spine-rom').textContent = stats.spine.rom + '°';
    document.getElementById('stat-spine-mean').textContent = stats.spine.mean + '°';
    document.getElementById('stat-spine-std').textContent = stats.spine.std + '°';
    document.getElementById('stat-spine-max').textContent = stats.spine.max + '°';
    document.getElementById('stat-spine-min').textContent = stats.spine.min + '°';

    if (stats.spine.peak_angular_velocity !== undefined) {
        document.getElementById('stat-spine-peak-vel').textContent =
            stats.spine.peak_angular_velocity + '°/s';
    }

    // Update pelvis statistics
    document.getElementById('stat-pelvis-rom').textContent = stats.pelvis.rom + '°';
    document.getElementById('stat-pelvis-mean').textContent = stats.pelvis.mean + '°';
    document.getElementById('stat-pelvis-std').textContent = stats.pelvis.std + '°';
    document.getElementById('stat-pelvis-max').textContent = stats.pelvis.max + '°';
    document.getElementById('stat-pelvis-min').textContent = stats.pelvis.min + '°';

    if (stats.pelvis.peak_angular_velocity !== undefined) {
        document.getElementById('stat-pelvis-peak-vel').textContent =
            stats.pelvis.peak_angular_velocity + '°/s';
    }

    // Update relative statistics
    document.getElementById('stat-relative-rom').textContent = stats.relative.rom + '°';
    document.getElementById('stat-relative-mean').textContent = stats.relative.mean + '°';
    document.getElementById('stat-relative-std').textContent = stats.relative.std + '°';
    document.getElementById('stat-relative-max').textContent = stats.relative.max + '°';
    document.getElementById('stat-relative-min').textContent = stats.relative.min + '°';

    document.getElementById('relative-rom-large').textContent = stats.relative.rom + '°';

    // Update coordination metrics
    if (stats.coordination) {
        document.getElementById('r-squared').textContent = stats.coordination.r_squared;
        document.getElementById('pearson-r').textContent = stats.coordination.pearson_r;
        document.getElementById('spine-contribution').textContent =
            (stats.coordination.contribution_ratio.spine * 100).toFixed(0) + '%';
        document.getElementById('pelvis-contribution').textContent =
            (stats.coordination.contribution_ratio.pelvis * 100).toFixed(0) + '%';
    }
}
