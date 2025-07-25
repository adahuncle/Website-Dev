# Mixer Data Review Tool

This Flask-based web application allows users to search, visualize, and review mixer batch data for quality control and production analysis. It includes dynamic filters, plotting capabilities, and a streamlined interface built with HTML/CSS/JavaScript and Plotly.

---

## Features

- Search batch data using multiple filters (e.g., compound, downtime reason, date range)
- Interactive Plotly-based signal visualizations
- SQL database integration with MySQL Connector
- Responsive frontend built using Select2 and jQuery
- Easily extensible with modular route structure

---

## 🛠 Project Structure

\`\`\`
.
├── app.py                 # Main application entry point
├── wsgi.py                # WSGI entry point for production servers
├── requirements.txt       # Python dependencies
├── config.py              # Configuration loader
├── sample_db_config.json  # Example DB config (for local dev)
├── routes/                # Blueprint routes for API endpoints
├── static/                # CSS, JS, images
└── templates/             # HTML templates
\`\`\`

---

## 📦 Installation

1. **Clone the repository:**


git clone https://github.com/adahuncle/Website-Dev.git
cd [Desired Directory]


2. **Create and activate a virtual environment:**


python3 -m venv venv
On Windows: .\venv\Scripts\activate


3. **Install dependencies:**


pip install -r requirements.txt


4. **Configure your database:**

Create a file named \`db_config.json\` based on \`sample_db_config.json\` and update your credentials.

---

## 💻 Running the App (Development)


python app.py


Then go to: [http://localhost:5000](http://localhost:5000)

---

## 🧪 Running in Production

Use the WSGI entry point with a production server like Gunicorn or Waitress:


gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app


Or on Windows:


waitress-serve --host=0.0.0.0 wsgi:app


---

## 📊 Tech Stack

- **Backend:** Flask, Flask-CORS
- **Database:** MySQL (via \`mysql-connector-python\`)
- **Frontend:** HTML/CSS, JavaScript, Select2, Plotly
- **Deployment Ready:** Works with Docker, Gunicorn, Synology, or local Python environments

---

## 📄 License

MIT License. See \`LICENSE\` file for details.

---

## 🤝 Acknowledgments

This project was develope by Michael Guerrero - Process Engineer at Pinnacle Elastomeric Technology as an internal tool to support quality and process optimization workflows. Special thanks to the teams who provided production insight and dataset access.
