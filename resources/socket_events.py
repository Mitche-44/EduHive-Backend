from flask_socketio import emit
from app import socketio

@socketio.on('connect')
def handle_connect():
    emit("server_message", {"msg": "Connected to EduHive WebSocket!"})

@socketio.on('subscribe_upgrade')
def handle_subscription_upgrade(data):
    emit("subscription_updated", data, broadcast=True)

@socketio.on('disconnect')
def handle_disconnect():
    emit("server_message", {"msg": "Disconnected from EduHive WebSocket!"})
    print("Client disconnected")