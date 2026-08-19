import json
import pandas as pd
from typing import Dict, List, Any
import os

class DatasetPreprocessor:
    def __init__(self):
        self.scitldr_path = "D:\\scitldr-master\\scitldr-master\\SciTLDR-Data"
        self.arxiv_path = "C:\\Users\\Diya Panjwani\\Downloads\\archive\\arxiv-metadata-oai-snapshot.json"
        self.output_dir = "datasets/processed"
        
        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)
    
    def preprocess_scitldr(self) -> pd.DataFrame:
        """Preprocess SciTLDR dataset for summarization"""
        print("Preprocessing SciTLDR dataset...")
        
        # Load SciTLDR data
        data_files = [
            "SciTLDR-Data\\SciTLDR-A\\train.jsonl",
            "SciTLDR-Data\\SciTLDR-A\\dev.jsonl", 
            "SciTLDR-Data\\SciTLDR-A\\test.jsonl"
        ]
        
        all_data = []
        for file_path in data_files:
            full_path = os.path.join(self.scitldr_path, file_path)
            
            if os.path.exists(full_path):
                with open(full_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        data = json.loads(line)
                        
                        # Extract paper information
                        paper_info = {
                            'paper_id': data.get('paper_id', ''),
                            'title': data.get('title', ''),
                            'abstract': data.get('abstract', ''),
                            'source': ' '.join(data.get('source', [])),
                            'target': ' '.join(data.get('target', [])),
                            'section_names': data.get('section_names', []),
                            'sections': data.get('sections', [])
                        }
                        all_data.append(paper_info)
        
        # Create DataFrame
        df = pd.DataFrame(all_data)
        
        # Save processed data
        output_path = os.path.join(self.output_dir, 'scitldr_processed.csv')
        df.to_csv(output_path, index=False)
        
        print(f"SciTLDR dataset processed: {len(df)} papers")
        return df
    
    def preprocess_arxiv(self, sample_size: int = 10000) -> pd.DataFrame:
        """Preprocess arXiv dataset for recommendations and trends"""
        print("Preprocessing arXiv dataset...")
        
        if not os.path.exists(self.arxiv_path):
            print("arXiv dataset not found")
            return pd.DataFrame()
        
        # Load arXiv metadata (sample for efficiency)
        papers = []
        with open(self.arxiv_path, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                if i >= sample_size:
                    break
                
                try:
                    data = json.loads(line)
                    
                    paper_info = {
                        'paper_id': data.get('id', ''),
                        'title': data.get('title', ''),
                        'abstract': data.get('abstract', ''),
                        'categories': data.get('categories', '').split(),
                        'authors': data.get('authors', ''),
                        'created': data.get('created', ''),
                        'updated': data.get('updated', '')
                    }
                    papers.append(paper_info)
                except json.JSONDecodeError:
                    continue
        
        # Create DataFrame
        df = pd.DataFrame(papers)
        
        # Clean and preprocess
        df['abstract'] = df['abstract'].fillna('')
        df['title'] = df['title'].fillna('')
        
        # Save processed data
        output_path = os.path.join(self.output_dir, 'arxiv_processed.csv')
        df.to_csv(output_path, index=False)
        
        print(f"arXiv dataset processed: {len(df)} papers")
        return df
    
    def create_training_data(self) -> Dict[str, Any]:
        """Create training data for various ML tasks"""
        
        # Preprocess both datasets
        scitldr_df = self.preprocess_scitldr()
        arxiv_df = self.preprocess_arxiv()
        
        training_data = {
            'summarization': self._prepare_summarization_data(scitldr_df),
            'similarity': self._prepare_similarity_data(arxiv_df),
            'topic_modeling': self._prepare_topic_data(arxiv_df)
        }
        
        # Save training data
        for task, data in training_data.items():
            output_path = os.path.join(self.output_dir, f'{task}_training.json')
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        
        return training_data
    
    def _prepare_summarization_data(self, df: pd.DataFrame) -> List[Dict]:
        """Prepare data for summarization training"""
        training_data = []
        
        for _, row in df.iterrows():
            if row['source'] and row['target']:
                training_data.append({
                    'input': row['source'],
                    'output': row['target'],
                    'paper_id': row['paper_id'],
                    'title': row['title']
                })
        
        return training_data
    
    def _prepare_similarity_data(self, df: pd.DataFrame) -> List[Dict]:
        """Prepare data for similarity training"""
        # Group by categories for similarity
        category_groups = df.groupby('categories').agg({
            'paper_id': list,
            'title': list,
            'abstract': list
        }).reset_index()
        
        similarity_data = []
        for _, group in category_groups.iterrows():
            if len(group['paper_id']) > 1:
                similarity_data.append({
                    'category': group['categories'],
                    'papers': [
                        {'paper_id': pid, 'title': t, 'abstract': a}
                        for pid, t, a in zip(group['paper_id'], group['title'], group['abstract'])
                    ]
                })
        
        return similarity_data
    
    def _prepare_topic_data(self, df: pd.DataFrame) -> List[Dict]:
        """Prepare data for topic modeling"""
        topic_data = []
        
        for _, row in df.iterrows():
            if row['abstract'] and row['categories']:
                topic_data.append({
                    'paper_id': row['paper_id'],
                    'text': f"{row['title']} {row['abstract']}",
                    'categories': row['categories'],
                    'title': row['title']
                })
        
        return topic_data

if __name__ == "__main__":
    preprocessor = DatasetPreprocessor()
    training_data = preprocessor.create_training_data()
    print("Dataset preprocessing completed!")