#!/usr/bin/env python3
"""
Setup script for Ollama integration
This script helps users set up Ollama for the logic set bot
"""

import subprocess
import sys
import platform
import requests
import time

def check_ollama_installed():
    """Check if Ollama is installed"""
    try:
        result = subprocess.run(['ollama', '--version'], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def install_ollama():
    """Install Ollama based on the operating system"""
    system = platform.system().lower()
    
    print("Installing Ollama...")
    
    if system == "windows":
        print("Please download and install Ollama from: https://ollama.ai/download")
        print("After installation, restart your terminal and run this script again.")
        return False
    elif system == "darwin":  # macOS
        subprocess.run(['curl', '-fsSL', 'https://ollama.ai/install.sh', '|', 'sh'], shell=True)
    elif system == "linux":
        subprocess.run(['curl', '-fsSL', 'https://ollama.ai/install.sh', '|', 'sh'], shell=True)
    else:
        print(f"Unsupported operating system: {system}")
        return False
    
    return True

def check_ollama_running():
    """Check if Ollama service is running"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        return response.status_code == 200
    except:
        return False

def start_ollama():
    """Start Ollama service"""
    print("Starting Ollama service...")
    try:
        subprocess.Popen(['ollama', 'serve'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(3)  # Wait for service to start
        return True
    except:
        return False

def pull_model(model_name="llama3.2"):
    """Pull the required model"""
    print(f"Pulling model {model_name}...")
    try:
        subprocess.run(['ollama', 'pull', model_name], check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    print("Setting up Ollama for Logic Set Bot...")
    print("=" * 50)
    
    # Check if Ollama is installed
    if not check_ollama_installed():
        print("Ollama is not installed.")
        if not install_ollama():
            print("Please install Ollama manually and run this script again.")
            return False
    else:
        print("✓ Ollama is installed")
    
    # Check if Ollama is running
    if not check_ollama_running():
        print("Ollama service is not running. Starting it...")
        if not start_ollama():
            print("Failed to start Ollama service. Please start it manually.")
            return False
    else:
        print("✓ Ollama service is running")
    
    # Pull the required model
    if not pull_model():
        print("Failed to pull the model. Please run 'ollama pull llama3.2' manually.")
        return False
    else:
        print("✓ Model pulled successfully")
    
    print("\n" + "=" * 50)
    print("✓ Ollama setup completed successfully!")
    print("You can now run the bot with: python run_bot.py")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
