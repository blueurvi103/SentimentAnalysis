# Tech Stock Sentiment Analysis Dashboard

A real-time sentiment analysis dashboard that combines data from financial news and WallStreetBets to provide insights into market sentiment for major tech stocks.

## Features
- Multi-source sentiment analysis (Financial News + Reddit)
- Real-time data fetching
- Interactive visualizations
- Weighted sentiment scoring
- Trading term analysis
- Historical trend analysis

## Setup
1. Clone the repository
```bash
git clone https://github.com/blueurvi103/SentimentAnalysis.git
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Run the dashboard
```bash
streamlit run main.py
```

## Environment Variables
Create a .env file with:
- REDDIT_CLIENT_ID
- REDDIT_CLIENT_SECRET
- REDDIT_USER_AGENT
- NEWS_API_KEY
