from flask import Flask, jsonify, request
import sqlite3
import content_poster

app = Flask(__name__)
DATABASE = 'engagement.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/top_articles', methods=['GET'])
def top_articles():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM engagement ORDER BY views + shares DESC LIMIT 3")
    articles = cursor.fetchall()
    conn.close()
    return jsonify([dict(article) for article in articles])

@app.route('/process_content', methods=['POST'])
def trigger_content_processing():
    content_poster.process_content()
    return jsonify({"status": "Content processing triggered."}), 200

@app.route('/generate_image', methods=['POST'])
def generate_image_route():
    """API endpoint to generate an image based on keywords."""
    data = request.get_json() 
    keywords = data.get("keywords")  
    
    if not keywords:
        return jsonify({"error": "Keywords are required"}), 400
    
    image_url = content_poster.generate_image(keywords)  
    return jsonify({"image_url": image_url})





if __name__ == "__main__":
    app.run(debug=True)
