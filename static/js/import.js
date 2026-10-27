
const form = document.getElementById("importForm");
const fileInput = document.getElementById("csvFile");
const statusElement = document.getElementById("importStatus");
const previewBody = document.getElementById("previewBody");
const importButton = document.getElementById("importButton");

let previewRows = [];

function escapeHTML(value) {
    return String(value ?? "").replace(/[&<>"']/g, character => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;"
    })[character]);
}

function showSummary(result) {
    document.getElementById("totalRows").textContent = result.total_rows;
    document.getElementById("validRows").textContent = result.valid_rows;
    document.getElementById("rejectedRows").textContent = result.rejected_rows;
}

function renderPreview(rows) {
    previewBody.replaceChildren();

    if (rows.length === 0) {
        previewBody.innerHTML =
            '<tr><td colspan="7">No data rows found.</td></tr>';
        return;
    }

    rows.forEach(row => {
        const data = row.data;
        const status = row.valid
            ? "Valid"
            : row.errors.join(" ");

        const values = [
            row.row_number,
            data.name,
            data.category,
            data.min_premium,
            data.max_premium,
            data.coverage_amount,
            status
        ];

        const tr = document.createElement("tr");

        values.forEach(value => {
            const td = document.createElement("td");
            td.textContent = value ?? "";
            tr.appendChild(td);
        });

        previewBody.appendChild(tr);
    });
}

form.addEventListener("submit", async event => {
    event.preventDefault();

    const file = fileInput.files[0];

    if (!file) {
        statusElement.textContent = "Please select a CSV file.";
        return;
    }

    const formData = new FormData();
    formData.append("file", file);

    statusElement.textContent = "Processing CSV...";
    importButton.disabled = true;
    previewRows = [];

    try {
        const response = await fetch("/api/import/preview", {
            method: "POST",
            body: formData
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || "Preview failed.");
        }

        previewRows = result.rows;
        showSummary(result);
        renderPreview(result.rows);

        importButton.disabled = result.valid_rows === 0;

        statusElement.textContent =
            `Preview complete: ${result.valid_rows} valid, ` +
            `${result.rejected_rows} rejected.`;

    } catch (error) {
        statusElement.textContent = error.message;
    }
});

importButton.addEventListener("click", async () => {
    const validRows = previewRows
        .filter(row => row.valid)
        .map(row => row.data);

    if (!validRows.length) {
        statusElement.textContent = "There are no valid rows to import.";
        return;
    }

    if (!confirm(`Import ${validRows.length} valid policies?`)) {
        return;
    }

    importButton.disabled = true;
    statusElement.textContent = "Importing policies...";

    try {
        const response = await fetch("/api/import/commit", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ rows: validRows })
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || "Import failed.");
        }

        statusElement.textContent =
            `Import finished: ${result.imported} imported, ` +
            `${result.rejected} rejected.`;

        // Reload the preview to reflect database changes.
        form.requestSubmit();

    } catch (error) {
        statusElement.textContent = error.message;
        importButton.disabled = false;
    }
});
