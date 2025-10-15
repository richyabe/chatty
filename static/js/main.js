document.addEventListener("DOMContentLoaded", function() {
    setTimeout(function() {
        let alerts = document.querySelectorAll(".alert");
        alerts.forEach(function(alert) {
            alert.style.transition = "opacity 0.5s ease-out";
            alert.style.opacity = "0";
            setTimeout(() => alert.remove(), 500); // Remove after fade-out
        });
    }, 5000); // 5 seconds delay before removing
});
