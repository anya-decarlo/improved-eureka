import requests
from bs4 import BeautifulSoup
import pandas as pd
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.sentiment import SentimentIntensityAnalyzer
from collections import Counter
import time
import os

# Download required NLTK data
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('vader_lexicon')

def scrape_interactions(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract all interactions
        interactions = []
        
        # Find all text content that could be part of interactions
        content_elements = soup.find_all(['p', 'div', 'section'], class_=['response', 'interaction', 'message'])
        
        for element in content_elements:
            text = element.get_text(strip=True)
            if text:
                interactions.append({
                    'content': text,
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),  # Current time as we don't have historical timestamps
                    'element_type': element.name,
                    'classes': ' '.join(element.get('class', []))
                })
        
        return interactions
    except Exception as e:
        print(f"Error scraping website: {e}")
        return []

def analyze_interactions(interactions):
    # Initialize NLTK tools
    stop_words = set(stopwords.words('english'))
    sia = SentimentIntensityAnalyzer()
    
    analyzed_data = []
    
    for interaction in interactions:
        content = interaction['content']
        
        # Basic text statistics
        words = word_tokenize(content)
        sentences = sent_tokenize(content)
        
        # Remove stopwords and calculate word frequency
        filtered_words = [word.lower() for word in words if word.isalnum() and word.lower() not in stop_words]
        word_freq = Counter(filtered_words).most_common(5)
        
        # Sentiment analysis
        sentiment_scores = sia.polarity_scores(content)
        
        # Additional analysis specific to Freysa's responses
        contains_blockchain = any(word in content.lower() for word in ['blockchain', 'crypto', 'token', 'smart contract'])
        contains_directive = any(word in content.lower() for word in ['directive', 'protocol', 'rule', 'restriction'])
        
        analyzed_data.append({
            'content': content,
            'timestamp': interaction['timestamp'],
            'element_type': interaction['element_type'],
            'classes': interaction['classes'],
            'word_count': len(words),
            'sentence_count': len(sentences),
            'top_words': ', '.join([f"{word}({count})" for word, count in word_freq]),
            'sentiment_compound': sentiment_scores['compound'],
            'sentiment_pos': sentiment_scores['pos'],
            'sentiment_neg': sentiment_scores['neg'],
            'sentiment_neu': sentiment_scores['neu'],
            'mentions_blockchain': contains_blockchain,
            'mentions_directive': contains_directive
        })
    
    return analyzed_data

def save_analysis(analyzed_data, output_dir='freysa_analysis'):
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Create DataFrame and save to CSV
    df = pd.DataFrame(analyzed_data)
    timestamp = time.strftime('%Y%m%d_%H%M%S')
    csv_filename = os.path.join(output_dir, f'freysa_interactions_{timestamp}.csv')
    df.to_csv(csv_filename, index=False)
    
    # Calculate and print summary statistics
    print("\nAnalysis Summary:")
    print(f"Total interactions analyzed: {len(analyzed_data)}")
    print(f"Average sentiment score: {df['sentiment_compound'].mean():.2f}")
    print(f"Total word count: {df['word_count'].sum()}")
    print(f"Blockchain mentions: {df['mentions_blockchain'].sum()}")
    print(f"Directive mentions: {df['mentions_directive'].sum()}")
    
    # Calculate sentiment trends
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    print("\nSentiment Trends:")
    print(df.groupby(df['timestamp'].dt.date)['sentiment_compound'].mean())
    
    return csv_filename

def main():
    url = 'https://www.freysa.ai/act-i'
    
    print("Scraping Freysa's interactions...")
    interactions = scrape_interactions(url)
    
    if interactions:
        print(f"Found {len(interactions)} interactions")
        analyzed_data = analyze_interactions(interactions)
        csv_file = save_analysis(analyzed_data)
        print(f"\nDetailed analysis saved to {csv_file}")
    else:
        print("No interactions found or error occurred during scraping")

if __name__ == "__main__":
    main()
