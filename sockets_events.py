from flask_socketio import SocketIO, emit

def register_socket_events(socketio: SocketIO):
    @socketio.on('connect')
    def handle_connect():
        emit("server_message", {"msg": "Connected to EduHive WebSocket!"})
        print("[Socket] Client connected")

    @socketio.on('disconnect')
    def handle_disconnect():
        emit("server_message", {"msg": "Disconnected from EduHive WebSocket!"})
        print("[Socket] Client disconnected")

    @socketio.on('subscribe_upgrade')
    def handle_subscription_upgrade(data):
        emit("subscription_updated", data, broadcast=True)
        print(f"[Socket] Subscription upgraded: {data}")

    @socketio.on('new_post')
    def handle_new_post(data):
        if not data or 'title' not in data or 'author_id' not in data:
            print("[Socket] Invalid new post data:", data)
            return
        print(f"[Socket] New post by user {data['author_id']}: {data['title']}")
        emit('new_post', data, broadcast=True)

    @socketio.on('like_post')
    def handle_like_post(data):
        if not data or 'postId' not in data:
            print("[Socket] Invalid like data:", data)
            return
        print(f"[Socket] Post liked: {data['postId']}")
        emit('like_post', data, broadcast=True)

    @socketio.on('reply')
    def handle_reply(data):
        if not data or 'post_id' not in data or 'content' not in data:
            print("[Socket] Invalid reply data:", data)
            return
        print(f"[Socket] New reply on post {data['post_id']}: {data['content']}")
        emit('reply', data, broadcast=True)
