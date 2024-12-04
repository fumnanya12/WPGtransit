
function getLocation() {
    const status = document.getElementById("status");
    const coordinates = document.getElementById("coordinates");

    // Check if geolocation is supported
    if (!navigator.geolocation) {
        status.textContent = "Geolocation is not supported by your browser.";
        return;
    }

    status.textContent = "Locating...";

    // Use the geolocation API
    navigator.geolocation.getCurrentPosition(
        (position) => {
            const latitude = position.coords.latitude;
            const longitude = position.coords.longitude;
            const accuracy = position.coords.accuracy;
            
            status.textContent = "Location found!";
            //coordinates.textContent = `Latitude: ${latitude}, Longitude: ${longitude}`;

            // Send data to the backend
            fetch("/location", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ latitude, longitude }),
            })
                .then((response) => response.json())
                .then((data) => {
                    console.log("Response from server:", data);
                     // Reload the page after successfully storing the location
                    window.location.reload();
                     
                })
                .catch((error) => {
                    console.error("Error sending location data:", error);
                });
                console.log(`Latitude: ${latitude}, Longitude: ${longitude}, Accuracy: ${accuracy}`);

        }, 
        () => {
            status.textContent = "Unable to retrieve your location.";
        }
    );
}
function postStopNumber(stopNumber, stopName) {
    console.log("postStopNumber called with stopNumber:", stopNumber, "and stopName:", stopName);

    fetch("/get_schedule", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ stop_number: stopNumber, stop_name: stopName })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error("Failed to store stop data.");
        }
        return response.json();
    })
    .then(data => {
        console.log("Stop data stored successfully:", data);
        window.location.href = `/stop_schedule`; // Navigate to the schedule page
    })
    .catch(error => {
        console.error("Error storing stop data:", error);
    });
}
