let loadedData = [];

/**
 * Validate an IP address.
 *
 * @param {string} ip - The IP address to validate.
 * @returns {boolean} - True if the IP address is valid, false otherwise.
 */
function isValidIP(ip) {
    const ipPattern = /^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;
    return ipPattern.test(ip);
}

/**
 * Validate a port number.
 *
 * @param {string} port - The port number to validate.
 * @returns {boolean} - True if the port number is valid, false otherwise.
 */
function isValidPort(port) {
    const portNumber = parseInt(port, 10);
    return portNumber >= 1 && portNumber <= 65535;
}

/**
 * Validate a filename.
 *
 * @param {string} filename - The filename to validate.
 * @returns {boolean} - True if the filename is valid, false otherwise.
 */
function isValidFilename(filename) {
    return /^[\w,\s-]+\.[A-Za-z]{3}$/.test(filename);
}

/**
 * Validate a keyword.
 *
 * @param {string} keyword - The keyword to validate.
 * @returns {boolean} - True if the keyword is valid, false otherwise.
 */
function isValidKeyword(keyword) {
    return /^[\w\s-]*$/.test(keyword);
}

/**
 * Fetch logs from the server and display them.
 *
 * @param {number} [page=1] - The page number to display.
 * @param {number} [pageSize=200] - The number of log entries per page.
 */
async function fetchLogs(page = 1, pageSize = 200) {
    const ip = document.getElementById('ip').value;
    const port = document.getElementById('port').value;
    const filename = document.getElementById('filename').value;
    const keyword = document.getElementById('keyword').value || '';
    let n = document.getElementById('n').value || 10000;
    const stream = document.getElementById('stream').value;
    const logContent = document.getElementById('logContent');
    const warnings = document.getElementById('warnings');
    logContent.innerHTML = ''; 
    warnings.innerHTML = '';

    if (!isValidIP(ip)) {
        warnings.textContent = 'Error from UI: Invalid IP address format';
        return;
    }

    if (!isValidPort(port)) {
        warnings.textContent = 'Error from UI: Invalid port number';
        return;
    }

    if (!isValidFilename(filename)) {
        warnings.textContent = 'Error from UI: Invalid filename format';
        return;
    }

    if (!isValidKeyword(keyword)) {
        warnings.textContent = 'Error from UI: Invalid keyword format';
        return;
    }

    if (isNaN(n) || n <= 0) {
        warnings.textContent = 'Error from UI: Number of lines must be a valid number';
        return;
    }

    if (n > 100000000) {
        warnings.textContent = 'WARN from UI: 100,000,000 is the limit for the number of lines';
        n = 100000000;
    }

    const url = `http://${ip}:${port}/${filename}?keyword=${keyword}&n=${n}&stream=${stream}`;
    try {
        const response = await fetch(url);

        if (!response.ok) {
            const errorData = await response.json();
            warnings.textContent = `Error: ${errorData.error}`;
            return;
        }

        const data = await response.text();
        loadedData = data.split('\n').filter(line => line.trim() !== '');
        displayLogs(page, pageSize);
    } catch (error) {
        console.error('Error fetching logs:', error);
        warnings.textContent = `Error fetching logs: ${error.message}`;
    }
}

/**
 * Display logs with pagination.
 *
 * @param {number} page - The page number to display.
 * @param {number} pageSize - The number of log entries per page.
 */
function displayLogs(page, pageSize) {
    const logContent = document.getElementById('logContent');
    logContent.innerHTML = ''; 

    const start = (page - 1) * pageSize;
    const end = start + pageSize;
    const paginatedLines = loadedData.slice(start, end);

    paginatedLines.forEach(line => {
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

    const paginationControls = document.createElement('div');
    paginationControls.classList.add('pagination-controls');

    const totalPages = Math.ceil(loadedData.length / pageSize);
    const maxPagesToShow = 5;
    let startPage = Math.max(1, page - Math.floor(maxPagesToShow / 2));
    let endPage = Math.min(totalPages, startPage + maxPagesToShow - 1);

    if (endPage - startPage < maxPagesToShow - 1) {
        startPage = Math.max(1, endPage - maxPagesToShow + 1);
    }

    if (startPage > 1) {
        const firstPageButton = document.createElement('button');
        firstPageButton.textContent = '1';
        firstPageButton.onclick = () => displayLogs(1, pageSize);
        firstPageButton.style.color = 'cyan';
        paginationControls.appendChild(firstPageButton);

        if (startPage > 2) {
            const dots = document.createElement('span');
            dots.textContent = '...';
            paginationControls.appendChild(dots);
        }
    }

    for (let i = startPage; i <= endPage; i++) {
        const pageButton = document.createElement('button');
        pageButton.textContent = i;
        pageButton.onclick = () => displayLogs(i, pageSize);
        if (i === page) {
            pageButton.style.backgroundColor = 'darkblue';
            pageButton.style.color = 'cyan';
            pageButton.classList.add('active');
        } else {
            pageButton.style.color = 'cyan';
        }
        paginationControls.appendChild(pageButton);
    }

    if (endPage < totalPages) {
        if (endPage < totalPages - 1) {
            const dots = document.createElement('span');
            dots.textContent = '...';
            paginationControls.appendChild(dots);
        }

        const lastPageButton = document.createElement('button');
        lastPageButton.textContent = totalPages;
        lastPageButton.onclick = () => displayLogs(totalPages, pageSize);
        lastPageButton.style.color = 'cyan';
        paginationControls.appendChild(lastPageButton);
    }

    const paginationWrapper = document.createElement('div');
    paginationWrapper.style.marginTop = '20px';
    paginationWrapper.appendChild(paginationControls);
    logContent.appendChild(paginationWrapper);
}
