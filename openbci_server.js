const WebSocket = require('ws');
const { Cyton } = require('openbci-cyton');

const wss = new WebSocket.Server({ port: 8080 }); // WebSocket server for game communication
const board = new Cyton({ port: '/dev/ttyUSB0', verbose: true }); // Adjust port if needed

async function startBoard() {
    try {
        await board.connect();
        console.log("🔗 OpenBCI Cyton Connected!");

        await board.start();
        console.log("📡 EEG Streaming Started...");

        board.on('sample', (sample) => {
            let eegData = sample.channelData; // Extract raw EEG data
            let blinkDetected = detectBlink(eegData);

            // Send EEG activity to all connected WebSocket clients
            wss.clients.forEach(client => {
                if (client.readyState === WebSocket.OPEN) {
                    client.send(JSON.stringify({ blink: blinkDetected }));
                }
            });

            console.log(`🔵 EEG Data: ${eegData.map(val => val.toFixed(2))} | Blink: ${blinkDetected ? "YES 🚀" : "NO 🏁"}`);
        });

    } catch (error) {
        console.error("❌ OpenBCI Connection Error:", error);
    }
}

// Blink detection logic (modify threshold based on real-time calibration)
function detectBlink(eegData) {
    const THRESHOLD = 100; // Set threshold dynamically based on calibration
    return eegData.some(channel => Math.abs(channel) > THRESHOLD);
}

wss.on('connection', ws => {
    console.log("🖥️ New Client Connected!");
    ws.on('close', () => console.log("❌ Client Disconnected"));
});

startBoard();

console.log("🟢 WebSocket Server running on ws://localhost:8080");
