// Wait for DOM to load
$(document).ready(function () {

    $('#compound-select').select2({
        placeholder: 'Select Compound(s)',
        ajax: {
            url: '/api/compounds',
            dataType: 'json',
            delay: 250,
            data: function (params) {
                return {
                    q: params.term
                };
            },
            processResults: data => ({
                results: data.map(item => ({ id: item, text: item }))
            })
        }
    });

    $('#dt-reason-select').select2({
        placeholder: 'Select Downtime Reason(s)',
        ajax: {
            url: '/api/dt-reason',
            dataType: 'json',
            delay: 250,
            data: function (params) {
                return {
                    q: params.term
                };
            },
            processResults: data => ({
                results: data.map(item => ({ id: item, text: item }))
            })
        }
    });

    // Handle Search Button Click
    $('.search-btn-mod button:contains("Search Database")').on('click', function () {
        const filters = collectFilters();

        // test line
        console.log("Collected filters:", filters);

        fetch('/api/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(filters)
        })
        .then(response => response.json())
        .then(data => {
            populateSummaryTable(data);
        })
        .catch(error => {
            console.error('Error during fetch:', error);
        });
    });

    // Handle Clear Filters Button
    $('.search-btn-mod button:contains("Clear Filters")').on('click', function () {
        clearFilters();

        // test line
        console.log("Cleared filters");
    });
});

function collectFilters() {
    return {
        compounds: $('#compound-select').val() || [],
        dt_reasons: $('#dt-reason-select').val() || [],
        start_date: $('#start-date').val() || null,
        end_date: $('#end-date').val() || null,
        batch_ids: $('#batch-id').val().split(',').map(s => s.trim()).filter(Boolean)
    };
}

function clearFilters() {
    $('#compound-select').val(null).trigger('change');
    $('#dt-reason-select').val(null).trigger('change');
    $('#start-date').val('');
    $('#end-date').val('');
    $('#batch-id').val('');
}

function formatDate(dateStr) {
    if (!dateStr) return '';
    const date = new Date(dateStr);
    return date.toLocaleDateString(); // Or customize format
}

function formatTime(timeStr) {
    if (!timeStr) return '';
    return timeStr.toString().split('.')[0]; // Remove milliseconds if present
}

function populateSummaryTable(results) {
    const tbody = document.querySelector('#summary-table tbody');
    tbody.innerHTML = ''; // Clear old content

    const fragment = document.createDocumentFragment(); // Create fragment

    results.forEach(row => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td><input type="checkbox" class="row-checkbox"></td>
            <td>${row.program ?? ''}</td>
            <td>${row.batch ?? ''}</td>
            <td>${formatDate(row.date)}</td>
            <td>${formatTime(row.start_time)}</td>
            <td>${formatTime(row.end_time)}</td>
            <td>${row.duration ?? ''}</td>
        `;
        fragment.appendChild(tr); // Append to fragment instead of DOM
    });

    tbody.appendChild(fragment); // Append all at once
}

function moveRows(sourceTable, targetTable) {
    const sourceTbody = document.querySelector(`${sourceTable} tbody`);
    const targetTbody = document.querySelector(`${targetTable} tbody`);

    const rows = sourceTbody.querySelectorAll('tr');
    rows.forEach(row => {
        const checkbox = row.querySelector('.row-checkbox');
        if (checkbox && checkbox.checked) {
            checkbox.checked = false;
            targetTbody.appendChild(row);
        }
    });
}

// Add selected from summary -> selection
document.querySelector("#add-selected").addEventListener("click", () => {
    moveRows("#summary-table", "#selection-table");
});

// Remove selected from selection -> summary
document.querySelector("#remove-selected").addEventListener("click", () => {
    moveRows("#selection-table", "#summary-table");
});

// Clear all selected (remove all rows from selection table)
document.querySelector("#clear-selected").addEventListener("click", () => {
    const selectionTbody = document.querySelector("#selection-table tbody");
    selectionTbody.innerHTML = '';
});

// Analyze selected rows
document.querySelector("#analyze-batches").addEventListener("click", () => {
    const rows = document.querySelectorAll("#selection-table tbody tr");
    const selectedData = [];

    rows.forEach(row => {
        const cells = row.querySelectorAll("td");
        selectedData.push({
            program: cells[1].textContent,
            batch_id: cells[2].textContent,
            date: cells[3].textContent,
            start_time: cells[4].textContent,
            end_time: cells[5].textContent,
            duration: cells[6].textContent
        });
    });

    console.log("Analyzing batches:", selectedData);
    // TODO: send to backend, generate plot, etc.
});

document.querySelector("#select-all-summary").addEventListener("change", function () {
    const checkboxes = document.querySelectorAll("#summary-table .row-checkbox");
    checkboxes.forEach(cb => cb.checked = this.checked);
});

document.querySelector("#select-all-selection").addEventListener("change", function () {
    const checkboxes = document.querySelectorAll("#selection-table .row-checkbox");
    checkboxes.forEach(cb => cb.checked = this.checked);
});
