function isValidFilename(filename) {
    return /^[\w,\s-]+\.[A-Za-z]{3}$/.test(filename);
}

function isValidKeyword(keyword) {
    return /^[\w\s-]*$/.test(keyword);
}

async function fetchLogs(page = 1, pageSize = 200) {
    const filename = document.getElementById('filename').value;
    const keyword = document.getElementById('keyword').value || '';
    let n = document.getElementById('n').value || 10000;
    const stream = document.getElementById('stream').value;
    const logContent = document.getElementById('logContent');
    const warnings = document.getElementById('warnings');
    logContent.innerHTML = ''; 
    warnings.innerHTML = '';

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

    if (n > 100000) {
        warnings.textContent = 'WARN from UI: 100000 is the limit for the number of lines';
        n = 100000;
    }

    const url = `http://localhost:5000/${filename}?keyword=${keyword}&n=${n}&stream=${stream}`;
    try {
        const response = await fetch(url);

        if (!response.ok) {
            const errorData = await response.json();
            warnings.textContent = `Error: ${errorData.error}`;
            return;
        }

        const data = await response.json();
        const start = (page - 1) * pageSize;
        const end = start + pageSize;
        const paginatedLines = data.lines.slice(start, end);

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

        const totalPages = Math.ceil(data.lines.length / pageSize);
        const maxPagesToShow = 5;
        let startPage = Math.max(1, page - Math.floor(maxPagesToShow / 2));
        let endPage = Math.min(totalPages, startPage + maxPagesToShow - 1);

        if (endPage - startPage < maxPagesToShow - 1) {
            startPage = Math.max(1, endPage - maxPagesToShow + 1);
        }

        if (startPage > 1) {
            const firstPageButton = document.createElement('button');
            firstPageButton.textContent = '1';
            firstPageButton.onclick = () => fetchLogs(1, pageSize);
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
            pageButton.onclick = () => fetchLogs(i, pageSize);
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
            lastPageButton.onclick = () => fetchLogs(totalPages, pageSize);
            lastPageButton.style.color = 'cyan';
            paginationControls.appendChild(lastPageButton);
        }

        const paginationWrapper = document.createElement('div');
        paginationWrapper.style.marginTop = '20px';
        paginationWrapper.appendChild(paginationControls);
        logContent.appendChild(paginationWrapper);
    } catch (error) {
        console.error('Error fetching logs:', error);
        warnings.textContent = `Error fetching logs: ${error.message}`;
    }
}
