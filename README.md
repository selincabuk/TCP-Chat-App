# Chat Application

This is a simple chat application that allows multiple users to communicate with each other. The application consists of a server and a client, enabling real-time messaging between users.

## Features

- Real-time messaging
- Nickname registration
- List of online users
- Message history
- Search messages
- Manage contacts (add, remove, move contacts between groups)

## Getting Started

### Prerequisites

Make sure you have Python 3.x installed on your machine. You can download it from [python.org](https://www.python.org/).

### Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/your-repo-name.git
    ```
2. Navigate to the project directory:
    ```bash
    cd your-repo-name
    ```

### Running the Application

#### Starting the Server

1. Open a command prompt or terminal window.
2. Navigate to the project directory if not already there.
3. Run the server script:
    ```bash
    python server.py
    ```
    The server will start and listen for incoming connections on port `25000`.

#### Starting the Client

1. Open another command prompt or terminal window.
2. Navigate to the project directory if not already there.
3. Run the client script:
    ```bash
    python client.py
    ```
4. Repeat the above steps to start additional clients for other users.

### Usage

1. When the client starts, it will prompt you to enter a nickname.
2. After setting your nickname, you can start sending messages.
3. Available commands:
    - `/quit`: Disconnect from the server
    - `/online`: Show a list of online users
    - `/history`: Show your message history
    - `/search <keyword>`: Search your message history for a keyword
    - `/commands`: List all available commands

### Example

#### Starting the Server

```bash
python server.py

### Output: Chat server is up and running!
Listening for new connections on port 25000.

#### Starting the Server
python client.py


### Output: Welcome to Chat! Please type your nickname:


 
