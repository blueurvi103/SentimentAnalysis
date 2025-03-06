from dotenv import load_dotenv
import os

def test_env():
    load_dotenv()
    
    # Test API keys
    alpha_key = os.environ.get('ALPHA_VANTAGE_KEY')
    news_key = os.environ.get('NEWS_API_KEY')
    
    print("Environment Variables Check:")
    print(f"Alpha Vantage Key present: {bool(alpha_key)}")
    print(f"News API Key present: {bool(news_key)}")
    
    # Test file structure
    required_folders = [
        'data_fetching',
        'sentiment_analysis',
        'visualizations'
    ]
    
    print("\nFolder Structure Check:")
    for folder in required_folders:
        exists = os.path.exists(folder)
        print(f"{folder}: {'✓' if exists else '✗'}")

if __name__ == "__main__":
    test_env()