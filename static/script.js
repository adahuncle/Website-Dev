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

    // Initialize DataTables for both summary and selection tables
    $('#summary-table').DataTable({
        autoWidth: false,
        order: [],
        pageLength: 50,
        lengthMenu: [ [10, 25, 50, -1], [10, 25, 50, "All"] ],
        columnDefs: [
        { targets: 1, visible: false },  // Hide ID column via JS
        { targets: [4], type: 'date' },
        { targets: [5, 6], type: 'string' }
        ],
        columns: [
            { width: "40px" },  // Checkbox
            null,               // ID (hidden)
            { width: "80px" }, // Compound
            { width: "120px" }, // Batch ID
            { width: "100px" },  // Date
            { width: "90px" },  // Start Time
            { width: "90px" },  // End Time
            { width: "80px" }   // Duration
        ]
    });

    $('#selection-table').DataTable({
        autoWidth: false,
        order: [],
        pageLength: 50,
        lengthMenu: [ [10, 25, 50, -1], [10, 25, 50, "All"] ],
        columnDefs: [
        { targets: 1, visible: false },  // Hide ID column via JS
        { targets: [4], type: 'date' },
        { targets: [5, 6], type: 'string' }
        ],
        columns: [
            { width: "40px" },  // Checkbox
            null,               // ID (hidden)
            { width: "80px" }, // Compound
            { width: "120px" }, // Batch ID
            { width: "100px" },  // Date
            { width: "110px" },  // Start Time
            { width: "110px" },  // End Time
            { width: "100px" }   // Duration
        ]
    });
});

function collectFilters() {
    return {
        compounds: $('#compound-select').val() || [],
        dt_reasons: $('#dt-reason-select').val() || [],
        start_date: $('#start-date').val() || null,
        end_date: $('#end-date').val() || null,
        batch: $('#batch').val().split(',').map(s => s.trim()).filter(Boolean)
    };
}

function clearFilters() {
    $('#compound-select').val(null).trigger('change');
    $('#dt-reason-select').val(null).trigger('change');
    $('#start-date').val('');
    $('#end-date').val('');
    $('#batch').val('');
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
    const table = $('#summary-table').DataTable();
    table.clear();

    results.forEach(row => {
        table.row.add([
            `<input type="checkbox" class="row-checkbox">`,
            row.id,
            row.program ?? '',
            row.batch ?? '',
            formatDate(row.date),
            formatTime(row.start_time),
            formatTime(row.end_time),
            row.duration ?? ''
        ]);
    });

    table.draw();

    }

function copyRows(sourceTableId, targetTableId) {
    const sourceTable = $(sourceTableId).DataTable();
    const targetTable = $(targetTableId).DataTable();

    const existingIds = new Set(
        targetTable.rows().data().toArray().map(row => row[1]) // assuming column 1 is the ID
    );

    const rowsToCopy = sourceTable.rows({ search: 'applied' }).nodes().toArray();

    rowsToCopy.forEach(row => {
        const checkbox = $(row).find('.row-checkbox');
        const rowData = sourceTable.row(row).data();
        const rowId = rowData[1]; // again, assuming column 1 is ID

        if (checkbox.is(':checked') && !existingIds.has(rowId)) {
            targetTable.row.add(rowData);
            existingIds.add(rowId); // prevent future duplication in same click
        }
    });

    targetTable.draw();
}


// Add selected from summary -> selection
document.querySelector("#add-selected").addEventListener("click", () => {
    copyRows("#summary-table", "#selection-table");
});

document.querySelector("#remove-selected").addEventListener("click", () => {
    const selectionTable = $('#selection-table').DataTable();

    // Get all rows that are checked
    selectionTable.rows({ search: 'applied' }).nodes().toArray().forEach(row => {
        const checkbox = $(row).find('.row-checkbox');
        if (checkbox.is(':checked')) {
            selectionTable.row(row).remove(); // just remove, no copy back
        }
    });

    selectionTable.draw(); // redraw after changes
});

// Clear all selected (remove all rows from selection table)
document.querySelector("#clear-selected").addEventListener("click", () => {
    const selectionTable = $('#selection-table').DataTable();
    selectionTable.clear().draw();
});

$('#select-all-summary').on('change', function () {
    const table = $('#summary-table').DataTable();
    const checked = $(this).prop('checked');

    table.rows({ search: 'applied' }).nodes().each(function (row) {
        $(row).find('.row-checkbox').prop('checked', checked);
    });
});

$('#summary-table tbody').on('change', '.row-checkbox', function () {
    const table = $('#summary-table').DataTable();
    const all = table.rows({ search: 'applied' }).nodes().to$().find('.row-checkbox');
    const allChecked = all.length > 0 && all.filter(':checked').length === all.length;
    $('#select-all-summary').prop('checked', allChecked);
});

$('#select-all-selection').on('change', function () {
    const table = $('#selection-table').DataTable();
    const checked = $(this).prop('checked');

    table.rows({ search: 'applied' }).nodes().each(function (row) {
        $(row).find('.row-checkbox').prop('checked', checked);
    });
});

$('#selection-table tbody').on('change', '.row-checkbox', function () {
    const table = $('#selection-table').DataTable();
    const all = table.rows({ search: 'applied' }).nodes().to$().find('.row-checkbox');
    const allChecked = all.length > 0 && all.filter(':checked').length === all.length;
    $('#select-all-selection').prop('checked', allChecked);
});

// Analyze selected rows
document.querySelector("#analyze-batches").addEventListener("click", () => {
    const selectionTable = $('#selection-table').DataTable();
    const rows = selectionTable.rows().data();  // This gives you all row data
    const selectedData = [];

    rows.each(function (rowData) {
        selectedData.push({
            id: rowData[1],
            program: rowData[2],
            batch: rowData[3],
            date: rowData[4],
            start_time: rowData[5],
            end_time: rowData[6],
            duration: rowData[7]
        });
    });

    fetch('/api/prepare-plot', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ batches: selectedData })
    })
    .then(res => res.json())
    .then(data => {
        if (data.plot_id) {
            window.open(`/plot/${data.plot_id}`, '_blank');
        } else {
            alert("Failed to prepare plot");
        }
    });
});
