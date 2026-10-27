
async function loadDashboardStats() {
    try {
        const response = await fetch("/api/policies");

        if (!response.ok) {
            throw new Error("Unable to load policy statistics.");
        }

        const policies = await response.json();

        const categories = new Set(
            policies.map(policy => policy.category)
        );

        const totalCoverage = policies.reduce(
            (sum, policy) => sum + Number(policy.coverage_amount),
            0
        );

        document.getElementById("totalPolicies").textContent =
            policies.length;

        document.getElementById("totalCategories").textContent =
            categories.size;

        document.getElementById("totalCoverage").textContent =
            new Intl.NumberFormat("en-IN", {
                style: "currency",
                currency: "INR",
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            }).format(totalCoverage);

    } catch (error) {
        console.error(error);

        document.getElementById("totalPolicies").textContent = "—";
        document.getElementById("totalCategories").textContent = "—";
        document.getElementById("totalCoverage").textContent = "—";
    }
}

loadDashboardStats();
