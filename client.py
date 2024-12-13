# client.py
import asyncio
import websockets
from colorama import init, Fore, Style
import sys

# Initialize colorama
init(autoreset=True)

# Define color mapping
COLORS = {
    "purple": Fore.MAGENTA,
    "red": Fore.RED,
    "green": Fore.GREEN,
    "orange": Fore.YELLOW + Style.BRIGHT,
    "yellow": Fore.YELLOW,
    "cyan": Fore.CYAN
}
DEFAULT_COLOR = Fore.WHITE  # Default color for the user's own messages

async def receive_messages(websocket):
    try:
        async for message in websocket:
            # Parse message color and content
            if ":" in message:
                color, content = message.split(":", 1)
                color = COLORS.get(color, DEFAULT_COLOR)
                sys.stdout.write(f"\r{color}{content}\n")
            else:
                sys.stdout.write(f"\r{DEFAULT_COLOR}{message}\n")
            sys.stdout.flush()
    except websockets.ConnectionClosed as e:
        print(f"\nConnection closed by server. Reason: {e}")

async def send_messages(websocket):
    try:
        while True:
            # Wait for user input
            message = await asyncio.to_thread(input)
            if message.strip():  # Only send if the message is not empty
                # Clear the current line and display the sent message
                sys.stdout.write("\033[F\033[K")  # Clear the line
                sys.stdout.write(f"{DEFAULT_COLOR}{message}\n")
                sys.stdout.flush()
                await websocket.send(message)
            else:
                print("\nCannot send an empty message.")
    except websockets.ConnectionClosed as e:
        print(f"\nConnection closed by server. Reason: {e}")

async def connect_to_server():
    while True:
        server_address = input("Enter the WebSocket server address (e.g., ws://192.168.1.100:8765): ").strip()
        try:
            # Attempt to connect to the server
            async with websockets.connect(server_address) as websocket:
                print("Connected to the server!")
                # Run receive and send tasks concurrently
                await asyncio.gather(
                    receive_messages(websocket),
                    send_messages(websocket)
                )
        except (websockets.ConnectionClosedError, OSError) as e:
            print(f"Failed to connect to {server_address}: {e}")
            print("Please check the address and try again.")

if __name__ == "__main__":
    try:
        asyncio.run(connect_to_server())
    except KeyboardInterrupt:
        print("\nDisconnected from server. Goodbye!")

