document.addEventListener("DOMContentLoaded", () => {
    updateNavbarUser();

    const dateInput = document.getElementById("day-select");
    const form = document.querySelector("form");

    form.addEventListener("submit", async (event) => {
        event.preventDefault();
        const selectedDate = dateInput.value;

        if (!selectedDate) {
            alert("Please select a date.");
            return;
        }

        const user = JSON.parse(localStorage.getItem("loggedInUser"));
        if (!user) {
            alert("You must be logged in to view events.");
            return;
        }

        const response = await fetch(`http://localhost:8080/events/user?user_id=${user.id}&date=${selectedDate}`);
        const data = await response.json();

        if (data.events.length === 0) {
            alert("No events found for this day.");
        } else {
            displayEvents(data.events);
        }
    });
});
