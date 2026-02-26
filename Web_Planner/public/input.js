document.addEventListener("DOMContentLoaded", () => {
    fetchTypes();
    checkUserSession();
    enableSubmitButton();
});

// Fetch available types
async function fetchTypes() {
    try {
        const user = JSON.parse(localStorage.getItem("loggedInUser"));

        const response = await fetch("http://localhost:8080/data", {
            method: "GET",
            headers: { "User-ID": user ? user.id : "" },
            credentials: "include"
        });

        const data = await response.json();

        const typeSelect = document.getElementById("types");
        typeSelect.innerHTML = '<option value="">Select Type</option>';

        data.types.forEach(type => {
            const option = document.createElement("option");
            option.value = type.id;
            option.textContent = type.name;
            typeSelect.appendChild(option);
        });
    } catch (error) {
        console.error("Error fetching types:", error);
    }
}

// Submit an event
document.getElementById("submitEvent").addEventListener("click", async () => {
    const name = document.getElementById("eventName").value;
    const description = document.getElementById("eventDesc").value;
    const date = document.getElementById("eventDate").value;
    const time = document.getElementById("eventTime").value;
    const type_id = document.getElementById("types").value;

    const user = JSON.parse(localStorage.getItem("loggedInUser"));
    if (!user) {
        alert("You must be logged in to create an event.");
        return;
    }

    const response = await fetch("http://localhost:8080/events", {    // 👈 updated URL
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, description, date, time, type_id, user_id: user.id })
    });

    const data = await response.json();
    alert(data.message);

    document.getElementById("eventName").value = "";
    document.getElementById("eventDesc").value = "";
    document.getElementById("eventDate").value = "";
    document.getElementById("eventTime").value = "";
});

// Submit a type
document.getElementById("submitType").addEventListener("click", async () => {
    const name = document.getElementById("typeName").value;
    const color = document.getElementById("typeColor").value;
    const importance = document.getElementById("priority").value;

    if (!name || !color || !importance) {
        alert("All fields are required!");
        return;
    }

    const response = await fetch("http://localhost:8080/types", {     // 👈 updated URL
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, color, importance })
    });

    const data = await response.json();
    alert(data.message);

    document.getElementById("typeName").value = "";
    document.getElementById("typeColor").value = "#FFFFFF";
    document.getElementById("priority").value = "1";

    fetchTypes();
});
