#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Remote Server Configuration - Handles remote LLM server connections
"""

import json
import os
import requests
from typing import List, Dict, Optional
from urllib.parse import urlparse

class RemoteServerConfig:
    """Manages remote server configurations and connections"""
    
    def __init__(self):
        self.config_file = "remote_servers.json"
        self.stored_servers = self._load_stored_servers()
        self.current_api_key = None  # Memory only, never saved
    
    def _load_stored_servers(self) -> List[str]:
        """Load previously used server IPs/URLs from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                    return data.get('servers', [])
        except Exception as e:
            print(f"Warning: Could not load stored servers: {e}")
        return []
    
    def _save_stored_servers(self):
        """Save server list to file"""
        try:
            data = {'servers': self.stored_servers}
            with open(self.config_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save servers: {e}")
    
    def add_server(self, server_url: str):
        """Add a new server to the stored list"""
        # Normalize the URL
        if not server_url.startswith(('http://', 'https://')):
            server_url = f"http://{server_url}"
        
        # Remove duplicates and add to front of list
        if server_url in self.stored_servers:
            self.stored_servers.remove(server_url)
        self.stored_servers.insert(0, server_url)
        
        # Keep only last 10 servers
        self.stored_servers = self.stored_servers[:10]
        self._save_stored_servers()
    
    def display_server_menu(self) -> Optional[str]:
        """Display server selection menu and return selected server"""
        print(f"\n{'='*60}")
        print("SELECT REMOTE SERVER")
        print(f"{'='*60}")
        
        if self.stored_servers:
            print("Previously used servers:")
            for i, server in enumerate(self.stored_servers, 1):
                print(f"{i}. {server}")
            print()
        
        print("Options:")
        print("0. Enter new server IP/URL")
        if self.stored_servers:
            print("Or select from the list above")
        print("q. Return to main menu")
        
        while True:
            try:
                choice = input("\nEnter your choice: ").strip().lower()
                
                if choice == 'q':
                    return None
                elif choice == '0':
                    return self._prompt_for_new_server()
                else:
                    choice_num = int(choice)
                    if 1 <= choice_num <= len(self.stored_servers):
                        selected_server = self.stored_servers[choice_num - 1]
                        print(f"Selected: {selected_server}")
                        return selected_server
                    else:
                        print(f"Please enter a number between 0 and {len(self.stored_servers)}")
            
            except ValueError:
                print("Please enter a valid number or 'q' to quit")
            except KeyboardInterrupt:
                print("\nCancelled.")
                return None
    
    def _prompt_for_new_server(self) -> Optional[str]:
        """Prompt user for new server IP/URL"""
        print("\nEnter the server IP or URL:")
        print("Examples:")
        print("  192.168.1.100")
        print("  192.168.10.101:11434")
        print("  https://api.openai.com")
        print("  my-server.domain.com:8080")
        
        try:
            server_input = input("\nServer IP/URL: ").strip()
            
            if not server_input:
                print("No server entered.")
                return None
            
            # Add protocol if missing
            if not server_input.startswith(('http://', 'https://')):
                server_input = f"http://{server_input}"
            
            # Validate URL format
            try:
                parsed = urlparse(server_input)
                if not parsed.netloc:
                    print("Invalid URL format.")
                    return None
            except Exception:
                print("Invalid URL format.")
                return None
            
            self.add_server(server_input)
            print(f"Added server: {server_input}")
            return server_input
            
        except KeyboardInterrupt:
            print("\nCancelled.")
            return None
    
    def prompt_for_api_key(self, server_url: str) -> Optional[str]:
        """Prompt for API key (stored in memory only)"""
        print(f"\n{'='*60}")
        print(f"API KEY FOR: {server_url}")
        print(f"{'='*60}")
        print("Enter API key for authentication (optional):")
        print("- Leave blank and press Enter if no API key is needed")
        print("- API key will NOT be saved between runs")
        
        try:
            api_key = input("\nAPI Key (optional): ").strip()
            
            if api_key:
                self.current_api_key = api_key
                print("API key stored in memory for this session.")
            else:
                self.current_api_key = None
                print("No API key provided - requests will be sent without authentication.")
            
            return self.current_api_key
            
        except KeyboardInterrupt:
            print("\nCancelled.")
            return None
    
    def get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers for API requests"""
        headers = {'Content-Type': 'application/json'}
        
        if self.current_api_key:
            # Common API key header formats
            headers['Authorization'] = f'Bearer {self.current_api_key}'
            # Some services use different header names
            headers['X-API-Key'] = self.current_api_key
        
        return headers
    
    def test_server_connection(self, server_url: str) -> Dict:
        """Test connection to remote server and detect service type"""
        print(f"\nTesting connection to {server_url}...")
        
        # Try different endpoints to detect service type
        test_endpoints = [
            ('/api/tags', 'Ollama'),          # Ollama
            ('/v1/models', 'vLLM/OpenAI'),    # vLLM or OpenAI compatible
            ('/health', 'Llama.cpp'),         # Llama.cpp
            ('/completion', 'Llama.cpp'),     # Llama.cpp alternative
            ('/', 'Generic')                  # Generic test
        ]
        
        headers = self.get_auth_headers()
        
        for endpoint, service_type in test_endpoints:
            try:
                response = requests.get(f"{server_url}{endpoint}", 
                                      headers=headers, 
                                      timeout=10)
                
                if response.status_code in [200, 401, 403]:  # 401/403 means auth issue but server responds
                    print(f"✓ Server responding - Detected: {service_type}")
                    
                    # Determine actual service name based on successful endpoint
                    if endpoint == '/api/tags':
                        service_name = 'Ollama'
                    elif endpoint == '/v1/models':
                        service_name = 'vLLM'
                    elif endpoint in ['/health', '/completion']:
                        service_name = 'Llama.cpp'
                    else:
                        service_name = 'Remote LLM'
                    
                    return {
                        'name': service_name,
                        'host': server_url,
                        'api_responding': response.status_code == 200,
                        'process_running': False,  # N/A for remote
                        'status': 'Available' if response.status_code == 200 else f'Auth Required ({response.status_code})',
                        'remote': True,
                        'auth_headers': headers
                    }
                    
            except requests.exceptions.RequestException:
                continue
        
        print(f"✗ Could not connect to {server_url}")
        return {
            'name': 'Remote LLM',
            'host': server_url,
            'api_responding': False,
            'process_running': False,
            'status': 'Connection Failed',
            'remote': True,
            'auth_headers': headers
        }

def display_connection_type_menu() -> Optional[str]:
    """Display menu to select local or remote connection"""
    print(f"\n{'='*60}")
    print("LLMBench - Connection Type")
    print(f"{'='*60}")
    print("Select how you want to connect to LLM services:")
    print()
    print("1. Local - Scan for services running on this machine")
    print("2. Remote - Connect to a remote LLM server")
    print("q. Quit")
    
    while True:
        try:
            choice = input("\nEnter your choice (1-2) or 'q' to quit: ").strip().lower()
            
            if choice == 'q':
                return None
            elif choice == '1':
                return 'local'
            elif choice == '2':
                return 'remote'
            else:
                print("Please enter 1, 2, or 'q'")
        
        except KeyboardInterrupt:
            print("\nGoodbye!")
            return None

# Example usage for testing
if __name__ == "__main__":
    # Test the remote configuration functionality
    config = RemoteServerConfig()
    
    # Test connection type menu
    connection_type = display_connection_type_menu()
    print(f"Selected: {connection_type}")
    
    if connection_type == 'remote':
        # Test server selection
        server = config.display_server_menu()
        if server:
            print(f"Selected server: {server}")
            
            # Test API key prompt
            api_key = config.prompt_for_api_key(server)
            print(f"API key provided: {'Yes' if api_key else 'No'}")
            
            # Test server connection
            result = config.test_server_connection(server)
            print(f"Connection test result: {result}")