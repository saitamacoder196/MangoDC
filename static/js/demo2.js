$(document).ready(function() {
    let isCaptureRunning = false;
    let socket = null;
    let reconnectAttempts = 0;
    const maxReconnectAttempts = 5; // Giới hạn số lần kết nối lại

    // Hàm để kết nối tới WebSocket
    function connectWebSocket() {
        if (socket !== null && socket.readyState === WebSocket.OPEN) {
            console.log("WebSocket is already connected.");
            return; // Không kết nối lại nếu đã kết nối
        }

        // Cập nhật URL WebSocket tới ws://localhost:8001
        socket = new WebSocket('ws://localhost:8001');

        // Khi WebSocket mở kết nối
        socket.onopen = function(e) {
            console.log("WebSocket connection established");
            reconnectAttempts = 0; // Reset lại số lần thử kết nối lại sau khi thành công
        };

        // Khi nhận được tin nhắn từ server qua WebSocket
        socket.onmessage = function(event) {
            try {
                // Parse tin nhắn từ server để đảm bảo dữ liệu đúng
                let messageData = JSON.parse(event.data);
                console.log("Message from server:", messageData);
            } catch (e) {
                console.error("Error parsing message:", e);
            }
        };

        // Khi WebSocket gặp lỗi
        socket.onerror = function(error) {
            console.error("WebSocket error:", error);
            handleWebSocketFailure(); // Gọi hàm xử lý khi WebSocket gặp lỗi
        };

        // Khi WebSocket bị đóng
        socket.onclose = function(e) {
            console.log("WebSocket connection closed");
            handleWebSocketFailure(); // Gọi hàm xử lý khi WebSocket bị đóng

            if (isCaptureRunning && reconnectAttempts < maxReconnectAttempts) {
                // Thử kết nối lại nếu đang capture và bị ngắt kết nối
                reconnectAttempts++;
                setTimeout(connectWebSocket, 1000 * reconnectAttempts); // Tăng dần thời gian thử lại
                console.log(`Trying to reconnect WebSocket... Attempt ${reconnectAttempts}`);
            } else if (reconnectAttempts >= maxReconnectAttempts) {
                console.error("Max reconnect attempts reached.");
            }
        };
    }

    // Hàm xử lý khi WebSocket gặp lỗi hoặc bị đóng
    function handleWebSocketFailure() {
        if (isCaptureRunning) {
            // Đặt lại trạng thái nút
            $("#capture-btn").text("Capture");
            isCaptureRunning = false;

            // Hiển thị thông báo lỗi
            alert("WebSocket connection failed. Please try capturing again.");
        }
    }

    $("#capture-btn").on("click", function() {
        if (!isCaptureRunning) {
            // Nếu chưa chạy capture, gọi API capture trước khi kết nối WebSocket
            $.ajax({
                url: "/capture/", // URL để gọi API capture
                type: "GET",
                success: function(response) {
                    console.log(response.message);
                    // Đổi tên nút sang "Turn off"
                    $("#capture-btn").text("Turn off");
                    isCaptureRunning = true;

                    // Kết nối tới WebSocket sau khi API capture thành công
                    connectWebSocket();
                },
                error: function(xhr, status, error) {
                    console.error("Error occurred: " + error);
                    alert("Failed to start capture process. Please try again.");
                }
            });
        } else {
            // Nếu chương trình đang chạy, gọi API để tắt và đóng WebSocket
            $.ajax({
                url: "/turnoff/", // URL để gọi API tắt chương trình
                type: "GET",
                success: function(response) {
                    console.log(response.message);
                    // Đổi tên nút lại thành "Capture"
                    $("#capture-btn").text("Capture");
                    isCaptureRunning = false;

                    // Ngắt kết nối WebSocket sau khi API turnoff thành công
                    if (socket !== null) {
                        socket.close();
                        console.log("WebSocket connection manually closed");
                    }
                },
                error: function(xhr, status, error) {
                    console.error("Error occurred: " + error);
                    alert("Failed to stop capture process. Please try again.");
                }
            });
        }
    });
});