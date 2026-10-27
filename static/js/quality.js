
const statusElement = document.getElementById("qualityStatus");
const tableBody = document.getElementById("qualityTableBody");
const runButton = document.getElementById("runAudit");
const severityFilter = document.getElementById("severityFilter");
const issueSearch = document.getElementById("issueSearch");

let allIssues = [];

function addCell(row, value) {
    const cell = document.createElement("td");
    cell.textContent = value ?? "—";
    row.appendChild(cell);
    return cell;
}

function renderIssues() {
    const severity = severityFilter.value;
    const query = issueSearch.value.trim().toLowerCase();

    const filtered = allIssues.filter(issue => {
        const matchesSeverity =
            severity === "all" || issue.severity === severity;

        const searchable = [
            issue.policy_id,
            issue.policy_name,
            issue.field,
            issue.issue,
            issue.severity
        ].join(" ").toLowerCase();

        return matchesSeverity && searchable.includes(query);
    });

    tableBody.replaceChildren();

    if (!filtered.length) {
        const row = document.createElement("tr");
        const cell = addCell(row, "No matching quality issues found.");
        cell.colSpan = 5;
        tableBody.appendChild(row);
        return;
    }

    filtered.forEach(issue => {
        const row = document.createElement("tr");

        addCell(row, issue.policy_id);
        addCell(row, issue.policy_name);
        addCell(row, issue.field);
        addCell(row, issue.issue);
        addCell(row, issue.severity);

        tableBody.appendChild(row);
    });
}

async function runAudit() {
    runButton.disabled = true;
    statusElement.textContent = "Running data quality audit...";

    try {
        const response = await fetch("/api/quality", {
            cache: "no-store"
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || "Audit failed.");
        }

        document.getElementById("totalRecords").textContent =
            result.total_records;

        document.getElementById("cleanRecords").textContent =
            result.clean_records;

        document.getElementById("affectedRecords").textContent =
            result.affected_records;

        document.getElementById("issueCount").textContent =
            result.issue_count;

        document.getElementById("qualityScore").textContent =
            `${result.quality_score}%`;

        allIssues = result.issues || [];
        renderIssues();

        statusElement.textContent =
            `Audit complete. Found ${result.issue_count} issue(s) ` +
            `across ${result.affected_records} record(s).`;

    } catch (error) {
        statusElement.textContent = error.message;
    } finally {
        runButton.disabled = false;
    }
}

runButton.addEventListener("click", runAudit);
severityFilter.addEventListener("change", renderIssues);
issueSearch.addEventListener("input", renderIssues);

runAudit();
