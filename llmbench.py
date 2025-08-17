#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLMBench - A benchmarking tool for LLM services
"""

import os
import subprocess
import requests
import psutil
from dotenv import load_dotenv
from typing import List, Dict, Optional
import sys
import time
from remoteconfig import RemoteServerConfig, display_connection_type_menu

# Load environment variables
load_dotenv()

class ServiceDetector:
    """Detects available LLM services on the system"""
    
    def __init__(self):
        self.ollama_host = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
        self.vllm_host = os.getenv('VLLM_HOST', 'http://localhost:8000')
        self.llamacpp_host = os.getenv('LLAMACPP_HOST', 'http://localhost:8080')
        self.timeout = int(os.getenv('TIMEOUT_SECONDS', '180'))
    
    def check_process_running(self, process_names: List[str]) -> bool:
        """Check if any of the given process names are running"""
        for proc in psutil.process_iter(['name', 'cmdline']):
            try:
                proc_info = proc.info
                if proc_info['name'] and any(name.lower() in proc_info['name'].lower() for name in process_names):
                    return True
                if proc_info['cmdline']:
                    cmdline_str = ' '.join(proc_info['cmdline']).lower()
                    if any(name.lower() in cmdline_str for name in process_names):
                        return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return False
    
    def check_service_health(self, url: str, health_endpoint: str = "/health") -> bool:
        """Check if a service is healthy via HTTP request"""
        try:
            response = requests.get(f"{url}{health_endpoint}", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def check_ollama_api(self) -> bool:
        """Check if Ollama API is responding"""
        try:
            response = requests.get(f"{self.ollama_host}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def detect_ollama(self) -> Optional[Dict]:
        """Detect Ollama service"""
        process_running = self.check_process_running(['ollama'])
        api_responding = self.check_ollama_api()
        
        if process_running or api_responding:
            return {
                'name': 'Ollama',
                'host': self.ollama_host,
                'process_running': process_running,
                'api_responding': api_responding,
                'status': 'Available' if api_responding else 'Process Running (API not responding)'
            }
        return None
    
    def detect_vllm(self) -> Optional[Dict]:
        """Detect vLLM service"""
        process_running = self.check_process_running(['vllm', 'python -m vllm'])
        api_responding = self.check_service_health(self.vllm_host, "/v1/models")
        
        if process_running or api_responding:
            return {
                'name': 'vLLM',
                'host': self.vllm_host,
                'process_running': process_running,
                'api_responding': api_responding,
                'status': 'Available' if api_responding else 'Process Running (API not responding)'
            }
        return None
    
    def detect_llamacpp(self) -> Optional[Dict]:
        """Detect llama.cpp service"""
        process_running = self.check_process_running(['llama-server', 'llama.cpp', 'server'])
        api_responding = self.check_service_health(self.llamacpp_host, "/health")
        
        if process_running or api_responding:
            return {
                'name': 'Llama.cpp',
                'host': self.llamacpp_host,
                'process_running': process_running,
                'api_responding': api_responding,
                'status': 'Available' if api_responding else 'Process Running (API not responding)'
            }
        return None
    
    def detect_all_services(self) -> List[Dict]:
        """Detect all available LLM services"""
        services = []
        
        # Check each service
        ollama = self.detect_ollama()
        if ollama:
            services.append(ollama)
        
        vllm = self.detect_vllm()
        if vllm:
            services.append(vllm)
        
        llamacpp = self.detect_llamacpp()
        if llamacpp:
            services.append(llamacpp)
        
        return services

class ServiceMenu:
    """Interactive terminal menu for service selection"""
    
    def __init__(self, services: List[Dict]):
        self.services = services
    
    def display_services(self):
        """Display available services"""
        print("\n" + "="*60)
        print("LLMBench - Available LLM Services")
        print("="*60)
        
        if not self.services:
            print("No LLM services detected!")
            print("\nPlease ensure one of the following is running:")
            print("  - Ollama (default: http://localhost:11434)")
            print("  - vLLM (default: http://localhost:8000)")
            print("  - Llama.cpp server (default: http://localhost:8080)")
            return None
        
        for i, service in enumerate(self.services, 1):
            status_icon = "[OK]" if service['api_responding'] else "[PROC]"
            print(f"{i}. {status_icon} {service['name']}")
            print(f"   Host: {service['host']}")
            print(f"   Status: {service['status']}")
            print()
        
        return self.get_user_choice()
    
    def get_user_choice(self) -> Optional[Dict]:
        """Get user's service selection"""
        while True:
            try:
                print(f"Enter your choice (1-{len(self.services)}) or 'q' to quit: ", end="")
                choice = input().strip().lower()
                
                if choice == 'q':
                    print("Goodbye!")
                    return None
                
                choice_num = int(choice)
                if 1 <= choice_num <= len(self.services):
                    selected_service = self.services[choice_num - 1]
                    print(f"\nSelected: {selected_service['name']} at {selected_service['host']}")
                    return selected_service
                else:
                    print(f"Please enter a number between 1 and {len(self.services)}")
            
            except ValueError:
                print("Please enter a valid number or 'q' to quit")
            except KeyboardInterrupt:
                print("\nGoodbye!")
                return None

class ModelSelector:
    """Handles model selection for LLM services"""
    
    def __init__(self, service_info: Dict):
        self.service_info = service_info
        self.service_name = service_info['name']
        self.host = service_info['host']
    
    def get_available_models(self) -> List[str]:
        """Query the service for available models"""
        try:
            if self.service_name == "Ollama":
                return self._get_ollama_models()
            elif self.service_name == "vLLM":
                return self._get_vllm_models()
            elif self.service_name == "Llama.cpp":
                return self._get_llamacpp_models()
            else:
                print(f"Model listing not implemented for {self.service_name}")
                return []
        except Exception as e:
            print(f"Error fetching models from {self.service_name}: {e}")
            return []
    
    def _get_ollama_models(self) -> List[str]:
        """Get models from Ollama API"""
        headers = self.service_info.get('auth_headers', {})
        response = requests.get(f"{self.host}/api/tags", headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        models = []
        for model in data.get('models', []):
            models.append(model.get('name', 'unknown'))
        
        return models
    
    def _get_vllm_models(self) -> List[str]:
        """Get models from vLLM API"""
        headers = self.service_info.get('auth_headers', {})
        response = requests.get(f"{self.host}/v1/models", headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        models = []
        for model in data.get('data', []):
            models.append(model.get('id', 'unknown'))
        
        return models
    
    def _get_llamacpp_models(self) -> List[str]:
        """Get models from Llama.cpp API"""
        # Llama.cpp typically serves one model at a time
        # Try to get model info from the /props endpoint
        headers = self.service_info.get('auth_headers', {})
        try:
            response = requests.get(f"{self.host}/props", headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                model_name = data.get('default_generation_settings', {}).get('model', 'current_model')
                return [model_name]
        except:
            pass
        
        # Fallback: return a generic name since llama.cpp serves whatever model was loaded
        return ["current_model"]
    
    def display_model_menu(self) -> Optional[str]:
        """Display model selection menu and return selected model"""
        print(f"\n{'='*60}")
        print(f"SELECT MODEL - {self.service_name}")
        print(f"{'='*60}")
        
        if not self.service_info.get('api_responding', False):
            print(f"Warning: {self.service_name} API is not responding.")
            print("Cannot fetch model list. Using default model.")
            return "default"
        
        print("Fetching available models...")
        models = self.get_available_models()
        
        if not models:
            print("No models found or API error.")
            print("Using default model.")
            return "default"
        
        print(f"\nAvailable models:")
        for i, model in enumerate(models, 1):
            print(f"{i}. {model}")
        
        print("0. Cancel and return to main menu")
        
        while True:
            try:
                print(f"\nEnter your choice (1-{len(models)}) or 0 to cancel: ", end="")
                choice = input().strip()
                
                if choice == '0':
                    return None
                
                choice_num = int(choice)
                if 1 <= choice_num <= len(models):
                    selected_model = models[choice_num - 1]
                    print(f"\nSelected model: {selected_model}")
                    return selected_model
                else:
                    print(f"Please enter a number between 1 and {len(models)}")
            
            except ValueError:
                print("Please enter a valid number")
            except KeyboardInterrupt:
                print("\nCancelled.")
                return None

def main():
    """Main application entry point"""
    
    # First, ask for connection type
    connection_type = display_connection_type_menu()
    if not connection_type:
        return 0
    
    services = []
    
    if connection_type == 'local':
        print("Detecting local LLM services...")
        
        # Detect available local services
        detector = ServiceDetector()
        services = detector.detect_all_services()
        
    elif connection_type == 'remote':
        print("Setting up remote server connection...")
        
        # Handle remote server configuration
        remote_config = RemoteServerConfig()
        server_url = remote_config.display_server_menu()
        
        if not server_url:
            print("No server selected.")
            return 0
        
        # Prompt for API key
        api_key = remote_config.prompt_for_api_key(server_url)
        
        # Test connection and create service info
        service_info = remote_config.test_server_connection(server_url)
        services = [service_info] if service_info else []
    
    # Display menu and get user selection
    menu = ServiceMenu(services)
    selected_service = menu.display_services()
    
    if selected_service:
        print(f"\nSelected service: {selected_service['name']} at {selected_service['host']}")
        
        # Model selection step
        model_selector = ModelSelector(selected_service)
        selected_model = model_selector.display_model_menu()
        
        if not selected_model:
            print("No model selected. Returning to main menu.")
            return 0
        
        # Add selected model to service info
        selected_service['selected_model'] = selected_model
        
        print(f"\nReady to benchmark {selected_service['name']} with model: {selected_model}")
        
        # Import and run the benchmarking module
        try:
            import runllmbench
            runllmbench.run_benchmark(selected_service)
        except ImportError:
            print("Error: runllmbench.py not found!")
            return 1
        except Exception as e:
            print(f"Error running benchmark: {e}")
            return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())