$(document).ready(function () {
    let isCaptureRunning = false;
    let socket = null;
    let reconnectAttempts = 0;
    const maxReconnectAttempts = 5;
    let currentFolderPath = '';
    let currentIndex = 0;
    let isLastItem = false; // Biến để theo dõi xem có phải là item cuối cùng không

    // Hàm load danh sách folder paths (không thay đổi)
    function loadFolderPaths() {
        $.ajax({
            url: "/api/folder-paths/",
            type: "GET",
            success: function (response) {
                const select = $("#folder-path-select");
                select.empty();
                response.folder_paths.forEach(function (folderPath) {
                    select.append($('<option></option>').val(folderPath).text(folderPath));
                });
                if (response.folder_paths.length > 0) {
                    currentFolderPath = response.folder_paths[0];
                    loadMangoItem(currentFolderPath, 0);
                }
            },
            error: function (xhr, status, error) {
                console.error("Error loading folder paths:", error);
            }
        });
    }

    // Thêm hàm để hiển thị/ẩn overlay loading
    function toggleLoadingOverlay(show) {
        if (show) {
            $('body').append('<div id="loading-overlay" style="position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.5);display:flex;justify-content:center;align-items:center;z-index:9999;"><div>Connecting...</div></div>');
        } else {
            $('#loading-overlay').remove();
        }
    }

    // Hàm để enable/disable các nút điều hướng
    function toggleNavigationButtons(enable) {
        $("#next-button, #prev-button").prop('disabled', !enable);
    }

    // Hàm load mango item
    function loadMangoItem(folderPath, index) {
        $.ajax({
            url: `/api/mango-item-by-folder/?folder_path=${encodeURIComponent(folderPath)}&index=${index}`,
            type: "GET",
            success: function (response) {
                console.log("Full API Response:", response); // Log toàn bộ response để debug

                if (response && response.current_item) {
                    updateCurrentItem(response.current_item);
                } else {
                    console.error("Invalid response structure: missing current_item");
                }
                if (response && response.prediction_images) {
                    updatePredictionImages(response.prediction_images);
                } else {
                    console.error("Invalid response structure: missing prediction_images");
                }
                if (response && response.original_images) {
                    updateOriginalImages(response.original_images);
                } else {
                    console.error("Invalid response structure: missing original_images");
                }
                if (response && response.conclusion) {
                    updateConclusion(response.conclusion);
                } else {
                    console.error("Invalid response structure: missing conclusion");
                    // Gọi updateConclusion với dữ liệu mặc định khi không có dữ liệu
                    updateConclusion({
                        detected_areas: [],
                        total_disease_area: 0,
                        total_mango_surface_area: 0,
                        disease_area_percentage: 0,
                        conclusion: "No data available"
                    });
                }

                isLastItem = false;  // Không phải item cuối cùng, vì load thành công
                currentIndex = index;
                updateNavigationButtons();
            },
            error: function (xhr, status, error) {
                console.error("Error loading mango item:", error);
                console.log("XHR Status:", xhr.status);
                console.log("Full Response Text:", xhr.responseText);
                if (xhr.status === 404) {
                    alert("No more items in this folder.");
                    isLastItem = true;  // Đây là item cuối cùng
                }
                // Update UI to show error state
                updateConclusion({
                    detected_areas: [],
                    total_disease_area: 0,
                    total_mango_surface_area: 0,
                    disease_area_percentage: 0,
                    conclusion: "No data available"
                });
                updateNavigationButtons();  // Cập nhật trạng thái nút điều hướng
            }
        });
    }

    // Hàm cập nhật trạng thái nút điều hướng
    function updateNavigationButtons() {
        $("#prev-button").prop('disabled', currentIndex === 0);
        $("#next-button").prop('disabled', isLastItem);  // Disable nút Next nếu là item cuối cùng
    }

    // Hàm cập nhật trạng thái nút Capture
    function updateCaptureButton() {
        if (isCaptureRunning) {
            $("#capture-btn").html('<i class="icon-stop"></i> Stop');
            $("#capture-btn").removeClass("btn-success").addClass("btn-danger");
        } else {
            $("#capture-btn").html('<i class="icon-play"></i> Start');
            $("#capture-btn").removeClass("btn-danger").addClass("btn-success");
        }
    }

    // Cập nhật hàm connectWebSocket
    function connectWebSocket() {
        if (socket !== null && socket.readyState === WebSocket.OPEN) {
            console.log("WebSocket is already connected.");
            return true; // Kết nối đã tồn tại
        }

        toggleLoadingOverlay(true); // Hiển thị overlay loading
        toggleNavigationButtons(false); // Disable các nút điều hướng

        socket = new WebSocket('ws://localhost:8001');

        socket.onopen = function (e) {
            console.log("WebSocket connection established");
            reconnectAttempts = 0;
            isCaptureRunning = true;
            updateCaptureButton();
            toggleLoadingOverlay(false); // Ẩn overlay loading
        };

        socket.onmessage = function (event) {
            try {
                let messageData = JSON.parse(event.data);
                console.log("Message from server:", messageData);
                // Khi nhận được message, gọi API để lấy mango item mới nhất
                loadLatestMangoItem();
            } catch (e) {
                console.error("Error parsing message:", e);
            }
        };

        socket.onerror = function (error) {
            console.error("WebSocket error:", error);
            handleWebSocketFailure();
        };

        socket.onclose = function (e) {
            console.log("WebSocket connection closed");
            handleWebSocketFailure();
        };

        return false; // Kết nối mới được tạo
    }

    // Hàm để load mango item mới nhất
    function loadLatestMangoItem() {
        $.ajax({
            url: `/api/latest-mango-item/`, // Giả sử bạn có API endpoint này
            type: "GET",
            success: function (response) {
                console.log("Latest Mango Item:", response);
                if (response) {
                    updateCurrentItem(response.current_item);
                    updatePredictionImages(response.prediction_images);
                    updateOriginalImages(response.original_images);
                    updateConclusion(response.conclusion);
                }
            },
            error: function (xhr, status, error) {
                console.error("Error loading latest mango item:", error);
            }
        });
    }


    // Cập nhật hàm disconnectWebSocket
    function disconnectWebSocket() {
        if (socket !== null) {
            socket.close();
            socket = null;
            isCaptureRunning = false;
            updateCaptureButton();
            toggleNavigationButtons(true); // Enable các nút điều hướng khi ngừng capture
            console.log("WebSocket disconnected");
        }
    }

    // Cập nhật hàm handleWebSocketFailure
    function handleWebSocketFailure() {
        isCaptureRunning = false;
        updateCaptureButton();
        toggleLoadingOverlay(false); // Ẩn overlay loading
        toggleNavigationButtons(true); // Enable các nút điều hướng
        if (reconnectAttempts < maxReconnectAttempts) {
            reconnectAttempts++;
            setTimeout(connectWebSocket, 1000 * reconnectAttempts);
            console.log(`Trying to reconnect WebSocket... Attempt ${reconnectAttempts}`);
        } else {
            console.error("Max reconnect attempts reached.");
            alert("Unable to establish WebSocket connection. Please try again later.");
        }
    }

    // Event listener cho việc chọn folder
    $("#folder-path-select").change(function () {
        currentFolderPath = $(this).val();
        currentIndex = 0;
        isLastItem = false;  // Khi đổi folder, không biết có bao nhiêu item, nên reset isLastItem
        loadMangoItem(currentFolderPath, currentIndex);
    });

    // Event listener cho nút Next
    $("#next-button").click(function () {
        if (!isLastItem) {  // Chỉ load item tiếp theo nếu không phải là item cuối cùng
            loadMangoItem(currentFolderPath, currentIndex + 1);
        }
    });

    // Event listener cho nút Previous
    $("#prev-button").click(function () {
        if (currentIndex > 0) {
            currentIndex -= 1;
            isLastItem = false;  // Reset isLastItem khi đi lùi, vì có thể không còn ở item cuối
            loadMangoItem(currentFolderPath, currentIndex);
        }
    });

    // Cập nhật event listener cho nút Capture
    $("#capture-btn").on("click", function () {
        if (!isCaptureRunning) {
            connectWebSocket();
        } else {
            disconnectWebSocket();
        }
    });
    
    // Load folder paths khi trang được tải
    loadFolderPaths();
});