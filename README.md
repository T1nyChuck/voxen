# Voxen: Real-Time Voice AI Chat Application

A Python-based real-time voice AI chat application using OpenAI's Real-time API, Flask, and Socket.IO. This repository includes three core files:

- `instructions.py` – Contains the prompt instructions for the AI voice agent.
- `realtime_voice_api.py` – Main Flask application handling voice streaming and API calls.
- `index.html` – Frontend interface for recording and playing back audio.

---

## Table of Contents

1. [Prerequisites](#prerequisites)  
2. [Setup Instructions](#setup-instructions)  
   - [Clone the Repository](#clone-the-repository)  
   - [Open in VSCode](#open-in-vscode)  
   - [Create and Activate a Virtual Environment](#create-and-activate-a-virtual-environment)  
   - [Install Dependencies](#install-dependencies)  
3. [Configuration](#configuration)  
   - [Create the `.env` File](#create-the-env-file)  
4. [Project Structure](#project-structure)  
5. [Running the Application](#running-the-application)  
6. [Usage](#usage)  
7. [Troubleshooting](#troubleshooting)  
8. [License](#license)  

---

## Prerequisites

- **Python 3.8+** installed on your system.  
- **VSCode** (Visual Studio Code) for development.  
- An **OpenAI API key**. Sign up at [https://platform.openai.com](https://platform.openai.com) if you don’t have one.  

---

## Setup Instructions

### Clone the Repository

```bash
# Replace with your GitHub SSH or HTTPS URL
git clone git@github.com:T1nyChuck/voxen.git
cd voxen
```

### Open in VSCode

1. Launch VSCode.  
2. Select **File › Open Folder...**.  
3. Choose the `voxen` folder you just cloned.  

### Create and Activate a Virtual Environment

It’s best practice to isolate dependencies in a virtual environment.

```bash
# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate

# Windows (PowerShell)
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### Install Dependencies

With the virtual environment activated, install required packages:

```bash
pip install flask flask-socketio python-dotenv openai requests
```

> **Tip:** You can freeze these into a `requirements.txt` for future installs:
> ```bash
> pip freeze > requirements.txt
> ```

---

## Configuration

### Create the `.env` File

1. In the project root, create a file named `.env`.  
2. Add your OpenAI API key:

   ```ini
   OPENAI_API_KEY=your_openai_api_key_here
   ```

3. Save and close the file.  

---

## Project Structure

```plaintext
voxen/
├── instructions.py            # AI prompt instructions
├── realtime_voice_api.py      # Flask + Socket.IO server
├── templates/
│   └── index.html             # Frontend HTML page
└── .env                       # Environment variables (not checked into Git)
```

> **Note:** Ensure `index.html` is placed under a `templates` folder so Flask’s `render_template` can find it.

---

## Running the Application

1. Ensure your virtual environment is activated.  
2. Start the Flask server:

   ```bash
   python realtime_voice_api.py
   ```

3. You should see output like:

   ```
   * Serving Flask app 'realtime_voice_api'
   * Debug mode: on
   * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
   ```

4. Open your browser and navigate to `http://localhost:5000`.  

---

## Usage

1. Click **Start Conversation** to begin recording your voice.  
2. Speak clearly into your microphone.  
3. Click **End Conversation** to stop recording and send audio to the AI.  
4. The AI response will play back automatically.  

Feel free to iterate on `instructions.py` to adjust the AI’s behavior.

---

## Troubleshooting

- **Module Not Found Errors**: Double-check that your virtual environment is activated and that you ran `pip install`.  
- **`.env` Not Loaded**: Verify that `python-dotenv` is installed and that your `.env` file is in the project root.  
- **Port Already in Use**: If port 5000 is occupied, stop the running service or modify `realtime_voice_api.py` to use a different port.  
- **CORS or Socket Issues**: Ensure you’re loading `index.html` via Flask (i.e., at `/`), not from the file system.  

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

**Happy coding!** 🎉
