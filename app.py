"""
Flask web application for the fact-checking chatbot.
Provides a web interface for users to submit claims and receive fact-check results.
"""

from flask import Flask, render_template, request, jsonify
from factcheck import FactChecker
import os
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')

# Initialize fact checker
fact_checker = FactChecker()

@app.route('/')
def index():
    """Render the main chat interface."""
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat requests and return fact-check results."""
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({
                'error': 'No message provided'
            }), 400
        
        claim = data['message'].strip()
        
        if not claim:
            return jsonify({
                'error': 'Empty message provided'
            }), 400
        
        if len(claim) > 500:
            return jsonify({
                'error': 'Message too long. Please limit to 500 characters.'
            }), 400
        
        # Perform fact check
        result = fact_checker.fact_check(claim)
        
        # Format response for the chat interface
        response = {
            'message': format_fact_check_response(result),
            'classification': result['classification'],
            'confidence': result['confidence'],
            'sources': result['sources'],
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(response)
        
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        return jsonify({
            'error': 'An error occurred while processing your request. Please try again.'
        }), 500

def format_fact_check_response(result):
    """Format the fact-check result into a user-friendly message."""
    classification = result['classification']
    explanation = result['explanation']
    sources = result['sources']
    
    # Classification emoji mapping
    emoji_map = {
        'True': '✅',
        'False': '❌',
        'Misleading': '⚠️',
        'Unverifiable': '❓'
    }
    
    emoji = emoji_map.get(classification, '❓')
    
    # Build response message
    message = f"{emoji} **{classification}**\n\n"
    message += f"{explanation}\n\n"
    
    if sources:
        message += "**Sources:**\n"
        for i, source in enumerate(sources[:4], 1):  # Show up to 4 sources
            title = source.get('title', 'Unknown')
            url = source.get('url', '#')
            description = source.get('description', '')
            source_type = source.get('source', 'Wikipedia')
            
            # Add emoji based on source type
            emoji = "🌐" if source_type == "Google Search" else "📖"
            
            message += f"{i}. {emoji} [{title}]({url})"
            if description:
                message += f" - {description}"
            message += "\n"
    else:
        message += "*No sources found for verification.*"
    
    return message

@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Create cache directory if it doesn't exist
    os.makedirs('cache', exist_ok=True)
    
    # Run the app
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    print(f"Starting Fact-Check Chatbot on port {port}")
    print(f"Debug mode: {debug}")
    print(f"Visit http://localhost:{port} to use the chatbot")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
