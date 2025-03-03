const WebSocket = require('ws');
const { OpenBCIBoard } = require('openbci');

const wss = new WebSocket.Server({ port: 8080 }); // WebSocket Server
const board = new OpenBCIBoard({ port: '/dev/ttyUSB0', verbose: true }); // Change port if needed

board.connect().then(() => {
    console.log("🔗 OpenBCI Connected!");
    board.streamStart();
});

board.on('sample', sample => {
    let eegData = sample.channelData; // Raw EEG data
    let blinkDetected = detectBlink(eegData);
    
    // Send EEG activity data to WebSocket clients (browser)
    wss.clients.forEach(client => {
        if (client.readyState === WebSocket.OPEN) {
            client.send(JSON.stringify({ blink: blinkDetected }));
        }
    });
});

// Blink detection function (adjust threshold based on your EEG cap)
function detectBlink(eegData) {
    return eegData.some(channel => Math.abs(channel) > 100); // Adjust based on calibration
}

console.log("🟢 WebSocket Server running on ws://localhost:8080");
