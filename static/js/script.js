
const API = "/api/policies";
const categories = ["Motor", "Health", "Life", "Travel", "Home", "Other"];

const tableBody = document.getElementById("policyTableBody");
const dialog = document.getElementById("policyDialog");
const form = document.getElementById("policyForm");
const formError = document.getElementById("formError");
const statusMessage = document.getElementById("statusMessage");

let policies = [];

function money(value) {
    return new Intl.NumberFormat("en-IN", {
        style: "currency",
        currency: "INR",
        maximumFractionDigits: 2
    }).format(value);
}

function showStatus(message) {
    statusMessage.textContent = message;
}

async function apiRequest(url, options = {}) {
    const response = await fetch(url, {
        ...options,
        headers: {
            "Content-Type": "application/json",
            ...options.headers
        }
    });

    const result = await response.json().catch(() => ({}));

    if (!response.ok) {
        throw new Error(result.error || "The request failed.");
    }

    return result;
}


async function loadPolicies() {
    showStatus("Loading policies...");

    try {
        const categoryFilter = document.getElementById("categoryFilter");
        const category = categoryFilter ? categoryFilter.value : "";

        const url = category
            ? `${API}?category=${encodeURIComponent(category)}`
            : API;

        policies = await apiRequest(url);
        renderPolicies();
        updateStats();
        showStatus(`${policies.length} policy record(s) loaded.`);
    } catch (error) {
    console.error("Failed to load policies:", error);
    showStatus(error.message || "Unable to load policies.");

    if (tableBody) {
        tableBody.replaceChildren();
    }
}
}

function renderPolicies() {
    const searchInput = document.getElementById("searchInput");
    const query = searchInput
        ? searchInput.value.trim().toLowerCase()
        : "";

    if (!tableBody) {
        console.error(
            'Missing table body. Expected an element with id="policyTableBody".'
        );
        return;
    }

    const filtered = policies.filter(policy =>
        String(policy.policy_type_id).includes(query) ||
        String(policy.name || "").toLowerCase().includes(query)
    );

    tableBody.replaceChildren();

    if (filtered.length === 0) {
        const row = document.createElement("tr");
        const cell = document.createElement("td");
        cell.colSpan = 7;
        cell.textContent = "No policies found.";
        row.appendChild(cell);
        tableBody.appendChild(row);
        return;
    }

    filtered.forEach(policy => {
        const row = document.createElement("tr");

        const values = [
            policy.policy_type_id,
            policy.name,
            policy.category,
            money(policy.min_premium),
            money(policy.max_premium),
            money(policy.coverage_amount)
        ];

        values.forEach((value, index) => {
            const cell = document.createElement("td");

            if (index === 2) {
                const badge = document.createElement("span");
                badge.className = "badge";
                badge.textContent = value;
                cell.appendChild(badge);
            } else {
                cell.textContent = value;
            }

            row.appendChild(cell);
        });

        const actions = document.createElement("td");

        const editButton = document.createElement("button");
        editButton.className = "action-btn";
        editButton.textContent = "Edit";
        editButton.addEventListener("click", () => openEdit(policy));

        const deleteButton = document.createElement("button");
        deleteButton.className = "action-btn delete";
        deleteButton.textContent = "Delete";
        deleteButton.addEventListener("click", () => removePolicy(policy));

        actions.append(editButton, deleteButton);
        row.appendChild(actions);
        tableBody.appendChild(row);
    });
}


function updateStats() {
    const totalPoliciesEl = document.getElementById("totalPolicies");
    const totalCategoriesEl = document.getElementById("totalCategories");
    const totalCoverageEl = document.getElementById("totalCoverage");

    const allCategories = new Set(
        policies.map(policy => policy.category)
    );

    const coverage = policies.reduce(
        (total, policy) => total + Number(policy.coverage_amount || 0),
        0
    );

    if (totalPoliciesEl) {
        totalPoliciesEl.textContent = policies.length;
    }

    if (totalCategoriesEl) {
        totalCategoriesEl.textContent = allCategories.size;
    }

    if (totalCoverageEl) {
        totalCoverageEl.textContent = money(coverage);
    }
}


function openCreate() {
    form.reset();
    document.getElementById("policyId").value = "";
    document.getElementById("dialogTitle").textContent = "Add Policy";
    document.getElementById("saveBtn").textContent = "Save Policy";
    formError.textContent = "";
    dialog.showModal();
}

function openEdit(policy) {
    form.reset();
    document.getElementById("policyId").value = policy.policy_type_id;
    document.getElementById("name").value = policy.name;
    document.getElementById("category").value = policy.category;
    document.getElementById("minPremium").value = policy.min_premium;
    document.getElementById("maxPremium").value = policy.max_premium;
    document.getElementById("coverage").value = policy.coverage_amount;
    document.getElementById("dialogTitle").textContent = "Edit Policy";
    document.getElementById("saveBtn").textContent = "Update Policy";
    formError.textContent = "";
    dialog.showModal();
}

form.addEventListener("submit", async event => {
    event.preventDefault();
    formError.textContent = "";

    const id = document.getElementById("policyId").value;
    const payload = {
        name: document.getElementById("name").value.trim(),
        category: document.getElementById("category").value,
        min_premium: Number(document.getElementById("minPremium").value),
        max_premium: Number(document.getElementById("maxPremium").value),
        coverage_amount: Number(document.getElementById("coverage").value)
    };

    if (!payload.name) {
        formError.textContent = "Policy name cannot be empty.";
        return;
    }

    if (!categories.includes(payload.category)) {
        formError.textContent = "Select a valid category.";
        return;
    }

    if (
        !Number.isFinite(payload.min_premium) ||
        !Number.isFinite(payload.max_premium) ||
        !Number.isFinite(payload.coverage_amount) ||
        payload.min_premium <= 0 ||
        payload.max_premium <= payload.min_premium ||
        payload.coverage_amount < payload.max_premium
    ) {
        formError.textContent =
            "Enter positive amounts, minimum premium below maximum, " +
            "and coverage at least equal to maximum premium.";
        return;
    }

    try {
        await apiRequest(
            id ? `${API}/${id}` : API,
            {
                method: id ? "PUT" : "POST",
                body: JSON.stringify(payload)
            }
        );

        dialog.close();
        await loadPolicies();
        showStatus(id ? "Policy updated successfully." :
            "Policy created successfully.");
    } catch (error) {
        formError.textContent = error.message;
    }
});

async function removePolicy(policy) {
    const confirmed = window.confirm(
        `Delete "${policy.name}" (Policy ID ${policy.policy_type_id})?`
    );

    if (!confirmed) return;

    try {
        await apiRequest(`${API}/${policy.policy_type_id}`, {
            method: "DELETE"
        });

        await loadPolicies();
        showStatus(`Policy ID ${policy.policy_type_id} deleted successfully.`);
    } catch (error) {
        showStatus(error.message);
    }
}


const addPolicyBtn = document.getElementById("addPolicyBtn");
const searchInput = document.getElementById("searchInput");
const categoryFilter = document.getElementById("categoryFilter");
const refreshBtn = document.getElementById("refreshBtn");
const closeDialogBtn = document.getElementById("closeDialogBtn");
const cancelBtn = document.getElementById("cancelBtn");

if (addPolicyBtn) {
    addPolicyBtn.addEventListener("click", openCreate);
}

if (searchInput) {
    searchInput.addEventListener("input", renderPolicies);
}

if (categoryFilter) {
    categoryFilter.addEventListener("change", loadPolicies);
}

if (refreshBtn) {
    refreshBtn.addEventListener("click", loadPolicies);
}

if (closeDialogBtn) {
    closeDialogBtn.addEventListener("click", () => dialog.close());
}

if (cancelBtn) {
    cancelBtn.addEventListener("click", () => dialog.close());
}



async function initializePoliciesPage() {
    await loadPolicies();

    const params = new URLSearchParams(window.location.search);

    if (params.get("create") === "1") {
        openCreate();
    }

    if (params.get("delete") === "1") {
        showStatus("Select the policy you want to delete.");
        document.getElementById("policies")?.scrollIntoView({
            behavior: "smooth"
        });
    }
}

initializePoliciesPage();

