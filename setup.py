#!/usr/bin/env python3
"""
LLMBench Setup Script - Automatic virtual environment setup and launcher
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path
import getpass

class LLMBenchSetup:
    def __init__(self):
        self.is_windows = platform.system() == "Windows"
        self.current_user = getpass.getuser()
        self.python_cmd = "python" if self.is_windows else "python3"
        
        # Determine installation directory based on platform
        if self.is_windows:
            # Windows: Documents/LLMBench
            documents_dir = Path.home() / "Documents"
            self.install_dir = documents_dir / "LLMBench"
        else:
            # Linux/macOS: ~/LLMBench
            self.install_dir = Path.home() / "LLMBench"
        
        # Source directory (where this script is located)
        self.source_dir = Path(__file__).parent.absolute()
        self.venv_dir = self.install_dir / "venv"
        
        # Virtual environment paths
        if self.is_windows:
            self.venv_python = self.venv_dir / "Scripts" / "python.exe"
            self.venv_pip = self.venv_dir / "Scripts" / "pip.exe"
            self.activate_script = self.venv_dir / "Scripts" / "activate.bat"
        else:
            self.venv_python = self.venv_dir / "bin" / "python"
            self.venv_pip = self.venv_dir / "bin" / "pip"
            self.activate_script = self.venv_dir / "bin" / "activate"
    
    def copy_source_files(self):
        """Copy source files to installation directory"""
        print(f"📁 Installing to {self.install_dir}")
        
        # Create installation directory
        self.install_dir.mkdir(parents=True, exist_ok=True)
        
        # Files to copy
        source_files = [
            "llmbench.py", "runllmbench.py", "savellmbench.py", 
            "remoteconfig.py", "custom_prompts.py", "requirements.txt", ".env", "README.md"
        ]
        
        print("📋 Copying source files...")
        for file_name in source_files:
            source_file = self.source_dir / file_name
            dest_file = self.install_dir / file_name
            
            if source_file.exists():
                shutil.copy2(source_file, dest_file)
                print(f"   ✓ {file_name}")
            else:
                print(f"   ⚠️  {file_name} not found (optional)")
        
        return True
    
    def check_python(self):
        """Check if Python is available"""
        try:
            result = subprocess.run([self.python_cmd, "--version"], 
                                  capture_output=True, text=True, check=True)
            version = result.stdout.strip()
            print(f"✓ Found {version}")
            
            # Check minimum version (3.8+)
            version_parts = version.split()[1].split('.')
            major, minor = int(version_parts[0]), int(version_parts[1])
            if major < 3 or (major == 3 and minor < 8):
                print(f"❌ Python 3.8+ required, found {version}")
                return False
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(f"❌ Python not found. Please install Python 3.8+ and add it to PATH")
            return False
    
    def create_venv(self):
        """Create virtual environment"""
        print(f"📦 Creating virtual environment in {self.venv_dir}")
        
        # Remove existing venv if it exists
        if self.venv_dir.exists():
            print("🗑️  Removing existing virtual environment...")
            shutil.rmtree(self.venv_dir)
        
        # Create new venv
        try:
            subprocess.run([self.python_cmd, "-m", "venv", str(self.venv_dir)], 
                          check=True)
            print("✓ Virtual environment created")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create virtual environment: {e}")
            return False
    
    def install_dependencies(self):
        """Install required packages in virtual environment"""
        print("📥 Installing dependencies...")
        
        requirements_file = self.install_dir / "requirements.txt"
        if not requirements_file.exists():
            print("❌ requirements.txt not found")
            return False
        
        try:
            subprocess.run([str(self.venv_pip), "install", "-r", str(requirements_file)], 
                          check=True)
            print("✓ Dependencies installed")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            return False
    
    def create_launcher_scripts(self):
        """Create launcher scripts for easy execution"""
        print("🚀 Creating launcher scripts...")
        
        if self.is_windows:
            # Windows batch file
            launcher_content = f"""@echo off
cd /d "{self.install_dir}"
call "{self.activate_script}"
python llmbench.py %*
"""
            launcher_path = self.install_dir / "llmbench.bat"
            with open(launcher_path, "w") as f:
                f.write(launcher_content)
            
            # PowerShell script
            ps_content = f"""Set-Location "{self.install_dir}"
& "{self.activate_script}"
& python llmbench.py $args
"""
            ps_path = self.install_dir / "llmbench.ps1"
            with open(ps_path, "w") as f:
                f.write(ps_content)
            
            # Create global launcher script in user directory
            global_launcher = Path.home() / "llmbench.bat"
            global_content = f"""@echo off
cd /d "{self.install_dir}"
call llmbench.bat %*
"""
            with open(global_launcher, "w") as f:
                f.write(global_content)
            
            print("✓ Created llmbench.bat and llmbench.ps1")
            print(f"✓ Created global launcher: {global_launcher}")
            
        else:
            # Linux/macOS shell script
            launcher_content = f"""#!/bin/bash
cd "{self.install_dir}"
source "{self.activate_script}"
python llmbench.py "$@"
"""
            launcher_path = self.install_dir / "llmbench"
            with open(launcher_path, "w") as f:
                f.write(launcher_content)
            
            # Make executable
            os.chmod(launcher_path, 0o755)
            
            # Create global launcher in user's local bin
            local_bin = Path.home() / ".local" / "bin"
            local_bin.mkdir(parents=True, exist_ok=True)
            global_launcher = local_bin / "llmbench"
            
            global_content = f"""#!/bin/bash
cd "{self.install_dir}"
exec ./llmbench "$@"
"""
            with open(global_launcher, "w") as f:
                f.write(global_content)
            os.chmod(global_launcher, 0o755)
            
            print("✓ Created llmbench launcher script")
            print(f"✓ Created global launcher: {global_launcher}")
        
        return True
    
    def setup(self):
        """Complete setup process"""
        print("🔧 LLMBench Setup Starting...")
        print(f"📁 Source directory: {self.source_dir}")
        print(f"📂 Install directory: {self.install_dir}")
        print(f"👤 Current user: {self.current_user}")
        print(f"🖥️  Platform: {platform.system()}")
        print()
        
        # Check Python
        if not self.check_python():
            return False
        
        # Copy source files to installation directory
        if not self.copy_source_files():
            return False
        
        # Create virtual environment
        if not self.create_venv():
            return False
        
        # Install dependencies
        if not self.install_dependencies():
            return False
        
        # Create launcher scripts
        if not self.create_launcher_scripts():
            return False
        
        print()
        print("🎉 Setup completed successfully!")
        print()
        print("📋 How to run LLMBench:")
        
        if self.is_windows:
            print(f"   From anywhere:          llmbench")
            print(f"   Windows Command Prompt: {self.install_dir}\\llmbench.bat")
            print(f"   Windows PowerShell:     {self.install_dir}\\llmbench.ps1")
            print(f"   Direct Python:          {self.venv_python} {self.install_dir}\\llmbench.py")
        else:
            print(f"   From anywhere:          llmbench")
            print(f"   Linux/macOS:            {self.install_dir}/llmbench")
            print(f"   Direct Python:          {self.venv_python} {self.install_dir}/llmbench.py")
        
        print()
        print("📁 Installation details:")
        print(f"   Installation directory: {self.install_dir}")
        print(f"   Virtual environment:    {self.venv_dir}")
        if self.is_windows:
            print(f"   Global launcher:        {Path.home()}/llmbench.bat")
        else:
            print(f"   Global launcher:        {Path.home()}/.local/bin/llmbench")
            print("   (Make sure ~/.local/bin is in your PATH)")
        
        return True
    
    def run_benchmark(self):
        """Run the benchmark application"""
        try:
            subprocess.run([str(self.venv_python), "llmbench.py"] + sys.argv[2:])
        except KeyboardInterrupt:
            print("\n👋 LLMBench interrupted by user")
        except Exception as e:
            print(f"❌ Error running LLMBench: {e}")

def main():
    setup = LLMBenchSetup()
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python setup.py --setup     Setup virtual environment and dependencies")
        print("  python setup.py --run       Run LLMBench in virtual environment")
        print("  python setup.py --help      Show this help message")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "--setup":
        success = setup.setup()
        sys.exit(0 if success else 1)
    
    elif command == "--run":
        if not setup.venv_dir.exists():
            print("❌ Virtual environment not found. Run 'python setup.py --setup' first.")
            sys.exit(1)
        setup.run_benchmark()
    
    elif command == "--help":
        print("LLMBench Setup Script")
        print()
        print("Commands:")
        print("  --setup    Create virtual environment and install dependencies")
        print("  --run      Run LLMBench in the virtual environment")
        print("  --help     Show this help message")
        print()
        print("After setup, you can also run:")
        if platform.system() == "Windows":
            print("  llmbench.bat    (Windows Command Prompt)")
            print("  .\\llmbench.ps1  (Windows PowerShell)")
        else:
            print("  ./llmbench      (Linux/macOS)")
    
    else:
        print(f"❌ Unknown command: {command}")
        print("Use 'python setup.py --help' for usage information")
        sys.exit(1)

if __name__ == "__main__":
    main()