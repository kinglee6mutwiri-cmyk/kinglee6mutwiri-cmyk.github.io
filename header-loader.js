document.addEventListener("DOMContentLoaded", function () {
    const header = document.getElementById("shared-header");

    if (header) {
        fetch("header.html")
            .then(response => response.text())
            .then(data => {
                header.innerHTML = data;
            })
            .catch(error => console.error("Header loading error:", error));
    }
});

