document.addEventListener('DOMContentLoaded', function () {
    // Connect to the Socket.IO server
    const socket = io('http://127.0.0.1:8050'); 

    socket.on('connect', function () {
        console.log('Connected to Socket.IO server.');
    });

    socket.on('message', function (data) {
        console.log('Received message:', data);

        // Dispatch a custom event to update the dcc.Store
        const event = new CustomEvent('store-update', { detail: data });
        window.dispatchEvent(event);
    });

    // Listen for custom events to update dcc.Store
    window.addEventListener('store-update', function (event) {
        const storeElement = document.querySelector('#socket-store');
        if (storeElement) {
            // Set the received data into the dcc.Store
            storeElement.__shinyValue = event.detail; // Update dcc.Store's value
            storeElement.dispatchEvent(new Event('input')); // Notify Dash of the change
        }
    });
});