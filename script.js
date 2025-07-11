// Wait for DOM to load
$(document).ready(function () {
    // Initialize Select2
    $('#compound-select').select2({
        placeholder: 'Select Compound(s)',
        ajax: {
            url: '/api/compounds',
            dataType: 'json',
            delay: 250,
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
    });
});

function collectFilters() {
    return {
        compounds: $('#compound-select').val() || [],
        dtReasons: $('#dt-reason-select').val() || [],
        startDate: $('#start-date').val() || null,
        endDate: $('#end-date').val() || null,
        batchIds: $('#batch-id').val().split(',').map(s => s.trim()).filter(Boolean)
    };
}

function clearFilters() {
    $('#compound-select').val(null).trigger('change');
    $('#dt-reason-select').val(null).trigger('change');
    $('#start-date').val('');
    $('#end-date').val('');
    $('#batch-id').val('');
}

function populateSummaryTable(results) {
    const tbody = document.querySelector('#summary-table tbody');
    tbody.innerHTML = '';

    results.forEach(row => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td><input type="checkbox" class="row-checkbox"></td>
            <td>${row.compound}</td>
            <td>${row.batch_id}</td>
            <td>${row.date}</td>
            <td>${row.start_time}</td>
            <td>${row.end_time}</td>
            <td>${row.duration}</td>
        `;
        tbody.appendChild(tr);
    });
}