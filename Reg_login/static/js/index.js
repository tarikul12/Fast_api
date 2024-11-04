$(document).ready(function() {
    // Start scan when button is clicked
    $('#startScan').click(function() {
        const urlInput = $('#urlInput').val();
        if (!urlInput) {
            alert('Please enter a valid URL.');
            return;
        }

        // Send POST request to scan the website
        $.ajax({
            url: "http://127.0.0.1:8000/scan/",
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify({ url: urlInput }),
            success: function(data) {
                alert("Website scan completed successfully.");
                fetchHeadings();
            },
            error: function(jqXHR) {
                alert("Error: " + jqXHR.responseJSON.detail);
            }
        });
    });

    // Function to fetch headings from the API
    function fetchHeadings() {
        $.ajax({
            url: "http://127.0.0.1:8000/headings/",
            type: "GET",
            success: function(data) {
                const resultsBody = $("#resultsBody");
                resultsBody.empty(); // Clear previous results

                // Populate table with headings
                data.headings.forEach(heading => {
                    const row = `
                        <tr>
                            <td>${heading.url}</td>
                            <td>${heading.tag}</td>
                            <td>${heading.content}</td>
                        </tr>
                    `;
                    resultsBody.append(row);
                });
            },
            error: function() {
                console.error("Error fetching headings.");
            }
        });
    }
});
