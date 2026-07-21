document.addEventListener("DOMContentLoaded", function() {
    let alerts = document.querySelectorAll(".flash-message");
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.display = "none";
        }, 3000);
    });
});
