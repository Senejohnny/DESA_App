# Run a test server.
from app import app
if __name__ == "__main__":
    app.run(host='127.0.0.1', port=4001, debug=True)
    # app.run(port=5002 , debug=True)