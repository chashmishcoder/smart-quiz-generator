import re
import math
from collections import Counter
from typing import List, Dict, Tuple

def preprocess_text(text: str) -> List[str]:
    """Clean text and split into chunks of 200-300 words"""
    # Clean the text
    cleaned_text = clean_text(text)
    
    # Split into sentences
    sentences = re.split(r'[.!?]+', cleaned_text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    # Group sentences into chunks of 200-300 words
    chunks = []
    current_chunk = []
    current_word_count = 0
    
    for sentence in sentences:
        words = sentence.split()
        sentence_word_count = len(words)
        
        # If adding this sentence would exceed 300 words, start a new chunk
        if current_word_count + sentence_word_count > 300 and current_chunk:
            chunk_text = '. '.join(current_chunk) + '.'
            if current_word_count >= 200:  # Only add chunks with at least 200 words
                chunks.append(chunk_text)
            current_chunk = [sentence]
            current_word_count = sentence_word_count
        else:
            current_chunk.append(sentence)
            current_word_count += sentence_word_count
    
    # Add the last chunk if it has enough words
    if current_chunk and current_word_count >= 200:
        chunk_text = '. '.join(current_chunk) + '.'
        chunks.append(chunk_text)
    
    # If no chunks meet the word count, return the original text as a single chunk
    if not chunks:
        chunks = [cleaned_text]
    
    return chunks

def clean_text(text: str) -> str:
    """Clean text using simple regex patterns"""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s.!?,-]', '', text)
    
    # Remove multiple consecutive punctuation
    text = re.sub(r'[.]{2,}', '.', text)
    text = re.sub(r'[!]{2,}', '!', text)
    text = re.sub(r'[?]{2,}', '?', text)
    
    # Ensure proper spacing after punctuation
    text = re.sub(r'([.!?])([A-Z])', r'\1 \2', text)
    
    return text.strip()

def extract_key_concepts(text: str) -> List[str]:
    """Extract top 10 key concepts using TF-IDF approach"""
    # Clean and tokenize text
    cleaned_text = clean_text(text.lower())
    
    # Remove common stop words (simple list)
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
        'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
        'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those',
        'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them', 'my', 'your',
        'his', 'its', 'our', 'their', 'from', 'up', 'about', 'into', 'through', 'during', 'before',
        'after', 'above', 'below', 'between', 'among', 'around', 'near', 'far', 'here', 'there',
        'where', 'when', 'why', 'how', 'what', 'which', 'who', 'whom', 'whose', 'if', 'unless',
        'while', 'although', 'because', 'since', 'so', 'than', 'such', 'both', 'either', 'neither'
    }
    
    # Extract words (2+ characters, not pure numbers)
    words = re.findall(r'\b[a-zA-Z]{2,}\b', cleaned_text)
    
    # Filter out stop words and short words
    meaningful_words = [word for word in words if word not in stop_words and len(word) > 2]
    
    # Calculate word frequencies
    word_freq = Counter(meaningful_words)
    
    # Simple TF-IDF scoring (using log frequency)
    scores = {}
    total_words = len(meaningful_words)
    
    for word, freq in word_freq.items():
        # Term frequency (normalized)
        tf = freq / total_words
        
        # Inverse document frequency (simplified - boost less common words)
        idf = math.log(total_words / freq) if freq > 0 else 0
        
        # TF-IDF score
        scores[word] = tf * idf
    
    # Get top 10 concepts
    top_concepts = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:10]
    
    # Return just the words
    return [concept[0] for concept in top_concepts]

def group_questions_by_topic(questions: List[Dict], text: str) -> Dict[str, List[Dict]]:
    """Group questions by topic based on key concepts"""
    key_concepts = extract_key_concepts(text)
    
    # Initialize topic groups
    topic_groups = {concept: [] for concept in key_concepts[:5]}  # Top 5 concepts as topics
    topic_groups['general'] = []
    
    for question in questions:
        question_text = question.get('question', '').lower()
        question_assigned = False
        
        # Try to match question with topics based on concept presence
        for concept in key_concepts[:5]:
            if concept in question_text:
                topic_groups[concept].append(question)
                question_assigned = True
                break
        
        # If no specific topic match, add to general
        if not question_assigned:
            topic_groups['general'].append(question)
    
    # Remove empty groups
    topic_groups = {topic: questions for topic, questions in topic_groups.items() if questions}
    
    return topic_groups

def determine_optimal_question_count(text_length: int) -> Dict[str, int]:
    """Determine optimal question count based on text length"""
    # Calculate based on text length
    if text_length < 200:
        recommended = 2
        max_reasonable = 3
    elif text_length < 500:
        recommended = 3
        max_reasonable = 5
    elif text_length < 1000:
        recommended = 5
        max_reasonable = 8
    elif text_length < 2000:
        recommended = 8
        max_reasonable = 12
    else:
        recommended = 10
        max_reasonable = 15
    
    return {
        'recommended': recommended,
        'maximum': max_reasonable,
        'minimum': max(1, recommended // 2)
    }

def analyze_text_complexity(text: str) -> Dict[str, any]:
    """Analyze text complexity for better question generation"""
    words = text.split()
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    # Basic metrics
    word_count = len(words)
    sentence_count = len(sentences)
    avg_words_per_sentence = word_count / sentence_count if sentence_count > 0 else 0
    
    # Vocabulary complexity (unique words ratio)
    unique_words = len(set(word.lower() for word in words))
    vocabulary_complexity = unique_words / word_count if word_count > 0 else 0
    
    # Determine complexity level
    if avg_words_per_sentence > 20 and vocabulary_complexity > 0.6:
        complexity = 'high'
    elif avg_words_per_sentence > 15 and vocabulary_complexity > 0.4:
        complexity = 'medium'
    else:
        complexity = 'low'
    
    return {
        'word_count': word_count,
        'sentence_count': sentence_count,
        'avg_words_per_sentence': round(avg_words_per_sentence, 1),
        'vocabulary_complexity': round(vocabulary_complexity, 2),
        'difficulty': complexity,  # Fixed: use 'difficulty' instead of 'complexity_level'
        'complexity_level': complexity,  # Keep for backward compatibility
        'key_concepts': extract_key_concepts(text)
    }
