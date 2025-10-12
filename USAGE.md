# 🚀 Quick Usage Guide

## Getting Started in 30 Seconds

1. **Navigate to the project**:
   ```bash
   cd ai-fact-check
   ```

2. **Start the application**:
   ```bash
   python start.py
   ```

3. **Open your browser** to the displayed URL (usually `http://localhost:5001`)

4. **Start fact-checking!** Type any claim like:
   - "The Earth is flat"
   - "Water boils at 100°C at sea level"
   - "Honey never spoils"

## What the Smart Starter Does

The `start.py` script automatically handles:

### ✅ Environment Setup
- Checks Python version (requires 3.8+)
- Creates virtual environment if needed
- Installs dependencies only if not already present

### 🔍 Smart Port Management
- Tries port 5001 first
- If busy, automatically finds next available port
- Displays the correct URL to open

### 🧪 Health Checks
- Runs basic tests to verify everything works
- Shows clear error messages if something fails

### 🚀 Application Launch
- Starts Flask in development mode
- Shows startup progress with emojis
- Handles Ctrl+C gracefully

## Example Output

```
🚀 AI Fact-Check Chatbot Starter
========================================
✅ Python 3.11.5 detected
✅ Virtual environment already exists
✅ Dependencies already installed
✅ All tests passed
⚠️  Port 5001 is busy, finding alternative...
🌐 Starting application on port 5001
🔗 Open your browser to: http://localhost:5001
📝 Press Ctrl+C to stop the server
----------------------------------------
```

## Troubleshooting

### Common Issues

**"Python version too old"**
- Install Python 3.8 or higher
- Use `python3 start.py` if you have multiple Python versions

**"Permission denied"**
- Run `chmod +x start.py` to make it executable
- Or use `python start.py` instead of `./start.py`

**"Port already in use"**
- The script automatically finds free ports
- If all ports 5001-5050 are busy, close other applications

**"Dependencies failed to install"**
- Check internet connection
- Try running `pip install --upgrade pip` first
- Use `python -m pip install -r requirements.txt` manually

### Manual Override

If you prefer manual control:

```bash
# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run application
python app.py
```

## Features Overview

### 🔍 Fact-Checking Classifications
- **✅ True**: Supported by evidence
- **❌ False**: Contradicts evidence
- **⚠️ Misleading**: Partially true, lacks context
- **❓ Unverifiable**: Insufficient evidence

### 🌐 Data Sources
- **Wikipedia API**: For factual context
- **HuggingFace AI**: For claim analysis
- **Smart Caching**: Faster repeat queries

### 💻 User Interface
- Clean, responsive chat design
- Real-time fact-checking
- Source links for verification
- Confidence scores for transparency

---

**Need help?** Check the main [README.md](README.md) for detailed documentation.
