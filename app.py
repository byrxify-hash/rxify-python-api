<?php
ini_set('display_errors', 1);
error_reporting(E_ALL);

$search = isset($_GET['q']) ? trim($_GET['q']) : '';
$apiUrl = "https://rxify-python-api.onrender.com/medicines" . ($search !== '' ? "?q=" . urlencode($search) : "");

$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, $apiUrl);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_TIMEOUT, 50);
curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
$response = curl_exec($ch);
curl_close($ch);

$medicines = ($response !== false) ? json_decode($response, true) : [];
if (!is_array($medicines)) {
    $medicines = [];
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Medicine Directory</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 20px; }
        .container { max-width: 1200px; margin: auto; background: rgba(30, 41, 59, 0.6); padding: 25px; border-radius: 16px; backdrop-filter: blur(12px); border: 1px solid rgba(255,255,255,0.05); box-shadow: 0 10px 30px rgba(0,0,0,0.3); }
        
        /* Search Bar */
        .search-wrapper { display: flex; gap: 10px; margin-bottom: 20px; }
        input[type="text"] { flex-grow: 1; padding: 12px 15px; border-radius: 8px; border: 1px solid #475569; background: rgba(15, 23, 42, 0.6); color: #fff; outline: none; font-size: 16px; transition: 0.3s; }
        input[type="text"]:focus { border-color: #3b82f6; background: rgba(15, 23, 42, 0.8); }
        button[type="submit"] { padding: 12px 24px; border-radius: 8px; border: none; background: #3b82f6; color: #fff; cursor: pointer; font-weight: bold; font-size: 16px; transition: 0.3s; }
        button[type="submit"]:hover { background: #2563eb; }
        
        /* Table Styling */
        .table-responsive { overflow-x: auto; border-radius: 8px; border: 1px solid rgba(255,255,255,0.05); }
        table { width: 100%; border-collapse: collapse; min-width: 800px; }
        th, td { padding: 14px 16px; text-align: left; border-bottom: 1px solid rgba(255,255,255,0.05); white-space: nowrap; }
        th { background: rgba(15, 23, 42, 0.8); font-weight: 600; color: #94a3b8; text-transform: uppercase; font-size: 0.85em; letter-spacing: 0.5px; }
        tr:hover td { background: rgba(255,255,255,0.02); }
        
        /* View Button */
        .view-btn { background: #10b981; color: white; padding: 8px 16px; border-radius: 6px; border: none; font-size: 0.9em; cursor: pointer; font-weight: bold; transition: 0.3s; box-shadow: 0 4px 6px rgba(16, 185, 129, 0.2); }
        .view-btn:hover { background: #059669; transform: translateY(-1px); }

        /* Upgraded Premium Modal */
        .modal { display: none; position: fixed; z-index: 1000; left: 0; top: 0; width: 100%; height: 100%; overflow: auto; background-color: rgba(15, 23, 42, 0.7); backdrop-filter: blur(6px); }
        .modal-content { 
            background: rgba(30, 41, 59, 0.85); 
            backdrop-filter: blur(16px);
            margin: 5% auto; 
            padding: 30px; 
            border: 1px solid rgba(255, 255, 255, 0.1); 
            width: 90%; 
            max-width: 700px; 
            border-radius: 16px; 
            box-shadow: 0 20px 40px rgba(0,0,0,0.5); 
        }
        .modal-header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 15px; margin-bottom: 20px; }
        .modal-header h3 { margin: 0; color: #fff; font-size: 1.6em; }
        .close { color: #94a3b8; font-size: 28px; font-weight: bold; cursor: pointer; transition: 0.3s; }
        .close:hover { color: #ef4444; }
        
        /* Grid Layout for Details */
        .detail-grid { display: grid; grid-template-columns: 1fr; gap: 15px; }
        @media (min-width: 600px) { .detail-grid { grid-template-columns: 1fr 1fr; } }
        .detail-item { background: rgba(15, 23, 42, 0.5); padding: 15px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.03); }
        .detail-item span.label { display: block; font-size: 0.8em; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px; }
        .detail-item span.value { display: block; color: #f8fafc; font-size: 1.05em; word-break: break-word; line-height: 1.4; }

        /* Action Buttons in Modal */
        .modal-actions { margin-top: 25px; display: flex; gap: 12px; justify-content: flex-end; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 20px; }
        .btn-whatsapp { background: #25D366; color: white; padding: 10px 20px; border-radius: 8px; text-decoration: none; font-weight: bold; border: none; cursor: pointer; transition: 0.3s; display: flex; align-items: center; gap: 8px; }
        .btn-whatsapp:hover { background: #1ebe5d; transform: translateY(-1px); }
        .btn-close { background: #475569; color: white; padding: 10px 20px; border-radius: 8px; border: none; cursor: pointer; font-weight: bold; transition: 0.3s; }
        .btn-close:hover { background: #334155; }
    </style>
</head>
<body>
    <div class="container">
        <h2>Global Medicine Directory</h2>
        <form method="GET" action="" class="search-wrapper">
            <input type="text" name="q" placeholder="Search by brand or generic name..." value="<?php echo htmlspecialchars($search); ?>">
            <button type="submit">Search</button>
        </form>

        <div class="table-responsive">
            <table>
                <thead>
                    <tr>
                        <th>Action</th>
                        <?php if (!empty($medicines) && isset($medicines[0]) && is_array($medicines[0])): ?>
                            <?php foreach (array_keys($medicines[0]) as $col): ?>
                                <th><?php echo htmlspecialchars($col); ?></th>
                            <?php endforeach; ?>
                        <?php else: ?>
                            <th>Results</th>
                        <?php endif; ?>
                    </tr>
                </thead>
                <tbody>
                    <?php if (!empty($medicines)): ?>
                        <?php foreach ($medicines as $row): ?>
                            <tr>
                                <?php $jsonData = htmlspecialchars(json_encode($row), ENT_QUOTES, 'UTF-8'); ?>
                                <td><button class="view-btn" onclick="openModal(<?php echo $jsonData; ?>)">View</button></td>
                                
                                <?php if (is_array($row)): ?>
                                    <?php foreach ($row as $val): ?>
                                        <td><?php echo htmlspecialchars(strlen((string)$val) > 40 ? substr((string)$val, 0, 40) . '...' : (string)$val); ?></td>
                                    <?php endforeach; ?>
                                <?php else: ?>
                                    <td><?php echo htmlspecialchars($row); ?></td>
                                <?php endif; ?>
                            </tr>
                        <?php endforeach; ?>
                    <?php else: ?>
                        <tr><td colspan="100%">No records found. Please check your search or wait for the API to load.</td></tr>
                    <?php endif; ?>
                </tbody>
            </table>
        </div>
    </div>

    <!-- Enhanced Modal -->
    <div id="medicineModal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <h3 id="modalTitle">Medicine Details</h3>
                <span class="close" onclick="closeModal()">&times;</span>
            </div>
            <div id="detailGrid" class="detail-grid">
                <!-- Details injected via JS -->
            </div>
            <div class="modal-actions">
                <button class="btn-close" onclick="closeModal()">Close</button>
                <button class="btn-whatsapp" onclick="shareToWhatsApp()">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16"><path d="M13.601 2.326A7.85 7.85 0 0 0 7.994 0C3.627 0 .068 3.558.064 7.926c0 1.399.366 2.76 1.057 3.965L0 16l4.204-1.102a7.9 7.9 0 0 0 3.79.965h.004c4.368 0 7.926-3.558 7.93-7.93A7.9 7.9 0 0 0 13.6 2.326zM7.994 14.521a6.6 6.6 0 0 1-3.356-.92l-.24-.144-2.494.654.666-2.433-.156-.251a6.56 6.56 0 0 1-1.007-3.505c0-3.626 2.957-6.584 6.591-6.584a6.56 6.56 0 0 1 4.66 1.931 6.56 6.56 0 0 1 1.928 4.66c-.004 3.639-2.961 6.592-6.592 6.592m3.615-4.934c-.197-.099-1.17-.578-1.353-.646-.182-.065-.315-.099-.445.099-.133.197-.513.646-.627.775-.114.133-.232.148-.43.05-.197-.1-.836-.308-1.592-.985-.59-.525-.985-1.175-1.103-1.372-.114-.198-.011-.304.088-.403.087-.088.197-.232.296-.346.1-.114.133-.198.198-.33.065-.134.034-.248-.015-.347-.05-.099-.445-1.076-.612-1.47-.16-.389-.323-.335-.445-.34-.114-.007-.247-.007-.38-.007a.73.73 0 0 0-.529.247c-.182.198-.691.677-.691 1.654s.71 1.916.81 2.049c.098.133 1.394 2.132 3.383 2.992.47.205.84.326 1.129.418.475.152.904.129 1.246.08.38-.058 1.171-.48 1.338-.943.164-.464.164-.86.114-.943-.049-.084-.182-.133-.38-.232"/></svg>
                    Share via WhatsApp
                </button>
            </div>
        </div>
    </div>

    <script>
        let modal = document.getElementById("medicineModal");
        let currentMedicineData = null;

        function openModal(data) {
            currentMedicineData = data;
            let grid = document.getElementById("detailGrid");
            grid.innerHTML = ''; 
            
            // Set the modal title dynamically based on typical name columns
            let title = data['Brand Name'] || data['Name'] || data['Generic Name'] || 'Medicine Details';
            document.getElementById("modalTitle").innerText = title;

            // Populate the grid
            for (let key in data) {
                if (data.hasOwnProperty(key) && data[key] && data[key].trim() !== "") {
                    grid.innerHTML += `
                        <div class="detail-item">
                            <span class="label">${key}</span>
                            <span class="value">${data[key]}</span>
                        </div>
                    `;
                }
            }
            modal.style.display = "block";
        }

        function closeModal() {
            modal.style.display = "none";
        }

        function shareToWhatsApp() {
            if (!currentMedicineData) return;
            
            let text = "*Medicine Details*\n\n";
            for (let key in currentMedicineData) {
                if (currentMedicineData[key] && currentMedicineData[key].trim() !== "") {
                    text += `*${key}:* ${currentMedicineData[key]}\n`;
                }
            }
            
            let whatsappUrl = "https://api.whatsapp.com/send?text=" + encodeURIComponent(text);
            window.open(whatsappUrl, '_blank');
        }

        // Close modal when clicking outside
        window.onclick = function(event) {
            if (event.target == modal) {
                closeModal();
            }
        }
    </script>
</body>
</html>
