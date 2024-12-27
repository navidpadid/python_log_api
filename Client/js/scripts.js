async function fetchLogs() {
    const filename = document.getElementById('filename').value;
    const keyword = document.getElementById('keyword').value || '';
    const n = document.getElementById('n').value || 100;
    const url = `http://localhost:5000/${filename}?keyword=${keyword}&n=${n}`;
    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        const logContent = document.getElementById('logContent');
        logContent.innerHTML = '';

        data.lines.forEach(line => {
            const logLine = document.createElement('div');
            logLine.textContent = line;

            if (line.includes('INFO')) {
                logLine.classList.add('log-info');
            } else if (line.includes('ERROR')) {
                logLine.classList.add('log-error');
            } else if (line.includes('DEBUG')) {
                logLine.classList.add('log-debug');
            } else if (line.includes('WARN')) {
                logLine.classList.add('log-warn');
            }

            logContent.appendChild(logLine);
        });
    } catch (error) {
        console.error('Error fetching logs:', error);
        const logContent = document.getElementById('logContent');
        logContent.textContent = `Error fetching logs: ${error.message}`;
    }
}
