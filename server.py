# server.py
import asyncio
import websockets
import socket

connected_users = {}  # Maps websocket to user_id
user_colors = [
    "purple", "red", "green", "orange", "yellow", "cyan"
]  # Define up to 6 colors

def get_local_ip():
    """Get the server's local IP address."""
    hostname = socket.gethostname()
    return socket.gethostbyname(hostname)

async def handler(websocket):
    if len(connected_users) >= len(user_colors):
        await websocket.send("Chat is full, try again later.")
        await websocket.close()
        return

    # Assign a unique user ID and color
    user_id = len(connected_users) + 1
    connected_users[websocket] = user_id
    print(f"User {user_id} connected. Total users: {len(connected_users)}")

    try:
        await websocket.send(f"Connected to the chat! You are User {user_id}.")
        async for message in websocket:
            print(f"Message received from User {user_id}: {message}")
            # Relay the message to other users
            for user_ws, user_id_other in connected_users.items():
                if user_ws != websocket:
                    try:
                        user_color = user_colors[user_id - 1]  # Get color for sender
                        await user_ws.send(f"{user_color}:{message}")
                        print(f"Message relayed to User {user_id_other}.")
                    except websockets.ConnectionClosed:
                        print(f"User {user_id_other} disconnected.")
    except websockets.ConnectionClosed:
        print(f"User {user_id} disconnected.")
    finally:
        # Remove user on disconnect
        del connected_users[websocket]
        print(f"User {user_id} disconnected. Total users: {len(connected_users)}")

async def main():
    local_ip = get_local_ip()
    port = 8765
    async with websockets.serve(handler, local_ip, port):
        print(f"Server started. Other devices can connect at:")
        print(f"  ws://{local_ip}:{port}")
        print(f"Or connect locally on this device at:")
        print(f"  ws://localhost:{port}")
        await asyncio.Future()  # Run until interrupted

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer is shutting down. Goodbye!")

