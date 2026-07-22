"""
Local Dev Server for testing - Serves static files & API on http://localhost:8080
"""
from api.index import app

if __name__ == '__main__':
    print("Starting local testing server on http://127.0.0.1:8080...")
    app.run(host='127.0.0.1', port=8080, debug=False, threaded=True)
