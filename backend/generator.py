from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch
import re
import random
from typing import List, Dict

# Import our new modules
from processors import preprocess_text, extract_key_concepts, group_questions_by_topic, analyze_text_complexity
from prompts import (
    get_difficulty_prompt, get_bloom_level_for_difficulty, get_distractor_prompt, 
    get_explanation_prompt, detect_subject_area, BLOOM_QUESTION_STARTERS
)

class QuestionGenerator:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.model_loaded = False
        self.load_model()
    
    def load_model(self):
        """Load the Flan-T5-Large model with error handling"""
        try:
            print("Loading google/flan-t5-large model...")
            self.tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-large")
            self.model = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-large")
            self.model_loaded = True
            print("✅ Model loaded successfully!")
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            print("💡 This might be due to Hugging Face authentication or network issues")
            print("🔧 Running in fallback mode - will generate mock questions")
            self.model_loaded = False
    
    def is_model_loaded(self):
        """Check if model is loaded"""
        return self.model_loaded
    
    def generate_mcq(self, text: str, num_questions: int, difficulty: str = "medium") -> List[Dict]:
        """Generate multiple choice questions from text with enhanced processing"""
        questions = []
        
        # If model not loaded, generate mock questions for testing
        if not self.model_loaded:
            return self._generate_mock_questions(text, num_questions)
        
        # Analyze text complexity and extract key concepts
        text_analysis = analyze_text_complexity(text)
        subject_area = detect_subject_area(text)
        
        # Preprocess text into optimal chunks
        text_chunks = preprocess_text(text)
        
        # Determine how many questions to generate from each chunk
        questions_per_chunk = max(1, num_questions // len(text_chunks))
        remaining_questions = num_questions
        
        for chunk_index, chunk in enumerate(text_chunks):
            if remaining_questions <= 0:
                break
                
            # Determine questions to generate from this chunk
            chunk_questions = min(questions_per_chunk, remaining_questions)
            if chunk_index == len(text_chunks) - 1:  # Last chunk gets remaining questions
                chunk_questions = remaining_questions
            
            # Extract key concepts from this chunk
            chunk_concepts = extract_key_concepts(chunk)
            
            for q_index in range(chunk_questions):
                try:
                    # Select concept for this question
                    concept = chunk_concepts[q_index % len(chunk_concepts)] if chunk_concepts else "main concept"
                    
                    # Generate question using enhanced prompts
                    question_prompt = get_difficulty_prompt(difficulty, chunk)
                    question_text = self._generate_text(question_prompt, max_length=100)
                    
                    # Clean up question text
                    question_text = self._clean_question_text(question_text)
                    
                    # Generate correct answer with context awareness
                    answer_prompt = f"Based on this text about {concept}, what is the correct answer to: {question_text}? Context: {chunk}"
                    correct_answer = self._generate_text(answer_prompt, max_length=50)
                    correct_answer = correct_answer.strip()
                    
                    # Generate enhanced distractors
                    distractors = self._generate_enhanced_distractors(correct_answer, chunk, difficulty, subject_area)
                    
                    # Create options list and shuffle
                    options = [correct_answer] + distractors
                    random.shuffle(options)
                    
                    # Determine Bloom's taxonomy level
                    bloom_level = self._determine_bloom_level(question_text, difficulty)
                    
                    # Generate enhanced explanation
                    explanation = self._generate_enhanced_explanation(question_text, correct_answer, chunk, difficulty)
                    
                    question_data = {
                        "question": question_text,
                        "options": options,
                        "correct_answer": correct_answer,
                        "explanation": explanation,
                        "difficulty": difficulty,
                        "bloom_level": bloom_level,
                        "subject_area": subject_area,
                        "key_concept": concept
                    }
                    
                    questions.append(question_data)
                    remaining_questions -= 1
                    
                except Exception as e:
                    print(f"Error generating question {q_index + 1} from chunk {chunk_index + 1}: {e}")
                    continue
        
        # Group questions by topic for better organization
        if len(questions) > 1:
            grouped_questions = group_questions_by_topic(questions, text)
            print(f"Generated {len(questions)} questions grouped into {len(grouped_questions)} topics")
        
        return questions
    
    def _generate_enhanced_distractors(self, correct_answer: str, context: str, difficulty: str, subject_area: str) -> List[str]:
        """Generate enhanced distractors based on difficulty and subject area"""
        distractors = []
        
        # Determine distractor type based on difficulty
        if difficulty.lower() == "easy":
            distractor_type = "factual"
        elif difficulty.lower() == "hard":
            distractor_type = "analytical"
        else:
            distractor_type = "conceptual"
        
        # Generate distractors using enhanced prompts
        distractor_prompt = get_distractor_prompt(distractor_type, correct_answer, context)
        
        for i in range(3):
            try:
                distractor_text = self._generate_text(distractor_prompt, max_length=50)
                distractor = distractor_text.strip()
                
                # Clean and validate distractor
                if distractor and distractor != correct_answer and distractor not in distractors:
                    distractors.append(distractor)
                else:
                    # Fallback distractor
                    fallback = f"Alternative option {i + 1}"
                    distractors.append(fallback)
            except Exception:
                fallback = f"Option {chr(66 + i)}"  # B, C, D
                distractors.append(fallback)
        
        # Ensure we have exactly 3 distractors
        while len(distractors) < 3:
            distractors.append(f"Additional option {len(distractors) + 1}")
        
        return distractors[:3]
    
    def _determine_bloom_level(self, question_text: str, difficulty: str) -> str:
        """Determine Bloom's taxonomy level based on question text and difficulty"""
        question_lower = question_text.lower()
        
        # Get appropriate Bloom level for difficulty
        primary_level = get_bloom_level_for_difficulty(difficulty)
        
        # Check question starters to refine the level
        for level, starters in BLOOM_QUESTION_STARTERS.items():
            for starter in starters:
                if question_lower.startswith(starter.lower()):
                    return level
        
        return primary_level
    
    def _generate_enhanced_explanation(self, question: str, answer: str, context: str, difficulty: str) -> str:
        """Generate enhanced explanation based on difficulty level"""
        if difficulty.lower() == "easy":
            explanation_type = "basic"
        elif difficulty.lower() == "hard":
            explanation_type = "analytical"
        else:
            explanation_type = "detailed"
        
        explanation_prompt = get_explanation_prompt(explanation_type, answer, question)
        explanation = self._generate_text(explanation_prompt, max_length=150)
        
        return explanation.strip()
    
    def _clean_question_text(self, question_text: str) -> str:
        """Clean and format question text"""
        # Remove any unwanted prefixes
        question_text = re.sub(r'^(Question:|Q:)\s*', '', question_text.strip())
        
        # Ensure question ends with question mark
        if not question_text.endswith('?'):
            question_text += '?'
        
        # Remove any option text that might have been generated
        question_text = re.sub(r'Options?:\s*[A-D]\..*$', '', question_text, flags=re.IGNORECASE | re.DOTALL)
        question_text = re.sub(r'Answer:\s*[A-D].*$', '', question_text, flags=re.IGNORECASE | re.DOTALL)
        
        return question_text.strip()
        """Generate 3 wrong answers (distractors)"""
        distractors = []
        
        # Method 1: Generate alternative answers
        prompt1 = f"Generate an incorrect but plausible alternative to: {correct_answer}"
        distractor1 = self._generate_text(prompt1, max_length=50)
        distractors.append(distractor1)
        
        # Method 2: Generate contradictory answer
        prompt2 = f"Generate an answer that contradicts: {correct_answer}"
        distractor2 = self._generate_text(prompt2, max_length=50)
        distractors.append(distractor2)
        
        # Method 3: Generate related but incorrect answer
        prompt3 = f"Generate a related but incorrect answer for the context: {context}"
        distractor3 = self._generate_text(prompt3, max_length=50)
        distractors.append(distractor3)
        
        # Clean and ensure uniqueness
        cleaned_distractors = []
        for d in distractors:
            cleaned = d.strip()
            if cleaned and cleaned != correct_answer and cleaned not in cleaned_distractors:
                cleaned_distractors.append(cleaned)
        
        # Ensure we have exactly 3 distractors
        while len(cleaned_distractors) < 3:
            fallback = f"Option {len(cleaned_distractors) + 1}"
            cleaned_distractors.append(fallback)
        
        return cleaned_distractors[:3]
    
    def add_explanation(self, question: str, answer: str, context: str) -> str:
        """Add explanation for the answer"""
        prompt = f"Explain why '{answer}' is the correct answer to '{question}' based on this context: {context}"
        explanation = self._generate_text(prompt, max_length=150)
        return explanation
    
    def _generate_text(self, prompt: str, max_length: int = 100) -> str:
        """Generate text using the model"""
        try:
            inputs = self.tokenizer(prompt, return_tensors="pt", max_length=512, truncation=True)
            
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs.input_ids,
                    max_length=max_length,
                    num_return_sequences=1,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Clean up the generated text
            generated_text = generated_text.strip()
            if generated_text.endswith('?') and 'question' in prompt.lower():
                return generated_text
            
            return generated_text
            
        except Exception as e:
            print(f"Error generating text: {e}")
            return "Generated content"
    
    def _generate_mock_questions(self, text: str, num_questions: int) -> List[Dict]:
        """Generate mock questions for testing when model is not available"""
        questions = []
        
        # Split text into words to extract key terms
        words = text.split()
        key_terms = [word.strip('.,!?') for word in words if len(word) > 5][:10]
        
        for i in range(num_questions):
            # Generate a simple question based on the text
            if key_terms:
                term = key_terms[i % len(key_terms)]
                question_text = f"What is the significance of '{term}' in the given context?"
            else:
                question_text = f"What is the main topic discussed in question {i+1}?"
            
            # Generate options
            correct_answer = f"Key concept related to {term if key_terms else 'main topic'}"
            distractors = [
                f"Alternative concept A",
                f"Alternative concept B", 
                f"Alternative concept C"
            ]
            
            options = [correct_answer] + distractors
            random.shuffle(options)
            
            explanation = f"Based on the provided text, the correct answer relates to the main concepts discussed."
            
            question_data = {
                "question": question_text,
                "options": options,
                "correct_answer": correct_answer,
                "explanation": explanation,
                "difficulty": "medium",
                "bloom_level": "understand"
            }
            
            questions.append(question_data)
        
        return questions

# Global instance
question_generator = QuestionGenerator()
