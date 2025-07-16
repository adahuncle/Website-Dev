from flask import Flask, render_template
from flask_cors import CORS
from routes.search import search_bp
from routes.dropdowns import dropdown_bp
from routes.plot import plot_bp

app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)

# Register Blueprints
app.register_blueprint(search_bp)
app.register_blueprint(dropdown_bp)
app.register_blueprint(plot_bp)

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=False)
