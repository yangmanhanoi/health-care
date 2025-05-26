from flask import Flask
from routes.forwarder import router
from flask_cors import CORS 

app = Flask(__name__)
CORS(app, resources={r"/svc-*/*": {"origins": "*"}}, supports_credentials=True)
app.register_blueprint(router)

if __name__ == "__main__":
    app.run(port=8080, debug=True, host="0.0.0.0")