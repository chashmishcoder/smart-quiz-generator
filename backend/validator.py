import re
from typing import Dict, List
from sentence_transformers import SentenceTransformer
import numpy as np

# Load sentence transformer model for similarity checking
try:
    similarity_model = SentenceTransformer('all-MiniLM-L6-v2')
    SIMILARITY_MODEL_LOADED = True
except:
    SIMILARITY_MODEL_LOADED = False
    similarity_model = None

def validate_question_quality(question: Dict) -> Dict:
    """Validate the quality of a question and return score 0-100"""
    score = 100
    feedback = []
    quality_metrics = {}
    
    question_text = question.get("question", "")
    options = question.get("options", [])
    correct_answer = question.get("correct_answer", "")
    explanation = question.get("explanation", "")
    
    # Check question structure
    if not question_text.endswith('?'):
        score -= 10
        feedback.append("Question should end with question mark")
    
    if len(question_text) < 10:
        score -= 20
        feedback.append("Question too short")
    
    if len(question_text) > 200:
        score -= 10
        feedback.append("Question too long")
    
    # Check options
    if len(options) != 4:
        score -= 30
        feedback.append(f"Should have 4 options, found {len(options)}")
    
    if correct_answer not in options:
        score -= 40
        feedback.append("Correct answer not found in options")
    
    # Check for duplicate options
    if len(set(options)) != len(options):
        score -= 25
        feedback.append("Duplicate options found")
    
    # Check option lengths
    avg_option_length = sum(len(opt) for opt in options) / len(options) if options else 0
    if avg_option_length < 5:
        score -= 15
        feedback.append("Options too short")
    
    # Check explanation
    if len(explanation) < 10:
        score -= 10
        feedback.append("Explanation too short")
    
    # Distractor quality check
    if len(options) >= 4:
        distractor_score = score_distractor_quality(options, correct_answer)
        quality_metrics["distractor_quality"] = distractor_score
        if distractor_score < 50:
            score -= 20
            feedback.append("Poor quality distractors")
    
    # Bloom level check
    bloom_level = check_bloom_level(question_text)
    quality_metrics["bloom_level"] = bloom_level
    
    # Final score adjustments
    score = max(0, min(100, score))
    
    quality_metrics.update({
        "question_length": len(question_text),
        "option_count": len(options),
        "explanation_length": len(explanation),
        "has_question_mark": question_text.endswith('?'),
        "unique_options": len(set(options)) == len(options)
    })
    
    return {
        "score": score,
        "feedback": "; ".join(feedback) if feedback else "Good quality question",
        "quality_metrics": quality_metrics
    }

def check_bloom_level(question_text: str) -> str:
    """Determine Bloom's taxonomy level based on question text"""
    question_lower = question_text.lower()
    
    # Remember level keywords
    remember_keywords = ['what', 'when', 'where', 'who', 'define', 'list', 'name', 'identify']
    understand_keywords = ['explain', 'describe', 'summarize', 'interpret', 'compare']
    apply_keywords = ['apply', 'demonstrate', 'solve', 'use', 'implement']
    analyze_keywords = ['analyze', 'examine', 'compare', 'contrast', 'differentiate']
    evaluate_keywords = ['evaluate', 'assess', 'judge', 'critique', 'justify']
    create_keywords = ['create', 'design', 'develop', 'formulate', 'construct']
    
    if any(keyword in question_lower for keyword in create_keywords):
        return "create"
    elif any(keyword in question_lower for keyword in evaluate_keywords):
        return "evaluate"
    elif any(keyword in question_lower for keyword in analyze_keywords):
        return "analyze"
    elif any(keyword in question_lower for keyword in apply_keywords):
        return "apply"
    elif any(keyword in question_lower for keyword in understand_keywords):
        return "understand"
    elif any(keyword in question_lower for keyword in remember_keywords):
        return "remember"
    else:
        return "understand"  # default

def score_distractor_quality(options: List[str], correct_answer: str) -> int:
    """Score the quality of distractors (wrong answers) 0-100"""
    if not SIMILARITY_MODEL_LOADED:
        return 70  # Default score if similarity model not available
    
    try:
        distractors = [opt for opt in options if opt != correct_answer]
        if len(distractors) == 0:
            return 0
        
        # Check similarity between distractors and correct answer
        all_options = [correct_answer] + distractors
        embeddings = similarity_model.encode(all_options)
        
        scores = []
        for i, distractor_emb in enumerate(embeddings[1:], 1):
            # Calculate similarity with correct answer
            similarity = np.dot(embeddings[0], distractor_emb) / (
                np.linalg.norm(embeddings[0]) * np.linalg.norm(distractor_emb)
            )
            
            # Good distractors should be somewhat similar but not too similar
            # Ideal similarity range: 0.3 - 0.7
            if 0.3 <= similarity <= 0.7:
                scores.append(100)
            elif similarity < 0.3:
                scores.append(max(0, 100 - (0.3 - similarity) * 200))
            else:  # similarity > 0.7
                scores.append(max(0, 100 - (similarity - 0.7) * 300))
        
        return int(np.mean(scores)) if scores else 50
    
    except Exception as e:
        print(f"Error scoring distractors: {e}")
        return 70  # Default score on error

def validate_multiple_questions(questions: List[Dict]) -> List[Dict]:
    """Validate multiple questions and return results"""
    results = []
    for question in questions:
        validation_result = validate_question_quality(question)
        results.append(validation_result)
    return results
