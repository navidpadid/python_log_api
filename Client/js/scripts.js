function isValidFilename(filename) {
    return /^[\w,\s-]+\.[A-Za-z]{3}$/.test(filename);
}

function isValidKeyword(keyword) {
    return /^[\w\s-]*$/.test(keyword);
}

async function fetchLogs() {
    const filename = document.getElementById('filename').value;
    const keyword = document.getElementById('keyword').value || '';
    let n = document.getElementById('n').value || 10000;
    const logContent = document.getElementById('logContent');
    logContent.innerHTML = ''; 

    if (!isValidFilename(filename)) {
        logContent.textContent = 'Error from UI: Invalid filename format';
        return;
    }

    if (!isValidKeyword(keyword)) {
        logContent.textContent = 'Error from UI: Invalid keyword format';
        return;
    }

    if (isNaN(n) || n <= 0) {
        logContent.textContent = 'Error from UI: Number of lines must be a valid number';
        return;
    }

    if (n > 100000) {
        logContent.textContent = 'WARN from UI: 100000 is the limit for the number of lines';
        n = 100000;
    }

    const url = `http://localhost:5000/${filename}?keyword=${keyword}&n=${n}`;
    try {
        const response = await fetch(url);

        if (!response.ok) {
            const errorData = await response.json();
            logContent.textContent = `Error: ${errorData.error}`;
            return;
        }

        const data = await response.json();
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
        logContent.textContent = `Error fetching logs: ${error.message}`;
    }
}
