import praw
import pandas as pd
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import time

class WSBSentimentFetcher:
    def __init__(self):
        # Load environment variables
        load_dotenv(dotenv_path='/Users/Avi 1/Sentiment Analysis Project/.env')
        
        # Get Reddit API credentials
        client_id = os.environ.get('REDDIT_CLIENT_ID')
        client_secret = os.environ.get('REDDIT_CLIENT_SECRET')
        user_agent = os.environ.get('REDDIT_USER_AGENT')
        
        # Validate credentials
        if not all([client_id, client_secret, user_agent]):
            print("WARNING: Missing Reddit API credentials")
        
        # Initialize Reddit API client with error handling
        try:
            self.reddit = praw.Reddit(
                client_id=client_id,
                client_secret=client_secret,
                user_agent=user_agent
            )
            print("Reddit API client initialized successfully")
        except Exception as e:
            print(f"Error initializing Reddit API client: {str(e)}")
            self.reddit = None
    
    def fetch_wsb_posts(self, ticker: str, days: int = 7) -> pd.DataFrame:
        """Fetch posts from WallStreetBets subreddit related to a specific ticker."""
        print(f"Fetching WSB posts for {ticker} over the last {days} days")
        
        # Check if Reddit client is initialized
        if self.reddit is None:
            print("ERROR: Reddit API client not initialized")
            return pd.DataFrame()
        
        try:
            # Calculate the date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Access the WallStreetBets subreddit
            try:
                subreddit = self.reddit.subreddit('wallstreetbets')
                print("Successfully connected to r/wallstreetbets")
            except Exception as e:
                print(f"Error accessing r/wallstreetbets: {str(e)}")
                return pd.DataFrame()
            
            # Search for posts containing the ticker
            posts = []
            search_query = f"{ticker}"
            
            # Use multiple time filters to ensure we get enough posts
            time_filters = ['day', 'week', 'month']
            
            for time_filter in time_filters:
                try:
                    print(f"Searching with time filter: {time_filter}")
                    search_results = subreddit.search(search_query, time_filter=time_filter, limit=100)
                    
                    for post in search_results:
                        try:
                            post_date = datetime.fromtimestamp(post.created_utc)
                            
                            # Check if post is within the date range
                            if start_date <= post_date <= end_date:
                                # Check if the ticker is actually mentioned in the title or body
                                title = post.title.upper()
                                selftext = post.selftext.upper() if post.selftext else ""
                                
                                if ticker.upper() in title or ticker.upper() in selftext:
                                    posts.append({
                                        'text': f"{post.title} {post.selftext}",
                                        'timestamp': post_date,
                                        'score': post.score,
                                        'num_comments': post.num_comments,
                                        'url': f"https://www.reddit.com{post.permalink}",
                                        'source': 'WallStreetBets',
                                        'ticker': ticker
                                    })
                        except Exception as e:
                            print(f"Error processing post: {str(e)}")
                            continue
                    
                    # If we found enough posts, break out of the loop
                    if len(posts) >= 50:
                        break
                        
                except Exception as e:
                    print(f"Error searching with time filter {time_filter}: {str(e)}")
                    continue
            
            print(f"Found {len(posts)} WSB posts for {ticker}")
            
            # If no posts found, try to fetch from hot/new/top
            if not posts:
                print("No posts found via search, trying hot/new/top posts")
                self._fetch_from_listings(subreddit, ticker, start_date, end_date, posts)
            
            # Return results as DataFrame
            return pd.DataFrame(posts)
            
        except Exception as e:
            print(f"Error fetching WSB posts: {str(e)}")
            return pd.DataFrame()
    
    def _fetch_from_listings(self, subreddit, ticker: str, start_date, end_date, posts: list):
        """Fetch posts from hot/new/top listings as a fallback method."""
        listings = [
            ('hot', subreddit.hot(limit=100)),
            ('new', subreddit.new(limit=100)),
            ('top', subreddit.top('week', limit=100))
        ]
        
        for listing_name, listing in listings:
            try:
                print(f"Checking {listing_name} posts")
                for post in listing:
                    try:
                        post_date = datetime.fromtimestamp(post.created_utc)
                        
                        # Check if post is within the date range
                        if start_date <= post_date <= end_date:
                            # Check if the ticker is mentioned in the title or body
                            title = post.title.upper()
                            selftext = post.selftext.upper() if post.selftext else ""
                            
                            if ticker.upper() in title or ticker.upper() in selftext:
                                posts.append({
                                    'text': f"{post.title} {post.selftext}",
                                    'timestamp': post_date,
                                    'score': post.score,
                                    'num_comments': post.num_comments,
                                    'url': f"https://www.reddit.com{post.permalink}",
                                    'source': 'WallStreetBets',
                                    'ticker': ticker
                                })
                    except Exception as e:
                        print(f"Error processing {listing_name} post: {str(e)}")
                        continue
            except Exception as e:
                print(f"Error fetching {listing_name} posts: {str(e)}")
                continue

# For testing
def main():
    fetcher = WSBSentimentFetcher()
    ticker = 'AAPL'
    df = fetcher.fetch_wsb_posts(ticker, days=7)
    print(f"Fetched {len(df)} WSB posts for {ticker}")
    if not df.empty:
        print(df[['timestamp', 'score', 'num_comments']].head())

if __name__ == '__main__':
    main()