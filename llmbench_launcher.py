#!/usr/bin/env python3
"""
LLMBench Windows Launcher - Hidden setup with separate benchmark window
"""

import os
import sys
import subprocess

def launch_in_new_window():
    """Launch LLMBench in a new console window"""
    
    print("Starting LLMBench...")
    
    try:        
        # Launch in new window
        if os.name == 'nt':  # Windows
            if getattr(sys, 'frozen', False):
                # We're running from a PyInstaller executable
                # Just run the main app directly in a new window
                cmd = [
                    'cmd', '/c', 'start', 
                    '"LLMBench - Benchmarking Tool"',  # Window title (quoted)
                    'cmd', '/k',  # Keep window open after execution
                    'echo 🚀 Welcome to LLMBench! &&',
                    'echo Benchmarking tool for Large Language Models &&',
                    'echo. &&',
                    'python', '-c', 
                    '"import sys; sys.path.insert(0, \'.\'); import llmbench; llmbench.main()"'
                ]
                
                # Run the command and hide this window
                subprocess.run(' '.join(cmd), shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
                
            else:
                # Running from Python script directly
                cmd = [
                    'cmd', '/c', 'start', 
                    '"LLMBench - Benchmarking Tool"',  # Window title
                    'cmd', '/k',  # Keep window open after execution
                    'python', 'llmbench.py'
                ]
                
                # Run the command and hide this window
                subprocess.run(' '.join(cmd), shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
            
        else:  # Linux/macOS fallback
            # Try various terminal emulators
            terminals = [
                ['gnome-terminal', '--', 'python3', 'llmbench.py'],
                ['xterm', '-e', 'python3', 'llmbench.py'],
                ['konsole', '-e', 'python3', 'llmbench.py'],
                ['Terminal', 'python3', 'llmbench.py']  # macOS
            ]
            
            for terminal_cmd in terminals:
                try:
                    subprocess.run(terminal_cmd, check=True)
                    break
                except (subprocess.CalledProcessError, FileNotFoundError):
                    continue
            else:
                # Fallback to current terminal
                print("Could not open new terminal window, running in current window...")
                subprocess.run(['python3', 'llmbench.py'])
        
        print("LLMBench launched in new window.")
        
    except Exception as e:
        print(f"Error launching LLMBench: {e}")
        print("Falling back to current window...")
        
        # Fallback: run in current window
        try:
            import llmbench
            return llmbench.main()
        except Exception as fallback_error:
            print(f"Fallback failed: {fallback_error}")
            return 1
    
    return 0

def main():
    """Main launcher entry point"""
    
    # Check if we're running from executable or script
    if getattr(sys, 'frozen', False):
        # Running from PyInstaller executable
        print("LLMBench Launcher - Starting...")
    
    try:
        return launch_in_new_window()
    except KeyboardInterrupt:
        print("\nLauncher interrupted.")
        return 0
    except Exception as e:
        print(f"Launcher error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())