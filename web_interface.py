# web_interface.py (Optional Flask Web Interface)
from flask import Flask, request, jsonify, render_template_string
import asyncio
from main import NorthwindAIAgent
from config import config

app = Flask(__name__)

# Initialize AI agent
agent = None

@app.before_first_request
def initialize_agent():
    global agent
    agent = NorthwindAIAgent(config.openai_api_key)

@app.route('/')
def home():
    """Main interface"""
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Northwind AI Agent</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .container { max-width: 800px; margin: 0 auto; }
            .query-box { width: 100%; padding: 10px; margin: 10px 0; }
            .response { background: #f5f5f5; padding: 15px; margin: 10px 0; border-radius: 5px; }
            .loading { color: #666; font-style: italic; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 Northwind AI Agent</h1>
            <p>Ask questions about the Northwind database in natural language!</p>
            
            <form id="queryForm">
                <textarea id="query" class="query-box" rows="3" 
                         placeholder="e.g., What are the top 5 best-selling products?"></textarea>
                <br>
                <button type="submit">Ask AI Agent</button>
            </form>
            
            <div id="response" class="response" style="display: none;"></div>
        </div>
        
        <script>
            document.getElementById('queryForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                const query = document.getElementById('query').value;
                const responseDiv = document.getElementById('response');
                
                responseDiv.style.display = 'block';
                responseDiv.innerHTML = '<div class="loading">Processing your query...</div>';
                
                try {
                    const response = await fetch('/query', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ query: query })
                    });
                    
                    const data = await response.json();
                    responseDiv.innerHTML = `<pre>${data.response}</pre>`;
                } catch (error) {
                    responseDiv.innerHTML = `<div style="color: red;">Error: ${error.message}</div>`;
                }
            });
        </script>
    </body>
    </html>
    """)

@app.route('/query', methods=['POST'])
def query():
    """Handle AI agent queries"""
    data = request.get_json()
    user_query = data.get('query', '')
    
    if not user_query:
        return jsonify({'error': 'Query is required'}), 400
    
    try:
        # Run async function in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        response = loop.run_until_complete(agent.process_query(user_query))
        loop.close()
        
        return jsonify({'response': response})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/tables')
def list_tables():
    """List all database tables"""
    from plugins.database_plugin import DatabasePlugin
    db_plugin = DatabasePlugin()
    tables = db_plugin.list_tables()
    return jsonify({'tables': tables})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)

