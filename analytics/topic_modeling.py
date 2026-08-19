import pandas as pd
import numpy as np
from typing import Dict, List, Any
from bertopic import BERTopic
from sklearn.feature_extraction.text import CountVectorizer
import os

class TopicModeler:
    def __init__(self):
        self.model = None
        self.topic_data = None
    
    def load_data(self, file_path: str):
        """Load topic modeling data"""
        self.topic_data = pd.read_csv(file_path)
        return self.topic_data
    
    def train_bertopic(self, embeddings_path: str = None):
        """Train BERTopic model"""
        if self.topic_data is None:
            raise ValueError("No data loaded")
        
        # Prepare documents
        documents = self.topic_data['text'].tolist()
        
        # Train BERTopic
        if embeddings_path and os.path.exists(embeddings_path):
            embeddings = np.load(embeddings_path)
            self.model = BERTopic()
            self.topics, self.probs = self.model.fit_transform(documents, embeddings=embeddings)
        else:
            self.model = BERTopic()
            self.topics, self.probs = self.model.fit_transform(documents)
        
        return self.model
    
    def train_lda(self, n_topics: int = 10):
        """Train LDA topic model"""
        from sklearn.decomposition import LatentDirichletAllocation
        from sklearn.feature_extraction.text import TfidfVectorizer
        
        if self.topic_data is None:
            raise ValueError("No data loaded")
        
        # Prepare documents
        documents = self.topic_data['text'].tolist()
        
        # Create TF-IDF matrix
        vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        
        X = vectorizer.fit_transform(documents)
        
        # Train LDA
        lda = LatentDirichletAllocation(
            n_components=n_topics,
            random_state=42,
            n_jobs=-1
        )
        
        lda.fit(X)
        
        self.model = lda
        self.vectorizer = vectorizer
        
        return lda
    
    def get_topics(self, n_top_words: int = 10) -> Dict[int, List[str]]:
        """Get topics with top words"""
        if self.model is None:
            return {}
        
        if hasattr(self.model, 'get_topics'):
            # BERTopic
            topics = self.model.get_topics()
            result = {}
            for topic_id, words in topics.items():
                result[topic_id] = [word for word, score in words[:n_top_words]]
            return result
        else:
            # LDA
            feature_names = self.vectorizer.get_feature_names_out()
            result = {}
            for topic_idx, topic in enumerate(self.model.components_):
                top_words = [feature_names[i] for i in topic.argsort()[:-n_top_words - 1:-1]]
                result[topic_idx] = top_words
            return result
    
    def get_topic_distribution(self) -> np.ndarray:
        """Get topic distribution for documents"""
        if self.model is None:
            return np.array([])
        
        if hasattr(self.model, 'get_topics'):
            # BERTopic
            return self.probs
        else:
            # LDA
            X = self.vectorizer.transform(self.topic_data['text'].tolist())
            return self.model.transform(X)
    
    def analyze_topic_evolution(self) -> Dict[str, List[int]]:
        """Analyze how topics evolve over time"""
        if self.topic_data is None or 'created' not in self.topic_data.columns:
            return {}
        
        # Convert dates
        self.topic_data['created'] = pd.to_datetime(self.topic_data['created'])
        self.topic_data['year'] = self.topic_data['created'].dt.year
        
        # Get topic distribution
        topic_dist = self.get_topic_distribution()
        
        evolution = {}
        for year in self.topic_data['year'].unique():
            year_mask = self.topic_data['year'] == year
            if year_mask.sum() > 0:
                year_dist = topic_dist[year_mask].mean(axis=0)
                evolution[str(year)] = year_dist.tolist()
        
        return evolution
    
    def identify_emerging_topics(self, threshold: float = 0.1) -> List[int]:
        """Identify emerging topics based on recent growth"""
        if self.topic_data is None or 'created' not in self.topic_data.columns:
            return []
        
        # Convert dates
        self.topic_data['created'] = pd.to_datetime(self.topic_data['created'])
        self.topic_data['year'] = self.topic_data['created'].dt.year
        
        # Get topic distribution
        topic_dist = self.get_topic_distribution()
        
        # Calculate growth rate
        years = sorted(self.topic_data['year'].unique())
        if len(years) < 2:
            return []
        
        emerging_topics = []
        for topic_id in range(topic_dist.shape[1]):
            # Get topic distribution over time
            topic_over_time = []
            for year in years:
                year_mask = self.topic_data['year'] == year
                if year_mask.sum() > 0:
                    topic_over_time.append(topic_dist[year_mask, topic_id].mean())
                else:
                    topic_over_time.append(0)
            
            # Calculate growth rate
            if len(topic_over_time) >= 2:
                growth_rate = (topic_over_time[-1] - topic_over_time[0]) / max(topic_over_time[0], 0.01)
                if growth_rate > threshold:
                    emerging_topics.append(topic_id)
        
        return emerging_topics

if __name__ == "__main__":
    modeler = TopicModeler()
    modeler.load_data("datasets/processed/topic_training.json")
    
    # Train BERTopic
    model = modeler.train_bertopic()
    topics = modeler.get_topics()
    
    print("Topics found:", len(topics))
    for topic_id, words in topics.items():
        print(f"Topic {topic_id}: {', '.join(words[:5])}")