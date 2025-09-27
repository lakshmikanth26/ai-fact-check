#!/usr/bin/env python3
"""
🚀 AI Fact-Check Chatbot - Universal Starter
Comprehensive startup script with automatic setup and smart port management.
"""

import os
import sys
import subprocess
import socket
import platform
import time
import signal
from pathlib import Path

class FactCheckStarter:
    def __init__(self):
        self.project_dir = Path(__file__).parent
        self.venv_dir = self.project_dir / "venv"
        self.requirements_file = self.project_dir / "requirements.txt"
        self.app_file = self.project_dir / "app.py"
        self.is_windows = platform.system() == "Windows"
        
    def print_banner(self):
        """Print startup banner."""
        print("🚀 AI Fact-Check Chatbot - Universal Starter")
        print("=" * 50)
        print("✨ Automatic setup, smart port management, enhanced sources")
        print()
        
    def check_python_version(self):
        """Check if Python version is compatible."""
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            print("❌ Error: Python 3.8 or higher is required")
            print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
            sys.exit(1)
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
        
    def create_virtual_environment(self):
        """Create virtual environment if it doesn't exist."""
        if self.venv_dir.exists():
            print("✅ Virtual environment already exists")
            return True
            
        print("📦 Creating virtual environment...")
        try:
            subprocess.run([
                sys.executable, "-m", "venv", str(self.venv_dir)
            ], check=True, capture_output=True)
            print("✅ Virtual environment created successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create virtual environment: {e}")
            return False
            
    def get_venv_python(self):
        """Get path to Python executable in virtual environment."""
        if self.is_windows:
            return self.venv_dir / "Scripts" / "python.exe"
        else:
            return self.venv_dir / "bin" / "python"
            
    def get_venv_pip(self):
        """Get path to pip executable in virtual environment."""
        if self.is_windows:
            return self.venv_dir / "Scripts" / "pip.exe"
        else:
            return self.venv_dir / "bin" / "pip"
            
    def check_requirements_installed(self):
        """Check if requirements are already installed."""
        if not self.requirements_file.exists():
            print("⚠️  requirements.txt not found")
            return True
            
        pip_path = self.get_venv_pip()
        if not pip_path.exists():
            return False
            
        try:
            # Check if Flask is installed (main dependency)
            result = subprocess.run([
                str(pip_path), "show", "Flask"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Dependencies already installed")
                return True
            else:
                return False
        except Exception:
            return False
            
    def install_requirements(self):
        """Install requirements in virtual environment."""
        if not self.requirements_file.exists():
            print("⚠️  No requirements.txt found, skipping dependency installation")
            return True
            
        if self.check_requirements_installed():
            return True
            
        print("📥 Installing dependencies (this may take a moment)...")
        pip_path = self.get_venv_pip()
        
        try:
            # Upgrade pip first
            subprocess.run([
                str(pip_path), "install", "--upgrade", "pip"
            ], check=True, capture_output=True)
            
            # Install requirements
            result = subprocess.run([
                str(pip_path), "install", "-r", str(self.requirements_file)
            ], check=True, capture_output=True, text=True)
            
            print("✅ Dependencies installed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            if e.stdout:
                print(f"   Output: {e.stdout}")
            if e.stderr:
                print(f"   Error: {e.stderr}")
            return False
    
    def check_port_available(self, port):
        """Check if a port is available."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind(('127.0.0.1', port))
                return True
        except OSError:
            return False
    
    def find_free_port(self, start_port=5000):
        """Find the first available port starting from start_port."""
        for port in range(start_port, start_port + 50):
            if self.check_port_available(port):
                return port
        return None
    
    def kill_processes_on_port(self, port):
        """Kill processes using the specified port (Unix/macOS only)."""
        if self.is_windows:
            return False
            
        try:
            result = subprocess.run(['lsof', '-ti', f':{port}'], 
                                  capture_output=True, text=True)
            if result.returncode == 0 and result.stdout.strip():
                pids = result.stdout.strip().split('\n')
                for pid in pids:
                    try:
                        subprocess.run(['kill', '-9', pid], check=True)
                        print(f"   🔄 Killed process {pid} on port {port}")
                    except:
                        pass
                time.sleep(1)
                return True
        except:
            pass
        return False
    
    def run_quick_test(self):
        """Run a quick test to verify the system works."""
        print("🧪 Running quick system test...")
        python_path = self.get_venv_python()
        
        try:
            test_code = '''
from factcheck import FactChecker
fc = FactChecker()
result = fc.fact_check("Test claim")
print("✅ System test passed")
'''
            
            result = subprocess.run([
                str(python_path), "-c", test_code
            ], cwd=str(self.project_dir), capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                print("✅ System test passed")
                return True
            else:
                print("⚠️  System test had issues, but continuing...")
                return True
                
        except Exception as e:
            print(f"⚠️  Could not run system test: {e}")
            return True
    
    def start_application(self):
        """Start the Flask application with smart port management."""
        if not self.app_file.exists():
            print(f"❌ Application file not found: {self.app_file}")
            return False
        
        print("🔍 Finding available port...")
        default_port = 5000
        
        # Try to free up the default port
        if not self.check_port_available(default_port):
            print(f"⚠️  Port {default_port} is busy")
            if self.kill_processes_on_port(default_port):
                print(f"   ✅ Freed up port {default_port}")
                port = default_port
            else:
                print("   💡 Tip: On macOS, this might be AirPlay Receiver")
                print("   🔍 Finding alternative port...")
                port = self.find_free_port(default_port + 1)
                if port is None:
                    print("❌ No available ports found!")
                    return False
                print(f"   ✅ Using port {port}")
        else:
            port = default_port
            print(f"✅ Port {port} is available")
        
        print()
        print("🚀 Starting AI Fact-Check Chatbot")
        print(f"🔗 Open your browser to: http://localhost:{port}")
        print("📝 Press Ctrl+C to stop the server")
        print("🌟 Features: Wikipedia + Google search, AI classification, location verification")
        print("-" * 50)
        
        python_path = self.get_venv_python()
        
        # Set environment variables
        env = os.environ.copy()
        env['PORT'] = str(port)
        env['FLASK_ENV'] = 'development'
        
        try:
            # Start the application
            subprocess.run([
                str(python_path), str(self.app_file)
            ], env=env, cwd=str(self.project_dir))
            return True
            
        except KeyboardInterrupt:
            print("\n👋 Application stopped by user")
            return True
        except Exception as e:
            print(f"❌ Error running application: {e}")
            return False
    
    def run(self):
        """Main startup sequence."""
        self.print_banner()
        
        # Step 1: Check prerequisites
        self.check_python_version()
        
        # Step 2: Setup virtual environment
        if not self.create_virtual_environment():
            return False
            
        # Step 3: Install dependencies
        if not self.install_requirements():
            return False
            
        # Step 4: Quick system test
        self.run_quick_test()
        
        # Step 5: Start application
        return self.start_application()

def main():
    """Main entry point."""
    try:
        starter = FactCheckStarter()
        success = starter.run()
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n👋 Startup cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
