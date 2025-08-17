import subprocess
import sys
import os
import shutil

def install_and_build():
    """Install requirements and build with PyInstaller - Enhanced Version"""

    print("🔧 Installing requirements...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)

    print("🧹 Cleaning previous builds...")
    for folder in ["build", "dist", "__pycache__"]:
        if os.path.exists(folder):
            try:
                shutil.rmtree(folder)
                print(f"   ✓ Removed {folder}")
            except PermissionError:
                print(f"   ⚠️  Could not remove {folder} (in use). Build will continue...")
            except Exception as e:
                print(f"   ⚠️  Error removing {folder}: {e}. Build will continue...")

    # Remove any existing spec files
    for file in os.listdir("."):
        if file.endswith(".spec"):
            os.remove(file)

    print("📦 Building windowed executable...")

    # Get the site-packages path to ensure we find modules
    import site
    site_packages = site.getsitepackages()[0]
    print(f"Site packages: {site_packages}")

    cmd = [
        "pyinstaller",
        "--onefile",
        "--name=llmbench",
        
        # Keep console visible for better user experience
        "--console",
        
        # Force collect entire packages
        "--collect-all=requests",
        "--collect-all=urllib3", 
        "--collect-all=certifi",
        "--collect-all=charset_normalizer",
        "--collect-all=idna",
        "--collect-all=psutil",
        "--collect-all=dotenv",

        # Also add as hidden imports (belt and suspenders)
        "--hidden-import=requests",
        "--hidden-import=urllib3",
        "--hidden-import=certifi", 
        "--hidden-import=charset_normalizer",
        "--hidden-import=idna",
        "--hidden-import=psutil",
        "--hidden-import=dotenv",

        # Include our modules
        "--hidden-import=runllmbench",
        "--hidden-import=savellmbench",
        "--hidden-import=remoteconfig",
        "--hidden-import=custom_prompts",

        # Include data files
        "--add-data=.env;.",
        "--add-data=requirements.txt;.",

        # Build options
        "--clean",
        "--noconfirm",
        "--debug=imports",  # This will show what's being imported

        "llmbench.py"  # Build main app directly
    ]

    print("Command:", " ".join(cmd))
    result = subprocess.run(cmd)

    if result.returncode == 0:
        print("✅ Console build successful!")
        exe_path = "dist/llmbench.exe"
        if os.path.exists(exe_path):
            size_mb = os.path.getsize(exe_path) / 1024 / 1024
            print(f"📁 Executable: {exe_path}")
            print(f"📊 Size: {size_mb:.1f} MB")
            print("🪟  This executable provides:")
            print("   - Clean console interface")
            print("   - Full streaming benchmark experience")
            print("   - Real-time elapsed timer display")
        else:
            print("❌ Executable not found!")
            return False
    else:
        print("❌ Build failed!")
        return False

    return True

if __name__ == "__main__":
    install_and_build()