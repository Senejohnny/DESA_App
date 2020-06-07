# Run a test server.
from app import app
app.run(host='127.0.0.1', port=8080, debug=True)
if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5002, debug=True)
    # app.run(port=5002 , debug=True)
    app.run
