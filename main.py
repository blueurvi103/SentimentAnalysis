import streamlit as st
from data_fetching.fetch_wsb_sentiment import WSBSentimentFetcher
from data_fetching.fetch_institutional_sentiment import InstitutionalSentimentFetcher
from sentiment_analysis.sentiment_analysis import SentimentAnalyzer
from datetime import datetime
import pandas as pd

# Import only the SentimentDashboard class, not the main function
from visualizations.sentiment_dashboard import SentimentDashboard

@st.cache_data(ttl=3600, max_entries=10)  # Cache for 1 hour, limit entries
def fetch_all_sentiment_data(ticker: str, days: int):
    """Fetch sentiment data from all sources."""
    # Create a cache key that includes the date range
    cache_key = f"{ticker}_{days}_{datetime.now().strftime('%Y-%m-%d')}"
    
    # Initialize fetchers
    wsb_fetcher = WSBSentimentFetcher()
    institutional_fetcher = InstitutionalSentimentFetcher()
    sentiment_analyzer = SentimentAnalyzer()
    
    # Fetch data from all sources
    wsb_df = wsb_fetcher.fetch_wsb_posts(ticker, days)
    institutional_df = institutional_fetcher.get_institutional_sentiment(ticker, days)
    
    # Debug prints
    print(f"WSB data: {len(wsb_df)} rows")
    print(f"Institutional data: {len(institutional_df)} rows")
    
    # Process and tag each dataframe before combining
    if not wsb_df.empty:
        # Ensure WSB data has sentiment scores
        if 'positive' not in wsb_df.columns:
            wsb_df = sentiment_analyzer.analyze_dataframe(wsb_df)
        wsb_df['source'] = 'WallStreetBets'
        # Create a fresh DataFrame to avoid index issues
        wsb_df = pd.DataFrame(wsb_df.to_dict('records'))
    
    if not institutional_df.empty:
        # Ensure institutional data has sentiment scores
        if 'positive' not in institutional_df.columns:
            institutional_df = sentiment_analyzer.analyze_dataframe(institutional_df)
        # Make sure source is set
        if 'source' not in institutional_df.columns:
            institutional_df['source'] = 'Financial News'
        # Create a fresh DataFrame to avoid index issues
        institutional_df = pd.DataFrame(institutional_df.to_dict('records'))
    
    # Combine all data with a more robust approach
    combined_df = pd.DataFrame()
    
    if not wsb_df.empty and not institutional_df.empty:
        # Ensure columns match before concatenation
        common_cols = list(set(wsb_df.columns) & set(institutional_df.columns))
        wsb_df = wsb_df[common_cols]
        institutional_df = institutional_df[common_cols]
        combined_df = pd.concat([wsb_df, institutional_df], ignore_index=True)
    elif not wsb_df.empty:
        combined_df = wsb_df
    elif not institutional_df.empty:
        combined_df = institutional_df
    
    print(f"Combined data: {len(combined_df)} rows")
    print(f"Sources present: {combined_df['source'].unique() if not combined_df.empty else 'None'}")
    
    return combined_df

def main():
    dashboard = SentimentDashboard()
    
    try:
        # Get data using the cached function
        ticker = dashboard.selected_ticker
        days = dashboard.days_lookback
        
        # Force cache invalidation when parameters change
        if 'last_ticker' not in st.session_state or 'last_days' not in st.session_state:
            st.session_state['last_ticker'] = ticker
            st.session_state['last_days'] = days
        elif st.session_state['last_ticker'] != ticker or st.session_state['last_days'] != days:
            # Parameters changed, clear cache
            st.cache_data.clear()
            st.session_state['last_ticker'] = ticker
            st.session_state['last_days'] = days
        
        combined_df = fetch_all_sentiment_data(ticker, days)
        
        if combined_df.empty:
            st.error("No data available from any source for the selected period.")
            return
        
        # Calculate combined sentiment score
        sentiment_analyzer = SentimentAnalyzer()
        combined_score = sentiment_analyzer.calculate_weighted_sentiment(combined_df)
        
        # Render dashboard
        dashboard.render_dashboard(combined_df, combined_score)
    
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        import traceback
        st.error(traceback.format_exc())

if __name__ == "__main__":
    main()