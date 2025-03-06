from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch
import pandas as pd
from typing import List, Dict, Union
from tqdm import tqdm

class SentimentAnalyzer:
    def __init__(self):
        # Load FinBERT model and tokenizer
        self.model_name = "ProsusAI/finbert"
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
        self.labels = ['negative', 'neutral', 'positive']
        
        # Move model to GPU if available
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model.to(self.device)
    
    def analyze_text(self, text: str) -> Dict[str, float]:
        """Analyze sentiment of a single text string."""
        inputs = self.tokenizer(text, return_tensors='pt', truncation=True, max_length=512)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            scores = torch.softmax(outputs.logits, dim=1)
        
        return {
            label: score.item()
            for label, score in zip(self.labels, scores[0])
        }
    
    def analyze_dataframe(self, df: pd.DataFrame, text_column: str = 'text') -> pd.DataFrame:
        """Analyze sentiment for all texts in a DataFrame."""
        results = []
        
        for text in tqdm(df[text_column], desc='Analyzing sentiment'):
            sentiment_scores = self.analyze_text(text)
            results.append(sentiment_scores)
        
        # Convert results to DataFrame columns
        sentiment_df = pd.DataFrame(results)
        return pd.concat([df, sentiment_df], axis=1)
    
    def get_combined_sentiment(self, scores: Dict[str, float]) -> str:
        """Get the dominant sentiment category."""
        return max(scores.items(), key=lambda x: x[1])[0]
    
    def calculate_weighted_sentiment(self, df: pd.DataFrame) -> float:
        """
        Calculate a weighted sentiment score across all sources.
        
        Weights:
        - Financial News: 0.7 (more reliable, professional sources)
        - WallStreetBets: 0.3 (more volatile, but captures market sentiment)
        
        Returns a score between -1 (very negative) and 1 (very positive)
        """
        if df.empty:
            return 0.0
        
        # Group by source and calculate average sentiment
        source_sentiments = {}
        
        for source in df['source'].unique():
            source_df = df[df['source'] == source]
            # Calculate net sentiment (positive - negative)
            source_sentiments[source] = source_df['positive'].mean() - source_df['negative'].mean()
        
        # Apply weights based on source
        weights = {
            'Financial News': 0.7,  # Higher weight for professional sources
            'WallStreetBets': 0.3,  # Lower weight for social media
        }
        
        # Calculate weighted average
        total_weight = 0
        weighted_sum = 0
        
        for source, sentiment in source_sentiments.items():
            weight = weights.get(source, 0.5)  # Default weight if source not recognized
            weighted_sum += sentiment * weight
            total_weight += weight
        
        # Return weighted average, or 0 if no weights
        return weighted_sum / total_weight if total_weight > 0 else 0.0

def main():
    # Test the analyzer
    analyzer = SentimentAnalyzer()
    test_text = "AAPL reported strong earnings, beating market expectations."
    sentiment = analyzer.analyze_text(test_text)
    print(f"Test text: {test_text}")
    print(f"Sentiment scores: {sentiment}")

if __name__ == '__main__':
    main()