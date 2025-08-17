# LLMBench - Large Language Model Benchmarking Tool

A comprehensive Python application for benchmarking Large Language Model services with real-time metrics tracking and live display updates.

## 🚀 Features

- **Local & Remote LLM Testing**: Connect to local services or remote servers
- **Multi-Service Support**: Ollama, vLLM, and Llama.cpp compatibility
- **Real-time Display**: Live metrics updates with screen clearing
- **Comprehensive Metrics**: Track timing, token speeds, and response quality
- **File Output**: Automatic results saving with timestamps
- **API Authentication**: Optional API key support for remote servers
- **Server History**: Automatic storage of previously used remote servers

## 📋 Requirements

- Python 3.8 or higher
- Windows 10+ / Linux / macOS
- Internet connection (for remote servers)

## 🔧 Installation

### 🚀 Automatic Setup (Recommended)

**One-command setup with automatic installation:**

1. **Download/clone this repository**
2. **Run the automatic setup:**

#### Windows (Command Prompt)
```cmd
# Navigate to LLMBench source directory
cd LLMBench

# Run automatic setup (installs to Documents/LLMBench)
python setup.py --setup

# Run LLMBench from anywhere
llmbench
```

#### Windows (PowerShell)
```powershell
# Navigate to LLMBench source directory
cd LLMBench

# Run automatic setup (installs to Documents/LLMBench)
python setup.py --setup

# Run LLMBench from anywhere
llmbench
```

#### Linux/macOS
```bash
# Navigate to LLMBench source directory
cd LLMBench

# Run automatic setup (installs to ~/LLMBench)
python3 setup.py --setup

# Run LLMBench from anywhere (if ~/.local/bin is in PATH)
llmbench

# Or run directly
~/LLMBench/llmbench
```

**What the setup does:**
- ✅ Installs to user directory (Documents/LLMBench on Windows, ~/LLMBench on Linux)
- ✅ Creates isolated virtual environment  
- ✅ Copies all source files to installation directory
- ✅ Installs all dependencies automatically
- ✅ Creates global launcher command (`llmbench`)
- ✅ Verifies Python version (3.8+ required)

**Installation Locations:**
- **Windows**: `C:\Users\[username]\Documents\LLMBench\`
- **Linux/macOS**: `/home/[username]/LLMBench/`

**Note for Linux/macOS users**: The setup creates a global `llmbench` command in `~/.local/bin/`. If this directory is not in your PATH, you can:
```bash
# Add to PATH (add this to ~/.bashrc or ~/.zshrc)
export PATH="$HOME/.local/bin:$PATH"

# Or run directly from installation directory
~/LLMBench/llmbench
```

### 📋 Manual Installation

#### Windows Manual Setup
```cmd
# Check Python version (3.8+ required)
python --version

# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run application
python llmbench.py
```

#### Linux/macOS Manual Setup
```bash
# Check Python version (3.8+ required)
python3 --version

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run application
python llmbench.py
```

### 📦 Standalone Executable (No Python Required)

For users without Python installed:

1. **Download the latest release** from the releases page
2. **Extract the ZIP file**
3. **Double-click `LLMBench.exe`** (Windows) to run
4. **Follow the on-screen prompts**

## 🎯 Quick Start

### Local Testing

#### After Automatic Setup:
```bash
# All platforms - run from anywhere
llmbench

# Or run from installation directory:
# Windows: Documents\LLMBench\llmbench.bat
# Linux:   ~/LLMBench/llmbench
```

#### Manual Steps:
1. **Start your LLM service** (Ollama, vLLM, or Llama.cpp)
2. **Run LLMBench using your preferred method above**
3. **Select "Local"** when prompted for connection type
4. **Choose your service** from the detected list
5. **Select a model** from the available models
6. **Pick prompts to test** and watch the live results!

### Remote Testing

#### Quick Example:
```bash
# Using launcher command (after setup)
llmbench

# Follow prompts:
# 1. Select "Remote"
# 2. Enter: 192.168.10.101:11434
# 3. API Key: (leave blank or enter key)
# 4. Select model: phi3:mini
# 5. Choose prompts and benchmark!
```

#### Manual Steps:
1. **Run LLMBench** (using any method above)
2. **Select "Remote"** when prompted for connection type
3. **Enter server IP/URL** (e.g., `192.168.1.100:11434`)
4. **Provide API key** (optional - leave blank if not needed)
5. **Select model and run benchmarks**

## 🔌 Supported Services

### Ollama
- **Default Port**: 11434
- **API Endpoint**: `/api/generate`
- **Model Listing**: `/api/tags`
- **Example**: `http://localhost:11434`

### vLLM
- **Default Port**: 8000
- **API Endpoint**: `/v1/completions`
- **Model Listing**: `/v1/models`
- **Example**: `http://localhost:8000`

### Llama.cpp
- **Default Port**: 8080
- **API Endpoint**: `/completion`
- **Health Check**: `/health`
- **Example**: `http://localhost:8080`

## 📊 Metrics Tracked

LLMBench provides comprehensive performance metrics:

- **Total Request Time**: Complete end-to-end timing
- **Prompt Delay Time**: Time from submission to first token
- **Generation Time**: Time from first token to completion
- **Total Tokens Generated**: Including any reasoning tokens
- **Generation Speed**: Tokens per second (generation time only)
- **Overall Request Speed**: Tokens per second (total request time)

## 📁 File Structure

```
LLMBench/
├── llmbench.py           # Main application entry point
├── runllmbench.py        # Benchmark execution engine
├── savellmbench.py       # Live display and file output
├── remoteconfig.py       # Remote server management
├── .env                  # Configuration settings
├── requirements.txt      # Python dependencies
├── results/              # Benchmark output files (auto-created)
├── remote_servers.json   # Stored server IPs (auto-created)
└── README.md            # This file
```

## ⚙️ Configuration

### Environment Variables (.env)

```bash
# Default API endpoints for local services
OLLAMA_HOST=http://localhost:11434
VLLM_HOST=http://localhost:8000
LLAMACPP_HOST=http://localhost:8080

# Request settings
TIMEOUT_SECONDS=180
MAX_RETRIES=3

# Logging
LOG_LEVEL=INFO
LOG_FILE=llmbench.log
```

### Remote Server Configuration

- **Server IPs/URLs** are automatically saved to `remote_servers.json`
- **API keys** are stored in memory only (never saved to disk)
- **Authentication headers** are automatically included in requests

## 🧪 Example Usage

### Testing Local Ollama with phi3:mini

#### Windows:
```cmd
REM Start Ollama
ollama serve

REM Pull a fast model for testing (in another terminal)
ollama pull phi3:mini

REM Run LLMBench (after setup)
llmbench.bat

REM Select: Local → Ollama → phi3:mini → Prompt 1
```

#### Linux/macOS:
```bash
# Start Ollama
ollama serve

# Pull a fast model for testing (in another terminal)
ollama pull phi3:mini

# Run LLMBench (after setup)
./llmbench

# Select: Local → Ollama → phi3:mini → Prompt 1
```

### Testing Remote Server

#### All Platforms:
```bash
# Run LLMBench
./llmbench              # Linux/macOS
llmbench.bat             # Windows CMD
.\llmbench.ps1           # Windows PowerShell

# Follow the prompts:
# 1. Select: Remote
# 2. Enter server: 192.168.10.101:11434
# 3. API Key: (leave blank or enter key)
# 4. Select available model and test prompts
```

## 📈 Results Output

Results are automatically saved to `results/benchmark_output_YYYYMMDD_HHMMSS.txt`:

```
================================================================================
LLMBench Results - 2025-08-16 17:50:50
================================================================================
Service: Ollama
Model: phi3:mini
Host: http://192.168.10.101:11434
================================================================================

============================================================
PROMPT: Write a short story about a robot learning to paint
============================================================
Prompt Text: Write a short story about a robot learning to paint.
Started: 2025-08-16 17:50:50

METRICS:
total_elapsed_time: 3.245
prompt_delay_time: 0.156
generation_time: 3.089
total_tokens_generated: 147
generation_speed_tokens_per_sec: 47.58
overall_request_speed_tokens_per_sec: 45.29
completed_at: 2025-08-16 17:50:53

RESPONSE:
[Full model response here...]
```

## 🐛 Troubleshooting

### Common Issues

**"No LLM services detected"**
- Ensure your LLM service is running and accessible
- Check firewall settings
- Verify correct ports (11434 for Ollama, 8000 for vLLM, 8080 for Llama.cpp)

**"Connection refused" for remote servers**
- Verify the server IP and port
- Check if API key is required
- Ensure the remote service is running and accessible

**"API request failed"**
- Check API key if required
- Verify the correct model name
- Ensure sufficient server resources

### Windows-Specific Issues

**"Windows protected your PC"**
- Click "More info" then "Run anyway"
- This is normal for unsigned executables

**Missing Python error**
- Download Python from [python.org](https://python.org)
- Ensure "Add to PATH" is checked during installation

**Permission denied**
- Run as administrator if needed
- Check antivirus software settings

## 🏗️ Building for Windows

### 🚀 Recommended: Automated Build Script

**Use the enhanced build script for the best experience:**

```bash
# Navigate to project directory
cd LLMBench

# Run the enhanced build script
python build_enhanced.py
```

**Enhanced build (`build_enhanced.py`):**
- ✅ Installs all required dependencies automatically
- ✅ Handles Windows permission errors gracefully
- ✅ Forces inclusion of all Python modules (fixes import issues)
- ✅ Creates standalone executable in `dist/llmbench.exe`
- ✅ Clean console interface with reduced flashing
- ✅ Full streaming benchmark experience
- ✅ Real-time elapsed timer display
- ✅ Custom prompt support included

### 📋 Manual Build (Alternative)

If you prefer manual control:

```bash
# Install PyInstaller
pip install pyinstaller

# Clean previous builds
rm -rf build dist __pycache__ *.spec

# Build with comprehensive module inclusion
pyinstaller --onefile \
    --name=llmbench \
    --collect-all=requests \
    --collect-all=urllib3 \
    --collect-all=certifi \
    --collect-all=charset_normalizer \
    --collect-all=idna \
    --collect-all=psutil \
    --collect-all=dotenv \
    --hidden-import=runllmbench \
    --hidden-import=savellmbench \
    --hidden-import=remoteconfig \
    --add-data=".env;." \
    --clean \
    --noconfirm \
    llmbench.py

# Executable will be in dist/llmbench.exe
```

### 📦 Create Portable Distribution Package

```bash
# After building, create distribution package
mkdir LLMBench-Windows-Portable
cp dist/llmbench.exe LLMBench-Windows-Portable/
cp .env LLMBench-Windows-Portable/
cp README.md LLMBench-Windows-Portable/

# Create quick start guide
cat > LLMBench-Windows-Portable/QUICKSTART.txt << 'EOF'
LLMBench - Windows Portable

Quick Start:
1. Double-click llmbench.exe
2. Select Local or Remote connection
3. Choose your service and model
4. Run benchmarks!

No Python installation required.
Results saved to results/ folder.
EOF

# Create ZIP for distribution
zip -r LLMBench-Windows-Portable.zip LLMBench-Windows-Portable/
```

### 🔧 Troubleshooting Windows Build

**If you encounter module import errors:**
1. **Use `build_enhanced.py`** - it handles most common issues automatically
2. **Check Python environment** - ensure all dependencies are installed
3. **Try fresh virtual environment** if issues persist

**Common issues and fixes:**
- **"No module named 'requests'"** → Use `build_enhanced.py` (automatically fixed)
- **"Windows protected your PC"** → Click "More info" → "Run anyway"
- **Antivirus blocking** → Add exception for the executable

## 🐧 Linux Setup and Usage

### 🚀 Quick Start (Recommended)

**1. Install Dependencies:**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv git

# CentOS/RHEL/Fedora
sudo dnf install python3 python3-pip python3-venv git
# or for older versions:
# sudo yum install python3 python3-pip python3-venv git

# Arch Linux
sudo pacman -S python python-pip git
```

**2. Clone and Setup:**
```bash
# Clone the repository
git clone https://github.com/Rob-P-Smith/llmbench.git
cd llmbench

# Run automatic setup
python3 setup.py --setup
```

**3. Run LLMBench:**
```bash
# If ~/.local/bin is in your PATH
llmbench

# Or run directly
~/LLMBench/llmbench

# Or from installation directory
cd ~/LLMBench && ./llmbench
```

### 📋 Manual Linux Setup

**For advanced users who prefer manual control:**

```bash
# Navigate to project directory
cd llmbench

# Check Python version (3.8+ required)
python3 --version

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run LLMBench
python3 llmbench.py
```

### 🔧 Linux Build (PyInstaller)

**Create a Linux executable:**

```bash
# Install PyInstaller in virtual environment
pip install pyinstaller

# Use the enhanced build script (adapted for Linux)
python3 build_windowed.py

# Or manual PyInstaller command
pyinstaller --onefile \
    --name=llmbench \
    --collect-all=requests \
    --collect-all=urllib3 \
    --collect-all=certifi \
    --collect-all=charset_normalizer \
    --collect-all=idna \
    --collect-all=psutil \
    --collect-all=dotenv \
    --hidden-import=runllmbench \
    --hidden-import=savellmbench \
    --hidden-import=remoteconfig \
    --hidden-import=custom_prompts \
    --add-data=".env:." \
    --clean \
    --noconfirm \
    llmbench.py

# Executable will be in dist/llmbench
./dist/llmbench
```

### 🐳 Docker Support

**Run LLMBench in a container:**

```dockerfile
# Create Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8080

CMD ["python3", "llmbench.py"]
```

```bash
# Build and run
docker build -t llmbench .
docker run -it --rm --network host llmbench
```

### 🔌 LLM Service Setup on Linux

**Ollama:**
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama service
ollama serve

# Pull a model (in another terminal)
ollama pull phi3:mini
```

**vLLM:**
```bash
# Install vLLM
pip install vllm

# Start vLLM server
python -m vllm.entrypoints.api_server \
    --model microsoft/DialoGPT-medium \
    --host 0.0.0.0 \
    --port 8000
```

**Llama.cpp:**
```bash
# Build llama.cpp
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp
make

# Start server (with your GGUF model)
./server -m your-model.gguf --host 0.0.0.0 --port 8080
```

### 🐛 Linux Troubleshooting

**Common Issues:**

**"Permission denied" for ~/.local/bin/llmbench:**
```bash
chmod +x ~/.local/bin/llmbench
```

**Missing Python development headers:**
```bash
# Ubuntu/Debian
sudo apt install python3-dev

# CentOS/RHEL/Fedora
sudo dnf install python3-devel
```

**Virtual environment activation issues:**
```bash
# Make sure you're in the right directory
cd ~/LLMBench
source venv/bin/activate

# Or use absolute path
source ~/LLMBench/venv/bin/activate
```

**Display/terminal issues:**
```bash
# If ANSI codes don't work, set fallback
export TERM=xterm-256color

# For tmux/screen users
export TERM=screen-256color
```

**Network/firewall issues:**
```bash
# Check if LLM service is accessible
curl http://localhost:11434/api/tags  # Ollama
curl http://localhost:8000/v1/models  # vLLM
curl http://localhost:8080/health     # Llama.cpp

# Open firewall if needed (for remote access)
sudo ufw allow 11434  # Ollama
sudo ufw allow 8000   # vLLM
sudo ufw allow 8080   # Llama.cpp
```

### 📊 Performance Tips for Linux

**For better performance:**
```bash
# Increase ulimits for large models
ulimit -n 65536

# Use faster JSON parsing (optional)
pip install ujson

# Monitor resources during benchmarking
htop
nvidia-smi  # For GPU monitoring
```

## 🔧 Development

### Project Structure

- **llmbench.py**: Main entry point with service detection and UI
- **runllmbench.py**: Core benchmarking logic and API communication
- **savellmbench.py**: Real-time display updates and file output
- **remoteconfig.py**: Remote server configuration and authentication

### Adding New Services

To add support for a new LLM service:

1. **Update ServiceDetector** in `llmbench.py`
2. **Add API endpoints** in `runllmbench.py`
3. **Implement model listing** in ModelSelector
4. **Test with real service**

### Dependencies

```
python-dotenv>=1.0.0  # Environment variable management
requests>=2.31.0      # HTTP API calls
psutil>=5.9.0         # Process detection (local services)
```

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For issues, questions, or contributions:

1. **Check troubleshooting** section above
2. **Search existing issues** in the repository
3. **Create a new issue** with detailed information
4. **Include logs and error messages** when reporting bugs

## 🎯 Roadmap

- [ ] Support for additional LLM services (Anthropic, OpenAI)
- [ ] Batch testing with multiple prompts
- [ ] Historical benchmark comparison
- [ ] CSV/JSON export options
- [ ] Custom prompt templates
- [ ] Performance regression testing
- [ ] Docker containerization
- [ ] Web-based dashboard

---

**Happy Benchmarking! 🚀**