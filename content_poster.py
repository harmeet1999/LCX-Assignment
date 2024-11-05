import json
import sqlite3
import os
import requests
import nltk
from textblob import TextBlob 
from datetime import datetime
from dotenv import load_dotenv  

load_dotenv()



def download_nltk_resources():
    nltk.download('punkt')
    nltk.download('punkt_tab')

# SQLite database
def init_db():
    db_file = 'engagement.db'
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS engagement 
    (id INTEGER PRIMARY KEY, title TEXT, summary TEXT, views INTEGER, shares INTEGER, timestamp TEXT)''')
    conn.commit()
    return conn, cursor

def retrieve_content():
    with open('content_feed.json') as f:
        return json.load(f)

def detect_new_content(content, cursor):
    existing_ids = {row[0] for row in cursor.execute("SELECT id FROM engagement").fetchall()}
    return [article for article in content if article["id"] not in existing_ids]

def summarize_content(text):
    blob = TextBlob(text)
    sentences = blob.sentences
    summary = " ".join([str(sent) for sent in sentences[:2]])
    return summary

def generate_image(keywords):
    image_api_url = "https://api.openai.com/v1/images/generations"
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    headers = {
        "Authorization":f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "prompt": keywords,
        "n": 1,
        "size": "1024x1024"
    }
    response = requests.post(image_api_url, json=data, headers=headers)
    
    if response.status_code == 200:
        return response.json().get("data", [{}])[0].get("url", "No image URL found")
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return "No image URL found"



def post_to_social_media(article, summary, image_url, cursor):
    print(f"Title: {article['title']}")
    print(f"Summary: {summary}")
    print(f"Image URL: {image_url}")
    print(f"Link: https://example.com/articles/{article['id']}")  

    # Engagement data
    views, shares = 100, 10 
    cursor.execute("INSERT INTO engagement (id, title, summary, views, shares, timestamp) VALUES (?, ?, ?, ?, ?, ?) ",
    (article["id"], article["title"], summary, views, shares, datetime.now().isoformat()))

def process_content():
    download_nltk_resources() 
    conn, cursor = init_db()   
    content = retrieve_content()   
    new_articles = detect_new_content(content, cursor)

    for article in new_articles:
        summary = summarize_content(article['content'])  
        keywords = " ".join(summary.split()[:5])  
        image_url = generate_image(keywords) 

        post_to_social_media(article, summary, image_url, cursor)

    conn.commit()  
    conn.close()   

if __name__ == "__main__":
    process_content()  
