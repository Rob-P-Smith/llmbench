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

### Create Standalone Executable

```bash
# Install PyInstaller
pip install pyinstaller

# Build executable
pyinstaller --onefile --name=LLMBench llmbench.py

# Executable will be in dist/LLMBench.exe
```

### Create Portable Package

```bash
# Create distribution folder
mkdir LLMBench-Portable
cp *.py LLMBench-Portable/
cp .env LLMBench-Portable/
cp requirements.txt LLMBench-Portable/

# Create run script
echo "python llmbench.py" > LLMBench-Portable/run.bat
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