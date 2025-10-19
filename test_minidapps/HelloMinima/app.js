
// HelloMinima custom JavaScript
function showBalance() {
    MDS.cmd("balance", function(resp) {
        if(resp.status) {
            const balances = resp.response;
            let html = '<div class="card"><h3>Your Balance</h3>';

            balances.forEach(function(bal) {
                html += `
                    <p><strong>${bal.token}:</strong> ${bal.sendable}</p>
                `;
            });

            html += '</div>';
            document.getElementById('balance-display').innerHTML = html;
        }
    });
}

function showAddress() {
    MDS.cmd("getaddress", function(resp) {
        if(resp.status) {
            const addr = resp.response;
            document.getElementById('address-display').innerHTML = `
                <div class="card">
                    <h3>Your Address</h3>
                    <p style="word-break: break-all;">${addr.miniaddress}</p>
                </div>
            `;
        }
    });
}

// Auto-load on MDS init
function onMDSInit() {
    showBalance();
    showAddress();
}
