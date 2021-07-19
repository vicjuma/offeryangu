var socket = io();

var target = window.location


socket.on('online', () => {
    socket.emit('asses', {
        "message": "online"
    })
})

socket.on('connect', () => {
    document.querySelector('#button').addEventListener('click', (event) => {
        event.preventDefault();
        let msg = document.querySelector('#chat');

        data = {
            message: `${msg.value}`,
            sender: String(target).split('/')[5],
            recepient: String(target).split('/')[6]
        }
        socket.emit('receive message', data);
        msg.focus();
        msg.value = '';
    })
});

const msright = document.querySelector('.display-right')
const msleft = document.querySelector('.display-left')

socket.on('broadcast', (data) => {
    location.reload(true)
})