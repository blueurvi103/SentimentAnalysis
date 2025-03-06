import requests
import pandas as pd
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from sentiment_analysis.sentiment_analysis import SentimentAnalyzer
import time

class InstitutionalSentimentFetcher:
    def __init__(self):
        # Load environment variables from the correct path
        load_dotenv(dotenv_path='/Users/Avi 1/Sentiment Analysis Project/.env')
        
        # Get API keys
        self.alpha_vantage_key = os.environ.get('ALPHA_VANTAGE_KEY')
        self.news_api_key = os.environ.get('NEWS_API_KEY')
        
        # Set up request headers
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Initialize sentiment analyzer
        self.sentiment_analyzer = None  # Lazy initialization to avoid circular imports
    
    def _get_sentiment_analyzer(self):
        """Lazy initialization of sentiment analyzer to avoid circular imports."""
        if self.sentiment_analyzer is None:
            self.sentiment_analyzer = SentimentAnalyzer()
        return self.sentiment_analyzer
    
    def fetch_alpha_vantage_news(self, ticker: str, days: int = 7) -> pd.DataFrame:
        """Fetch news from Alpha Vantage API."""
        print(f"\n=== Alpha Vantage API Request ===")
        print(f"Ticker: {ticker}")
        print(f"Days: {days}")
        print(f"API Key present: {bool(self.alpha_vantage_key)}")
        
        if not self.alpha_vantage_key or self.alpha_vantage_key == "":
            print("ERROR: Alpha Vantage API key is missing or invalid")
            return pd.DataFrame()
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Construct API URL
        url = f"https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers={ticker}&apikey={self.alpha_vantage_key}"
        
        try:
            # Make API request
            response = requests.get(url, headers=self.headers)
            print(f"Status Code: {response.status_code}")
            print(f"Response Keys: {data.keys() if response.status_code == 200 else 'No data'}")
            
            # Check response status
            if response.status_code != 200:
                print(f"Alpha Vantage API Error: Status code {response.status_code}")
                print(f"Response: {response.text}")
                return pd.DataFrame()
            
            # Parse response
            data = response.json()
            
            # Check if feed exists in response
            if "feed" not in data:
                print(f"No news feed found in Alpha Vantage response: {data.keys()}")
                return pd.DataFrame()
            
            # Process articles
            articles = []
            for item in data["feed"]:
                try:
                    # Parse timestamp
                    timestamp = datetime.strptime(item["time_published"], "%Y%m%dT%H%M%S")
                    
                    # Check if article is within date range
                    if start_date <= timestamp <= end_date:
                        # Create article entry
                        articles.append({
                            'text': f"{item.get('title', '')} {item.get('summary', '')}",
                            'timestamp': timestamp,
                            'source': 'Financial News',
                            'publisher': item.get('source', 'Unknown'),
                            'url': item.get('url', '')
                        })
                except Exception as e:
                    print(f"Error processing article: {e}")
                    continue
            
            print(f"Found {len(articles)} articles from Alpha Vantage")
            return pd.DataFrame(articles)
            
        except Exception as e:
            print(f"Error fetching Alpha Vantage news: {e}")
            return pd.DataFrame()
    
    def fetch_news_api(self, ticker: str, days: int = 7) -> pd.DataFrame:
        print(f"\n=== News API Request ===")
        print(f"Ticker: {ticker}")
        print(f"Days: {days}")
        print(f"API Key present: {bool(self.news_api_key)}")
        
        if not self.news_api_key or self.news_api_key == "your_news_api_key":
            print("ERROR: News API key is missing or using default value")
            return pd.DataFrame()
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Prepare API parameters
        params = {
            'q': f'{ticker} OR {self.get_company_name(ticker)}',
            'from': start_date.strftime('%Y-%m-%d'),
            'to': end_date.strftime('%Y-%m-%d'),
            'language': 'en',
            'sortBy': 'publishedAt',
            'apiKey': self.news_api_key,
            'pageSize': 100
        }
        
        try:
            # Make API request
            response = requests.get('https://newsapi.org/v2/everything', params=params, headers=self.headers)
            
            # Check response status
            if response.status_code != 200:
                print(f"News API Error: Status code {response.status_code}")
                print(f"Response: {response.text}")
                return pd.DataFrame()
            
            # Parse response
            data = response.json()
            articles = data.get('articles', [])
            
            print(f"Found {len(articles)} articles from News API")
            
            if not articles:
                return pd.DataFrame()
            
            # Process articles
            news_data = [{
                'text': f"{a.get('title', '')} {a.get('description', '')}",
                'timestamp': pd.to_datetime(a.get('publishedAt')),
                'source': 'Financial News',
                'publisher': a.get('source', {}).get('name', 'Unknown'),
                'url': a.get('url', '')
            } for a in articles]
            
            return pd.DataFrame(news_data)
            
        except Exception as e:
            print(f"Error fetching News API data: {e}")
            return pd.DataFrame()
    
    @staticmethod
    def get_company_name(ticker: str) -> str:
        """Get company name from ticker."""
        companies = {
            "AAPL": "Apple",
            "NVDA": "NVIDIA",
            "MSFT": "Microsoft",
            "TSLA": "Tesla",
            "AMZN": "Amazon",
            "GOOGL": "Google",
            "META": "Meta",
            "NFLX": "Netflix"
        }
        return companies.get(ticker, ticker)
    
    def get_institutional_sentiment(self, ticker: str, days: int = 7) -> pd.DataFrame:
        """Fetch and combine institutional sentiment data from multiple sources."""
        print(f"Fetching institutional sentiment for {ticker} over {days} days")
        
        # Try Alpha Vantage first
        alpha_vantage_df = self.fetch_alpha_vantage_news(ticker, days)
        
        # If Alpha Vantage fails or returns no data, try News API as backup
        news_api_df = pd.DataFrame()
        if alpha_vantage_df.empty:
            print("No data from Alpha Vantage, trying News API as backup")
            news_api_df = self.fetch_news_api(ticker, days)
        
        # Combine results
        dfs = []
        if not alpha_vantage_df.empty:
            dfs.append(alpha_vantage_df)
        if not news_api_df.empty:
            dfs.append(news_api_df)
        
        # If no data from any source, return empty DataFrame
        if not dfs:
            print("No institutional sentiment data available from any source")
            return pd.DataFrame()
        
        # Combine all data
        combined_df = pd.concat(dfs, ignore_index=True)
        
        # Add ticker column
        combined_df['ticker'] = ticker
        
        # Apply sentiment analysis if data exists
        if not combined_df.empty and 'sentiment_score' not in combined_df.columns:
            print("Analyzing sentiment for institutional data")
            analyzer = self._get_sentiment_analyzer()
            combined_df = analyzer.analyze_dataframe(combined_df)
        
        print(f"Final institutional sentiment data: {len(combined_df)} rows")
        return combined_df

# For testing
def main():
    fetcher = InstitutionalSentimentFetcher()
    ticker = 'AAPL'
    df = fetcher.get_institutional_sentiment(ticker, days=7)
    print(f"Fetched {len(df)} articles for {ticker}")
    if not df.empty:
        print(df[['timestamp', 'publisher', 'positive', 'negative', 'neutral']].head())

if __name__ == '__main__':
    main()