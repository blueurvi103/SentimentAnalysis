import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests
import os
from dotenv import load_dotenv

from data_fetching.fetch_institutional_sentiment import InstitutionalSentimentFetcher
from data_fetching.fetch_wsb_sentiment import WSBSentimentFetcher
from sentiment_analysis.sentiment_analysis import SentimentAnalyzer
from typing import List

class SentimentDashboard:
    def __init__(self):
        st.set_page_config(page_title="Tech Stock Sentiment Analysis", layout="wide")
        self.setup_sidebar()
    
    def setup_sidebar(self):
        """Setup the sidebar with stock selection and filters."""
        st.sidebar.title("⚙️ Dashboard Settings")
        self.selected_ticker = st.sidebar.selectbox(
            "Select Stock",
            ["AAPL", "NVDA", "MSFT", "TSLA"],
            format_func=lambda x: f"{x} - {self.get_company_name(x)}"
        )
        self.days_lookback = st.sidebar.slider(
            "Days Lookback",
            min_value=1,
            max_value=30,
            value=7
        )
    
    @staticmethod
    def get_company_name(ticker):
        """Get company name from ticker."""
        companies = {
            "AAPL": "Apple Inc.",
            "NVDA": "NVIDIA Corporation",
            "MSFT": "Microsoft Corporation",
            "TSLA": "Tesla, Inc."
        }
        return companies.get(ticker, ticker)
    
    def plot_sentiment_over_time(self, df: pd.DataFrame, source: str):
        """Create a line chart showing sentiment trends over time."""
        source_df = df[df['source'] == source].copy()
        if not source_df.empty:
            fig = go.Figure()
            
            for sentiment in ['positive', 'neutral', 'negative']:
                fig.add_trace(go.Scatter(
                    x=source_df['timestamp'],
                    y=source_df[sentiment],
                    name=sentiment.capitalize(),
                    mode='lines+markers'
                ))
            
            fig.update_layout(
                title=f"{source} Sentiment Over Time",
                xaxis_title="Date",
                yaxis_title="Sentiment Score",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
    
    def plot_sentiment_distribution(self, df: pd.DataFrame):
        """Create a pie chart showing overall sentiment distribution."""
        if not df.empty:
            avg_sentiments = {
                'Positive': df['positive'].mean(),
                'Neutral': df['neutral'].mean(),
                'Negative': df['negative'].mean()
            }
            
            fig = go.Figure(data=[go.Pie(
                labels=list(avg_sentiments.keys()),
                values=list(avg_sentiments.values()),
                hole=.3
            )])
            
            fig.update_layout(
                title="Overall Sentiment Distribution",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
    
    def display_sentiment_gauge(self, sentiment_score: float, title: str = "Sentiment Score"):
        """Create a gauge chart for sentiment score."""
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=sentiment_score,
            domain={'x': [0, 1], 'y': [0, 1]},
            gauge={
                'axis': {'range': [-1, 1]},
                'bar': {'color': "#1f77b4"},
                'steps': [
                    {'range': [-1, -0.3], 'color': "#ff7f7f"},
                    {'range': [-0.3, 0.3], 'color': "#ffff7f"},
                    {'range': [0.3, 1], 'color': "#7fff7f"}
                ]
            },
            title={'text': title}
        ))
        
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)

    def filter_financial_terms(self, words: List[str]) -> List[str]:
        """Filter for relevant financial terms and adjectives."""
        financial_terms = {
            # Trading terms
            'buy', 'sell', 'hold', 'call', 'put', 'long', 'short',
            # Adjectives
            'bullish', 'bearish', 'strong', 'weak', 'positive', 'negative',
            'volatile', 'stable', 'risky', 'safe', 'overvalued', 'undervalued',
            # Performance terms
            'up', 'down', 'rising', 'falling', 'surging', 'plunging',
            'outperform', 'underperform'
        }
        return [word for word in words if word.lower() in financial_terms]

    def render_dashboard(self, df: pd.DataFrame, combined_score: float):
        st.title(f"📊 {self.get_company_name(self.selected_ticker)} ({self.selected_ticker}) Sentiment Analysis")
        
        # Source Statistics Section
        st.subheader("📊 Source Statistics")
        
        # Create two columns for source metrics
        col1, col2 = st.columns(2)
        
        # Financial News metrics
        with col1:
            financial_df = df[df['source'] == 'Financial News']
            st.metric("Financial News Sources", len(financial_df), "News Articles")
            if not financial_df.empty and 'text' in financial_df.columns:
                words = ' '.join(financial_df['text'].str.lower()).split()
                filtered_words = self.filter_financial_terms(words)
                most_common = pd.Series(filtered_words).value_counts().nlargest(3)
                st.caption(f"Top trading terms: {', '.join(most_common.index)}")
        
        # WallStreetBets metrics
        with col2:
            wsb_df = df[df['source'] == 'WallStreetBets']
            st.metric("WallStreetBets Sources", len(wsb_df), "Reddit Posts")
            if not wsb_df.empty and 'text' in wsb_df.columns:
                words = ' '.join(wsb_df['text'].str.lower()).split()
                filtered_words = self.filter_financial_terms(words)
                most_common = pd.Series(filtered_words).value_counts().nlargest(3)
                st.caption(f"Top trading terms: {', '.join(most_common.index)}")
        
        # Overall metrics
        st.metric("Total Sources", len(df))
        st.metric("Days Analyzed", self.days_lookback)
        
        # Get unique sources
        sources = df['source'].unique()
        
        # Display sentiment gauges
        st.subheader("🎯 Sentiment Scores")
        
        # Combined sentiment gauge
        st.markdown("### Combined Sentiment")
        self.display_sentiment_gauge(combined_score, "Combined Sentiment Score")
        st.caption("Combined score weights: Financial News (70%), WallStreetBets (30%)")
        
        # Individual source gauges
        st.markdown("### Source-Specific Sentiment")
        sources = sorted(df['source'].unique())  # Sort sources for consistent order
        
        # Optimized sentiment calculation
        source_scores = df.groupby('source').apply(
            lambda x: x['positive'].mean() - x['negative'].mean()
        ).to_dict()
        
        # Create columns for each source
        if sources:
            cols = st.columns(len(sources))
            for idx, source in enumerate(sources):
                with cols[idx]:
                    st.markdown(f"### {source}")
                    self.display_sentiment_gauge(
                        source_scores.get(source, 0), 
                        f"{source} Sentiment"
                    )

        # Sentiment distribution
        st.subheader("📊 Sentiment Distribution")
        col1, col2 = st.columns(2)
        with col1:
            self.plot_sentiment_distribution(df)
        
        # Source-specific sentiment trends
        st.subheader("📈 Sentiment Trends by Source")
        for source in sources:
            self.plot_sentiment_over_time(df, source)
        
        # Remove the correlation analysis section completely

def main():
    dashboard = SentimentDashboard()
    sentiment_analyzer = SentimentAnalyzer()
    
    try:
        # Initialize fetchers
        news_fetcher = InstitutionalSentimentFetcher()
        wsb_fetcher = WSBSentimentFetcher()
        
        # Fetch raw data
        news_df = news_fetcher.get_institutional_sentiment(dashboard.selected_ticker, dashboard.days_lookback)
        wsb_raw_df = wsb_fetcher.fetch_wsb_posts(dashboard.selected_ticker, dashboard.days_lookback)
        
        # Process WallStreetBets data
        wsb_df = pd.DataFrame()
        if not wsb_raw_df.empty:
            wsb_df = sentiment_analyzer.analyze_dataframe(wsb_raw_df)
            wsb_df['source'] = 'WallStreetBets'

        # Process News data
        if not news_df.empty:
            news_df = sentiment_analyzer.analyze_dataframe(news_df)  # Ensure sentiment analysis is applied
            news_df['source'] = 'Financial News'
            
        # Combine data
        combined_df = pd.concat([news_df, wsb_df], ignore_index=True)
        
        if combined_df.empty:
            st.error("No data available from any source for the selected period.")
            return
            
        # Calculate weighted sentiment
        combined_score = sentiment_analyzer.calculate_weighted_sentiment(combined_df)
        
        # Render dashboard
        dashboard.render_dashboard(combined_df, combined_score)

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

if __name__ == '__main__':
    main()