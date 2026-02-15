export function showLobby() {
    document.getElementById('menu').style.display = 'none';
    document.getElementById('lobby').style.display = 'block';
    fetchRooms().then(rooms => renderRoomList(rooms));
}

export function hideLobby() {
    document.getElementById('lobby').style.display = 'none';
    document.getElementById('menu').style.display = 'block';
}

export async function fetchRooms() {
    const response = await fetch('/rooms');
    return await response.json();
}

export function renderRoomList(rooms) {
    const roomList = document.getElementById('room-list');
    roomList.innerHTML = '';
    
    rooms.forEach(room => {
        const roomItem = document.createElement('div');
        roomItem.className = 'room-item';
        roomItem.textContent = room.name;
        roomItem.onclick = () => joinRoom(room.id);
        roomList.appendChild(roomItem);
    });
}

function joinRoom(roomId) {
    console.log('Joining room:', roomId);
}

// Event handlers
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('create-room-btn').onclick = () => {
        const roomName = prompt('Enter room name:');
        if (roomName) {
            console.log('Creating room:', roomName);
        }
    };
    
    document.getElementById('join-room-btn').onclick = () => {
        fetchRooms().then(rooms => renderRoomList(rooms));
    };
    
    document.getElementById('back-btn').onclick = hideLobby;
});