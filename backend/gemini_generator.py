import google.generativeai as genai
import os
import json
import re
import random
from typing import List, Dict
from dotenv import load_dotenv

# Import our modules
from processors import preprocess_text, extract_key_concepts, group_questions_by_topic, analyze_text_complexity
from prompts import (
    get_difficulty_prompt, get_bloom_level_for_difficulty, get_distractor_prompt, 
    get_explanation_prompt, detect_subject_area, BLOOM_QUESTION_STARTERS
)

# Load environment variables
load_dotenv()

class GeminiQuestionGenerator:
    def __init__(self):
        self.model = None
        self.model_loaded = False
        self.load_model()
    
    def load_model(self):
        """Initialize Gemini API with error handling"""
        try:
            api_key = os.getenv('GEMINI_API_KEY')
            if not api_key or api_key == 'your_gemini_api_key_here':
                print("⚠️  Gemini API key not found or not set.")
                print("📝 Please add your Gemini API key to the .env file:")
                print("   GEMINI_API_KEY=your_actual_api_key_here")
                print("🔧 Running in fallback mode - will generate mock questions")
                self.model_loaded = False
                return
            
            print("🔗 Connecting to Gemini API...")
            genai.configure(api_key=api_key)
            
            # Initialize the model
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            
            # Test the connection
            test_response = self.model.generate_content("Test connection")
            if test_response:
                self.model_loaded = True
                print("✅ Gemini API connected successfully!")
            else:
                raise Exception("No response from Gemini API")
                
        except Exception as e:
            print(f"❌ Error connecting to Gemini API: {e}")
            print("🔧 Running in fallback mode - will generate mock questions")
            self.model_loaded = False
    
    def is_model_loaded(self):
        """Check if the model is loaded and ready"""
        return self.model_loaded
    
    def generate_mcq(self, text: str, num_questions: int = 5, difficulty: str = "medium") -> List[Dict]:
        """Generate multiple choice questions using Gemini API"""
        try:
            if not self.model_loaded:
                print("⚠️  Gemini API not available, generating mock questions")
                return self._generate_mock_questions(text, num_questions)
            
            # Normalize difficulty
            difficulty = difficulty.lower()
            print(f"🎯 Generating {num_questions} questions with difficulty: {difficulty}")
            
            # Preprocess and analyze the text
            processed_text = preprocess_text(text)
            complexity = analyze_text_complexity(text)
            subject_area = detect_subject_area(text)
            
            print(f"📊 Text Analysis: {complexity['word_count']} words, {complexity['difficulty']} difficulty")
            print(f"📚 Subject Area: {subject_area}")
            
            # Generate questions using Gemini
            questions = self._generate_questions_with_gemini(processed_text, num_questions, difficulty, subject_area)
            
            # For now, skip grouping to avoid errors - we can add it back later
            print(f"✅ Generated {len(questions)} questions")
            
            return questions
            
        except Exception as e:
            print(f"❌ Error in question generation: {e}")
            import traceback
            traceback.print_exc()
            return self._generate_mock_questions(text, num_questions)
    
    def _generate_questions_with_gemini(self, text: str, num_questions: int, difficulty: str, subject_area: str) -> List[Dict]:
        """Generate questions using Gemini API"""
        questions = []
        
        # Create comprehensive prompt for Gemini
        prompt = self._create_gemini_prompt(text, num_questions, difficulty, subject_area)
        
        try:
            response = self.model.generate_content(prompt)
            
            if response and response.text:
                # Parse the JSON response from Gemini
                questions_data = self._parse_gemini_response(response.text)
                
                for i, q_data in enumerate(questions_data):
                    if i >= num_questions:
                        break
                    
                    # Validate and structure the question
                    question = self._structure_question(q_data, difficulty, subject_area)
                    if question:
                        questions.append(question)
            
        except Exception as e:
            print(f"❌ Error generating questions with Gemini: {e}")
            # Fallback to mock questions
            return self._generate_mock_questions(text, num_questions)
        
        return questions
    
    def _create_gemini_prompt(self, text: str, num_questions: int, difficulty: str, subject_area: str) -> str:
        """Create a comprehensive prompt for Gemini API"""
        
        bloom_level = get_bloom_level_for_difficulty(difficulty)
        
        prompt = f"""
You are an expert educational content creator. Generate {num_questions} high-quality multiple choice questions based on the following text.

TEXT TO ANALYZE:
{text}

REQUIREMENTS:
- Subject Area: {subject_area}
- Difficulty: {difficulty}
- Bloom's Taxonomy Level: {bloom_level}
- Generate exactly {num_questions} questions
- Each question should have 4 options (A, B, C, D)
- Only one correct answer per question
- Include detailed explanations for correct answers
- Make distractors plausible but clearly incorrect
- Questions should test understanding, not just memorization

RESPONSE FORMAT (JSON):
Return a JSON array with this exact structure:
[
  {{
    "question": "Clear, specific question text?",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "correct_answer": "The exact text of the correct option",
    "explanation": "Detailed explanation of why this answer is correct",
    "difficulty": "{difficulty}",
    "bloom_level": "{bloom_level}",
    "category": "topic category"
  }}
]

Generate the questions now:
"""
        return prompt
    
    def _parse_gemini_response(self, response_text: str) -> List[Dict]:
        """Parse Gemini's JSON response"""
        try:
            # Clean up the response text
            cleaned_text = response_text.strip()
            
            # Remove markdown code blocks if present
            if cleaned_text.startswith('```json'):
                cleaned_text = cleaned_text[7:]
            if cleaned_text.endswith('```'):
                cleaned_text = cleaned_text[:-3]
            
            # Remove any extra text before/after JSON
            start_bracket = cleaned_text.find('[')
            end_bracket = cleaned_text.rfind(']')
            
            if start_bracket != -1 and end_bracket != -1:
                json_text = cleaned_text[start_bracket:end_bracket+1]
                questions_data = json.loads(json_text)
                return questions_data
            else:
                raise ValueError("No valid JSON array found in response")
                
        except Exception as e:
            print(f"❌ Error parsing Gemini response: {e}")
            print(f"Raw response: {response_text[:200]}...")
            return []
    
    def _structure_question(self, q_data: Dict, difficulty: str, subject_area: str) -> Dict:
        """Structure and validate a single question"""
        try:
            # Validate required fields
            if not all(key in q_data for key in ['question', 'options', 'correct_answer', 'explanation']):
                print(f"⚠️  Missing required fields in question data")
                return None
            
            # Ensure we have exactly 4 options
            options = q_data['options']
            if len(options) != 4:
                print(f"⚠️  Question has {len(options)} options instead of 4")
                return None
            
            # Validate correct answer is in options
            correct_answer = q_data['correct_answer']
            if correct_answer not in options:
                print(f"⚠️  Correct answer not found in options")
                return None
            
            # Structure the final question
            question = {
                "id": random.randint(1000, 9999),
                "question": q_data['question'].strip(),
                "options": options,
                "correct_answer": correct_answer,
                "explanation": q_data['explanation'].strip(),
                "difficulty": q_data.get('difficulty', difficulty).lower(),
                "bloom_level": q_data.get('bloom_level', get_bloom_level_for_difficulty(difficulty)),
                "category": q_data.get('category', subject_area),
                "subject_area": subject_area,
                "created_at": "2025-09-04"  # Current date
            }
            
            return question
            
        except Exception as e:
            print(f"❌ Error structuring question: {e}")
            return None
    
    def _generate_mock_questions(self, text: str, num_questions: int) -> List[Dict]:
        """Generate mock questions when Gemini API is not available"""
        questions = []
        
        # Split text into words to extract key terms
        words = text.split()
        key_terms = [word.strip('.,!?') for word in words if len(word) > 5][:10]
        
        for i in range(num_questions):
            # Generate a simple question based on the text
            if key_terms:
                term = random.choice(key_terms)
                question_text = f"What is the significance of {term} in the given context?"
            else:
                question_text = f"Based on the text, which statement is most accurate?"
            
            # Generate mock options
            options = [
                f"Option A: Related to {key_terms[0] if key_terms else 'concept'}",
                f"Option B: Connected to {key_terms[1] if len(key_terms) > 1 else 'topic'}",
                f"Option C: Associated with {key_terms[2] if len(key_terms) > 2 else 'subject'}",
                f"Option D: Linked to {key_terms[3] if len(key_terms) > 3 else 'theme'}"
            ]
            
            correct_answer = options[0]
            
            question = {
                "id": 9000 + i,
                "question": question_text,
                "options": options,
                "correct_answer": correct_answer,
                "explanation": f"This is a mock explanation for demonstration purposes. The correct answer relates to the key concepts in the text.",
                "difficulty": "medium",
                "bloom_level": "understand",
                "category": "Mock Questions",
                "subject_area": "general",
                "created_at": "2025-09-04"
            }
            
            questions.append(question)
        
        return questions

# Create a global instance
question_generator = GeminiQuestionGenerator()
