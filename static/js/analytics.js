
const analyticsCurrency = value =>
    new Intl.NumberFormat("en-IN", {
        style: "currency",
        currency: "INR",
        maximumFractionDigits: 2
    }).format(Number(value) || 0);

async function loadAnalytics() {
    const status = document.getElementById("analyticsStatus");
    status.textContent = "Loading analytics...";

    try {
        const response = await fetch("/api/analytics");

        if (!response.ok) {
            throw new Error("Unable to retrieve analytics.");
        }

        const data = await response.json();
        const summary = data.summary;

        document.getElementById("totalPolicies").textContent =
            summary.total_policies;

        document.getElementById("totalCategories").textContent =
            data.summary.total_categories;

        document.getElementById("averageMinPremium").textContent =
            analyticsCurrency(summary.average_min_premium);

        document.getElementById("averageMaxPremium").textContent =
            analyticsCurrency(summary.average_max_premium);

        document.getElementById("totalCoverage").textContent =
            analyticsCurrency(summary.total_coverage);

        document.getElementById("averageCoverage").textContent =
            analyticsCurrency(summary.average_coverage);

        const categories = data.categories;

        const commonLayout = {
            autosize: true,
            margin: { t: 20, r: 20, b: 60, l: 65 },
            paper_bgcolor: "white",
            plot_bgcolor: "white",
            font: { family: "Segoe UI, Arial, sans-serif" }
        };

        Plotly.react("categoryChart", [{
            type: "bar",
            x: categories.map(item => item.category),
            y: categories.map(item => item.policy_count),
            text: categories.map(item => item.policy_count),
            textposition: "auto",
            marker: { color: "#315fe8" }
        }], {
            ...commonLayout,
            yaxis: { title: "Number of policies", rangemode: "tozero" }
        }, { responsive: true });

        Plotly.react("premiumChart", [
            {
                type: "bar",
                name: "Average minimum",
                x: categories.map(item => item.category),
                y: categories.map(item => item.average_min_premium),
                marker: { color: "#315fe8" }
            },
            {
                type: "bar",
                name: "Average maximum",
                x: categories.map(item => item.category),
                y: categories.map(item => item.average_max_premium),
                marker: { color: "#80aaff" }
            }
        ], {
            ...commonLayout,
            barmode: "group",
            yaxis: { title: "Premium (INR)", rangemode: "tozero" },
            legend: { orientation: "h", y: -0.25 }
        }, { responsive: true });

        Plotly.react("coverageChart", [{
            type: "bar",
            x: categories.map(item => item.category),
            y: categories.map(item => item.total_coverage),
            marker: { color: "#159b83" }
        }], {
            ...commonLayout,
            yaxis: { title: "Total coverage (INR)", rangemode: "tozero" }
        }, { responsive: true });

        const tableBody = document.getElementById("topCoverageBody");
        tableBody.replaceChildren();

        if (data.top_coverage.length === 0) {
            const row = document.createElement("tr");
            const cell = document.createElement("td");
            cell.colSpan = 4;
            cell.textContent = "No policy records available.";
            row.appendChild(cell);
            tableBody.appendChild(row);
        } else {
            data.top_coverage.forEach(policy => {
                const row = document.createElement("tr");

                [
                    policy.policy_type_id,
                    policy.name,
                    policy.category,
                    analyticsCurrency(policy.coverage_amount)
                ].forEach(value => {
                    const cell = document.createElement("td");
                    cell.textContent = value;
                    row.appendChild(cell);
                });

                tableBody.appendChild(row);
            });
        }

        status.textContent = "Analytics updated successfully.";
    } catch (error) {
        console.error(error);
        status.textContent = error.message || "Failed to load analytics.";
    }
}

document.getElementById("refreshAnalytics")
    .addEventListener("click", loadAnalytics);

loadAnalytics();
