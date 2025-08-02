from flask_socketio import SocketIO, emit
from flask import request
from functools import wraps

def validate_socket_data(required_fields):
    """Decorator to validate incoming socket data"""
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            data = args[0] if args else kwargs.get('data', {})
            if not isinstance(data, dict):
                print(f"[Socket] Invalid data format. Expected dict, got {type(data)}")
                emit('error', {'message': 'Invalid data format'})
                return
            
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                print(f"[Socket] Missing required fields: {missing_fields}")
                emit('error', {'message': f'Missing fields: {", ".join(missing_fields)}'})
                return
                
            return f(*args, **kwargs)
        return wrapped
    return decorator

def register_socket_events(socketio: SocketIO):
    """Register all Socket.IO event handlers with proper validation and logging"""
    
    @socketio.on('connect')
    def handle_connect():
        """Handle new client connections"""
        client_id = request.sid
        print(f"[Socket] Client connected: {client_id}")
        emit('server_message', {
            'msg': 'Connected to EduHive WebSocket!',
            'client_id': client_id
        })
        
        # Send connection acknowledgement only to this client
        emit('connection_ack', {
            'status': 'success',
            'message': 'You are now connected'
        }, room=client_id)

    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle client disconnections"""
        client_id = request.sid
        print(f"[Socket] Client disconnected: {client_id}")
        emit('server_message', {
            'msg': 'Client disconnected',
            'client_id': client_id
        }, broadcast=True)

    @socketio.on('new_post')
    @validate_socket_data(['title', 'author_id', 'author_name'])
    def handle_new_post(data):
        """Broadcast new post to all connected clients"""
        print(f"[Socket] New post by {data['author_name']} (ID: {data['author_id']}): {data['title']}")
        
      
        emit('new_post', broadcast=True, include_self=False)
        
        # Send acknowledgement to sender
        emit('post_acknowledgement', {
            'status': 'success',
            'message': 'Your post was shared successfully',
             
        }, room=request.sid)

    @socketio.on('like_post')
    @validate_socket_data(['postId', 'userId', 'userName'])
    def handle_like_post(data):
        """Handle post likes and notify relevant clients"""
        print(f"[Socket] Post {data['postId']} liked by {data['userName']}")
        

     
        
        # Broadcast to all except the sender
        emit('like_post', broadcast=True, include_self=False)
        
        # Optionally notify post owner only
        emit('like_notification', {
            'post_id': data['postId'],
            'liked_by': data['userName']
        }, room=f"user_{data['postOwnerId']}")  # Assuming postOwnerId is available

    @socketio.on('reply')
    @validate_socket_data(['post_id', 'content', 'author_id', 'author_name'])
    def handle_reply(data):
        """Handle post replies with threading support"""
        print(f"[Socket] New reply on post {data['post_id']} by {data['author_name']}")
        
       
        # Broadcast to all clients
        emit('reply',  broadcast=True)
        
        # Send notification to post author
        emit('reply_notification', {
            'post_id': data['post_id'],
            'replied_by': data['author_name'],
            'preview': data['content'][:50] + '...' if len(data['content']) > 50 else data['content']
        }, room=f"user_{data['post_author_id']}")

    @socketio.on('subscribe_upgrade')
    @validate_socket_data(['user_id', 'subscription_level'])
    def handle_subscription_upgrade(data):
        """Handle subscription upgrades with validation"""
        valid_levels = ['basic', 'premium', 'enterprise']
        if data['subscription_level'] not in valid_levels:
            emit('error', {
                'message': f'Invalid subscription level. Must be one of: {", ".join(valid_levels)}'
            })
            return
            
        print(f"[Socket] User {data['user_id']} upgraded to {data['subscription_level']}")
        
        # Broadcast to all admin clients
        emit('admin_notification', {
            'type': 'subscription_upgrade',
            'user_id': data['user_id'],
            'new_level': data['subscription_level']
        }, room='admin_clients')
        
        # Notify the specific user
        emit('subscription_updated', {
            'status': 'success',
            'new_level': data['subscription_level'],
           
        }, room=f"user_{data['user_id']}")

    # Error handler for Socket.IO
    @socketio.on_error_default
    def default_error_handler(e):
        print(f"[Socket] Error occurred: {str(e)}")
        emit('error', {
            'message': 'An unexpected error occurred',
            'error': str(e)
        })