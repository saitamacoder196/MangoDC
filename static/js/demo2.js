$(document).ready(function() {
    let isCaptureRunning = false;

    $("#capture-btn").on("click", function() {
        if (!isCaptureRunning) {
            // Nếu chưa chạy capture, gọi API capture
            $.ajax({
                url: "/capture/", // URL để gọi API capture
                type: "GET",
                success: function(response) {
                    console.log(response.message);
                    // Đổi tên nút sang "Turn off"
                    $("#capture-btn").text("Turn off");
                    isCaptureRunning = true;
                },
                error: function(xhr, status, error) {
                    console.error("Error occurred: " + error);
                }
            });
        } else {
            // Nếu chương trình đang chạy, gọi API để tắt
            $.ajax({
                url: "/turnoff/", // URL để gọi API tắt chương trình
                type: "GET",
                success: function(response) {
                    console.log(response.message);
                    // Đổi tên nút lại thành "Capture"
                    $("#capture-btn").text("Capture");
                    isCaptureRunning = false;
                },
                error: function(xhr, status, error) {
                    console.error("Error occurred: " + error);
                }
            });
        }
    });
});
