import pandas as pd
import numpy as np
from collections import Counter
from typing import Dict, List, Any
import re

class TrendAnalyzer:
    def __init__(self):
        self.data = None
    
    def load_data(self, file_path: str):
        """Load arXiv dataset"""
        self.data = pd.read_csv(file_path)
        return self.data
    
    def analyze_topic_frequency(self) -> Dict[str, int]:
        """Analyze frequency of research topics"""
        if self.data is None:
            return {}
        
        common_topics = {
            'machine learning': 0,
            'deep learning': 0,
            'natural language processing': 0,
            'computer vision': 0,
            'reinforcement learning': 0,
            'data science': 0,
            'artificial intelligence': 0,
            'neural networks': 0,
            'optimization': 0,
            'classification': 0
        }
        
        for topic in common_topics.keys():
            count = self.data['abstract'].str.contains(
                topic, case=False, na=False
            ).sum()
            common_topics[topic] = int(count)
        
        return common_topics
    
    def analyze_research_growth(self, time_period: str = 'monthly') -> Dict[str, int]:
        """Analyze research growth over time"""
        if self.data is None:
            return {}
        
        if 'created' in self.data.columns:
            try:
                self.data['created'] = pd.to_datetime(self.data['created'])
                
                if time_period == 'monthly':
                    monthly_counts = self.data.groupby(
                        self.data['created'].dt.to_period('M')
                    ).size()
                    return {str(k): int(v) for k, v in monthly_counts.to_dict().items()}
                elif time_period == 'yearly':
                    yearly_counts = self.data.groupby(
                        self.data['created'].dt.year
                    ).size()
                    return {str(k): int(v) for k, v in yearly_counts.to_dict().items()}
            except:
                pass
        
        return {'total': len(self.data)}
    
    def identify_emerging_topics(self, top_n: int = 5) -> List[str]:
        """Identify emerging research topics"""
        if self.data is None:
            return []
        
        emerging_keywords = [
            'transformers', 'large language models', 'foundation models',
            'multimodal learning', 'self-supervised learning',
            'federated learning', 'explainable ai', 'ethical ai',
            'generative adversarial networks', 'graph neural networks'
        ]
        
        emerging_topics = []
        for topic in emerging_keywords:
            if self.data['abstract'].str.contains(
                topic, case=False, na=False
            ).sum() > 0:
                emerging_topics.append(topic)
        
        return emerging_topics[:top_n]
    
    def get_top_categories(self, top_n: int = 10) -> List[str]:
        """Get top research categories"""
        if self.data is None:
            return []
        
        if 'categories' in self.data.columns:
            all_categories = []
            for categories in self.data['categories']:
                if isinstance(categories, str):
                    all_categories.extend([
                        cat.strip() for cat in categories.split()
                    ])
            
            top_categories = Counter(all_categories).most_common(top_n)
            return [cat for cat, count in top_categories]
        
        return []
    
    def analyze_publication_trends(self) -> Dict[str, List[int]]:
        """Analyze publication trends"""
        if self.data is None:
            return {}
        
        trends = {}
        
        if 'created' in self.data.columns:
            try:
                self.data['created'] = pd.to_datetime(self.data['created'])
                self.data['year'] = self.data['created'].dt.year
                
                yearly_counts = self.data.groupby('year').size()
                trends['publications'] = yearly_counts.tolist()
                trends['years'] = yearly_counts.index.tolist()
                
            except:
                trends = {'publications': [len(self.data)], 'years': [2024]}
        else:
            trends = {'publications': [len(self.data)], 'years': [2024]}
        
        return trends
    
    def get_trending_keywords(self, top_n: int = 20) -> List[str]:
        """Get trending keywords from recent papers"""
        if self.data is None:
            return []
        
        # Sort by date if available
        if 'created' in self.data.columns:
            try:
                self.data['created'] = pd.to_datetime(self.data['created'])
                recent_data = self.data.nlargest(1000, 'created')
            except:
                recent_data = self.data
        else:
            recent_data = self.data
        
        # Extract keywords from abstracts
        all_text = ' '.join(recent_data['abstract'].fillna('').astype(str))
        
        # Simple keyword extraction
        words = re.findall(r'\b[a-zA-Z]{4,}\b', all_text.lower())
        word_counts = Counter(words)
        
        # Remove common stop words
        stop_words = {'this', 'that', 'with', 'from', 'have', 'were', 'they', 
                     'will', 'their', 'about', 'which', 'when', 'what', 'more'}
        
        trending = [
            word for word, count in word_counts.most_common(top_n * 2)
            if word not in stop_words
        ][:top_n]
        
        return trending

if __name__ == "__main__":
    analyzer = TrendAnalyzer()
    analyzer.load_data("datasets/processed/arxiv_processed.csv")
    
    print("Topic Frequency:", analyzer.analyze_topic_frequency())
    print("Emerging Topics:", analyzer.identify_emerging_topics())
    print("Top Categories:", analyzer.get_top_categories())
    print("Trending Keywords:", analyzer.get_trending_keywords())