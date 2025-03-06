# Project Structure Documentation

## Overview
This project is a comprehensive sentiment analysis dashboard for tech stocks, integrating data from multiple sources and providing real-time visualization of sentiment trends.

## File Structure Explanation

### Main Application Files

#### `main.py`
The entry point of the application that orchestrates the entire workflow:
- Initializes the dashboard and sentiment analyzer
- Coordinates data fetching from multiple sources
- Processes and combines sentiment data
- Renders the final dashboard

### Data Fetching (`data_fetching/`)

#### `fetch_institutional_sentiment.py`
Responsible for gathering sentiment data from institutional sources:
- Collects analyst ratings and reports
- Processes institutional investor sentiment
- Formats data for sentiment analysis

#### `fetch_twitter_sentiment.py`
Handles Twitter data collection:
- Fetches tweets related to specific tech stocks
- Filters relevant content
- Prepares data for sentiment analysis

#### `fetch_wsb_sentiment.py`
Manages Reddit WallStreetBets data:
- Collects posts and comments about tech stocks
- Filters for relevant discussions
- Prepares social media sentiment data

### Sentiment Analysis (`sentiment_analysis/`)

#### `sentiment_analysis.py`
Core sentiment analysis implementation:
- Processes text data from all sources
- Applies sentiment analysis algorithms
- Calculates sentiment scores
- Provides weighted sentiment analysis

### Visualizations (`visualizations/`)

#### `sentiment_dashboard.py`
Streamlit-based dashboard implementation:
- Creates an interactive web interface
- Displays real-time sentiment metrics
- Generates various visualization components:
  - Sentiment trends over time
  - Distribution pie charts
  - Sentiment gauge indicators
  - Source-specific analysis

### Configuration and Documentation

#### `requirements.txt`
Lists all Python dependencies required to run the project:
- Streamlit for web interface
- Plotly for interactive visualizations
- Pandas for data manipulation
- Other required packages

#### `README.md`
Project documentation with:
- Installation instructions
- Usage guidelines
- Project overview
- Setup requirements

## Data Flow

1. User selects a stock ticker and time range in the dashboard
2. Data fetchers collect information from multiple sources
3. Sentiment analyzer processes the collected data
4. Dashboard visualizes the results in various formats

## Key Features

- Real-time sentiment analysis
- Multi-source data integration
- Interactive visualizations
- Customizable time ranges
- Support for major tech stocks
- Comprehensive sentiment metrics