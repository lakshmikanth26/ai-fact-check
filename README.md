# AI Fact-Check Chatbot 🔍

A modern web-based fact-checking chatbot that uses Wikipedia and AI to verify claims in real-time. Built with Flask, powered by HuggingFace's BART model for natural language inference.

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![Flask](https://img.shields.io/badge/flask-v2.3+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## 🌟 Features

- **Interactive Chat Interface**: Clean, responsive web UI with real-time messaging
- **AI-Powered Analysis**: Uses HuggingFace's BART-large-MNLI model for claim classification
- **Wikipedia Integration**: Automatically searches and retrieves relevant context
- **Smart Caching**: JSON-based caching system to improve performance
- **Classification System**: 
  - ✅ **True**: Claim is supported by evidence
  - ❌ **False**: Claim contradicts available evidence  
  - ⚠️ **Misleading**: Partially true but lacks context
  - ❓ **Unverifiable**: Insufficient evidence to verify
- **Source Attribution**: Links to Wikipedia sources for transparency
- **Confidence Scoring**: Shows AI confidence levels for each classification

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Super Quick Start

```bash
cd ai-fact-check
python run.py
```

The universal starter will handle everything automatically!

### Installation

#### Option 1: One-Click Start (Recommended)

1. **Navigate to the project directory**:
   ```bash
   cd ai-fact-check
   ```

2. **Run the universal starter script**:
   ```bash
   python run.py
   ```

The `run.py` script will automatically:
- ✅ Check Python version compatibility
- 📦 Create a virtual environment if needed
- 📥 Install dependencies if not already installed
- 🔍 Find an available port (starts with 5000)
- 🚀 Launch the application
- 🧪 Run tests to verify everything works

#### Option 2: Manual Setup

1. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python app.py
   ```

4. **Open your browser** and navigate to:
   ```
   http://localhost:5000
   ```

That's it! The chatbot is now running and ready to fact-check claims.

## 💬 Usage

1. **Start a conversation**: Type any claim you want to verify in the chat input
2. **Wait for analysis**: The bot will search Wikipedia and analyze the claim using AI
3. **Review results**: Get a classification, confidence score, explanation, and sources
4. **Explore sources**: Click on Wikipedia links to read the full articles

### Example Claims to Try

- "The Earth is flat"
- "Water boils at 100 degrees Celsius at sea level"
- "The Great Wall of China is visible from space"
- "Honey never spoils"
- "Lightning never strikes the same place twice"

## 🏗️ Project Structure

```
factcheck_chatbot/
├── app.py                 # Flask web application
├── factcheck.py          # Core fact-checking logic
├── requirements.txt       # Python dependencies
├── cache.json            # Query cache (auto-generated)
├── templates/
│   └── index.html        # Chat interface
├── static/
│   └── style.css         # Custom styles
├── .env.example          # Environment variables template
├── .gitignore           # Git ignore rules
└── README.md            # This file
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```bash
cp .env.example .env
```

Available configuration options:

```env
# Flask configuration
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
PORT=5000

# Cache configuration  
CACHE_EXPIRY_HOURS=24

# Wikipedia settings
WIKIPEDIA_LANGUAGE=en
WIKIPEDIA_SEARCH_LIMIT=3
```

### API Configuration

The chatbot uses free APIs that don't require authentication:

- **Wikipedia REST API**: No key required
- **HuggingFace Inference API**: Uses free tier (no auth needed)

For production use, consider getting a HuggingFace API key for better rate limits.

## 🧠 How It Works

### Fact-Checking Pipeline

1. **Claim Input**: User submits a claim through the web interface
2. **Wikipedia Search**: System searches for relevant articles using Wikipedia's REST API
3. **Context Extraction**: Retrieves and summarizes content from top search results
4. **AI Analysis**: Sends claim + context to HuggingFace BART-MNLI model
5. **Classification**: Model performs Natural Language Inference to classify the claim
6. **Response Generation**: Formats results with explanation and sources
7. **Caching**: Stores results to improve future response times

### Classification Logic

The system uses BART's Natural Language Inference capabilities:

- **ENTAILMENT** (>0.7 confidence) → **True**
- **CONTRADICTION** (>0.7 confidence) → **False**  
- **NEUTRAL** (>0.5 confidence) → **Unverifiable**
- **Mixed/Low confidence** → **Misleading**

## 🎨 Frontend Features

- **Responsive Design**: Works on desktop, tablet, and mobile
- **Real-time Chat**: Smooth messaging experience with typing indicators
- **Loading States**: Visual feedback during fact-checking process
- **Source Links**: Direct links to Wikipedia articles
- **Confidence Visualization**: Progress bars showing AI confidence
- **Character Limits**: Input validation and character counting
- **Accessibility**: Keyboard navigation and screen reader support

## 🔄 API Endpoints

### `GET /`
Returns the main chat interface.

### `POST /chat`
Processes fact-check requests.

**Request Body**:
```json
{
  "message": "Your claim to fact-check"
}
```

**Response**:
```json
{
  "message": "Formatted response with classification",
  "classification": "True|False|Misleading|Unverifiable",
  "confidence": 0.85,
  "sources": [
    {
      "title": "Article Title",
      "url": "https://en.wikipedia.org/wiki/...",
      "description": "Article description"
    }
  ],
  "timestamp": "2023-12-07T10:30:00"
}
```

### `GET /health`
Health check endpoint for monitoring.

## 🚀 Deployment

### Local Development

```bash
export FLASK_ENV=development
python app.py
```

### Production Deployment

1. **Set production environment**:
   ```bash
   export FLASK_ENV=production
   export SECRET_KEY=your-secure-secret-key
   ```

2. **Use a production WSGI server** (e.g., Gunicorn):
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

3. **Set up reverse proxy** (nginx recommended)

4. **Configure HTTPS** for secure communication

### Docker Deployment

Create a `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["python", "app.py"]
```

Build and run:
```bash
docker build -t factcheck-chatbot .
docker run -p 5000:5000 factcheck-chatbot
```

## 🔍 Troubleshooting

### Common Issues

**HuggingFace API Errors**:
- The model may take time to load (503 errors are normal initially)
- Free tier has rate limits - consider upgrading for production use

**Wikipedia API Issues**:
- Check internet connection
- Some queries may return no results (this is normal)

**Cache Issues**:
- Delete `cache.json` to clear all cached results
- Check file permissions if cache isn't saving

**Performance Issues**:
- Increase cache expiry time in `.env`
- Consider using Redis for production caching
- Implement request queuing for high traffic

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **HuggingFace** for providing free AI model inference
- **Wikipedia** for open access to knowledge
- **Flask** community for the excellent web framework
- **Tailwind CSS** for beautiful, responsive styling

## 📞 Support

If you encounter any issues or have questions:

1. Check the [troubleshooting section](#-troubleshooting)
2. Search existing issues on GitHub
3. Create a new issue with detailed information

## 🔮 Future Enhancements

- [ ] Support for multiple languages
- [ ] Integration with additional fact-checking sources
- [ ] User authentication and history
- [ ] Advanced caching with Redis
- [ ] Real-time collaboration features
- [ ] Mobile app version
- [ ] API rate limiting and authentication
- [ ] Advanced analytics and reporting

---

**Built with ❤️ using Python, Flask, and AI**
