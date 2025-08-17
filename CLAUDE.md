# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

LLMBench is a Python-based benchmarking tool for Large Language Models. It automatically detects running LLM services (Ollama, vLLM, llama.cpp) and provides an interactive terminal interface for service selection.

## Project Structure

- `llmbench.py` - Main application with service detection and interactive menu
- `runllmbench.py` - Benchmark execution with comprehensive metrics tracking
- `savellmbench.py` - Real-time display and file output functionality
- `remoteconfig.py` - Remote server configuration and connection management
- `.env` - Configuration file for API endpoints and settings
- `requirements.txt` - Python dependencies
- `results/` - Directory containing timestamped benchmark results
- `remote_servers.json` - Stored remote server IPs/URLs (auto-generated)

## Development Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run the main application
python llmbench.py

# For testing without interactive input (CI/etc)
echo "q" | python llmbench.py
```

## Architecture

### Core Components

- **ServiceDetector**: Detects running LLM services using process scanning and API health checks
- **ServiceMenu**: Interactive terminal interface for service selection
- **ModelSelector**: Queries services for available models and provides selection interface
- **LLMBenchmarkRunner**: Handles actual benchmarking with comprehensive metrics tracking
- **LiveBenchmarkDisplay**: Real-time display updates and file output during benchmarks
- **RemoteServerConfig**: Manages remote server connections, IP storage, and API authentication
- **Configuration**: Environment-based configuration via .env file

### Service Detection Logic

The application detects services by:
1. Scanning running processes for service names (ollama, vllm, llama-server, etc.)
2. Making HTTP health check requests to default API endpoints
3. Combining both methods to determine service availability

### Configuration

Environment variables in `.env`:
- `OLLAMA_HOST`, `VLLM_HOST`, `LLAMACPP_HOST` - Service endpoints
- `TIMEOUT_SECONDS` - API request timeout
- `API_KEY` - Authentication (if needed)
- `LOG_LEVEL`, `LOG_FILE` - Logging configuration

### Dependencies

- `python-dotenv` - Environment variable management
- `requests` - HTTP API calls
- `psutil` - Process detection

### Workflow

1. **Connection Type Selection**: Choose between local or remote LLM services
2. **Service Discovery**: 
   - **Local**: Automatically detects Ollama, vLLM, and llama.cpp services on local machine
   - **Remote**: Connect to remote server with IP/URL storage and optional API key authentication
3. **Service Selection**: Interactive menu to choose which service to benchmark
4. **Model Selection**: Queries the selected service for available models and allows selection
5. **Prompt Selection**: Choose from 5 canned prompts or run all prompts
6. **Benchmarking**: Runs benchmarks with live display updates and comprehensive timing metrics
7. **File Output**: Automatically saves results to timestamped files in `results/` directory
8. **Results Display**: Shows detailed metrics and summary statistics

### Benchmark Metrics

The application tracks:
- **Total Time**: From submission to request completion
- **Prompt Delay Time**: Submission to first token received
- **Generation Time**: First token to last token
- **Total Tokens**: Generated tokens (including thinking tokens)
- **Tokens per Second**: Based on generation time only
- **Request Tokens per Second**: Based on total request time

### Live Display Features

- **Real-time updates**: Screen clears and updates with current metrics during benchmark
- **File output**: Results saved to `benchmark_output_YYYYMMDD_HHMMSS.txt` with:
  - Session header with service/model info
  - Per-prompt sections with metrics as key:value pairs
  - Full response text
  - Session summary
- **Live metrics**: Running calculations of token speeds and timing
- **Response streaming**: Shows response text as it's received (when available)

### Remote Server Features

- **Connection Types**: Local scanning or remote server connection
- **IP/URL Storage**: Previously used servers stored in `remote_servers.json`
- **API Authentication**: Optional API key support (memory-only, never saved)
- **Auto-detection**: Automatically detects service type (Ollama, vLLM, Llama.cpp) on remote servers
- **Connection Testing**: Tests server connectivity and service availability

## Future Development

- Additional prompt templates and categories
- Results export (CSV, JSON)
- Historical benchmark comparison
- Configuration profiles for different test scenarios
- Support for additional LLM services