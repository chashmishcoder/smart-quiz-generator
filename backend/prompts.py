"""
Prompt templates and configurations for question generation
"""

# Base prompt templates
QUESTION_PROMPT = "Create a multiple choice question testing understanding of: {text}"

DISTRACTOR_PROMPT = "Generate 3 incorrect but plausible answers for: {correct_answer} Context: {context}"

EXPLANATION_PROMPT = "Explain why {answer} is correct for question: {question}"

# Bloom's Taxonomy levels
BLOOM_LEVELS = ["Remember", "Understand", "Apply", "Analyze", "Evaluate", "Create"]

# Difficulty-based prompts
DIFFICULTY_PROMPTS = {
    "easy": "basic facts",
    "medium": "conceptual understanding", 
    "hard": "critical analysis",
    "mixed": "various cognitive levels"
}

# Enhanced question generation prompts by difficulty
ENHANCED_QUESTION_PROMPTS = {
    "easy": {
        "template": "Create a simple multiple choice question that tests {focus} from this text: {text}",
        "focus": "basic facts and recall",
        "bloom_levels": ["Remember", "Understand"],
        "instructions": "Focus on who, what, where, when questions. Use direct facts from the text."
    },
    "medium": {
        "template": "Create a multiple choice question that tests {focus} from this text: {text}",
        "focus": "conceptual understanding and application",
        "bloom_levels": ["Understand", "Apply"],
        "instructions": "Focus on why and how questions. Test comprehension and relationships between concepts."
    },
    "hard": {
        "template": "Create a challenging multiple choice question that tests {focus} from this text: {text}",
        "focus": "critical analysis and evaluation",
        "bloom_levels": ["Analyze", "Evaluate", "Create"],
        "instructions": "Focus on analysis, synthesis, and evaluation. Require deep thinking and inference."
    },
    "mixed": {
        "template": "Create multiple choice questions that test {focus} from this text: {text}",
        "focus": "various cognitive levels from basic recall to critical analysis",
        "bloom_levels": ["Remember", "Understand", "Apply", "Analyze"],
        "instructions": "Create questions of varying difficulty levels, from basic facts to analytical thinking."
    }
}

# Context-aware distractor generation prompts
ENHANCED_DISTRACTOR_PROMPTS = {
    "conceptual": "Generate 3 incorrect but conceptually related answers for '{correct_answer}'. Make them plausible but clearly wrong when analyzed. Context: {context}",
    "factual": "Generate 3 incorrect but factually similar answers for '{correct_answer}'. Use related numbers, dates, or names that could confuse students. Context: {context}",
    "analytical": "Generate 3 incorrect but logically structured answers for '{correct_answer}'. Make them sound reasonable but contain subtle errors. Context: {context}"
}

# Explanation generation prompts
ENHANCED_EXPLANATION_PROMPTS = {
    "basic": "Provide a clear, simple explanation for why '{answer}' is the correct answer to the question: '{question}'. Reference the source text.",
    "detailed": "Provide a comprehensive explanation for why '{answer}' is correct for: '{question}'. Include relevant context and explain why other options are incorrect.",
    "analytical": "Provide an analytical explanation for why '{answer}' is the best answer to: '{question}'. Discuss the reasoning process and key concepts involved."
}

# Bloom's taxonomy question starters by level
BLOOM_QUESTION_STARTERS = {
    "Remember": [
        "What is", "Who was", "When did", "Where is", "Which of the following",
        "Define", "List", "Name", "Identify", "State"
    ],
    "Understand": [
        "Explain why", "Describe how", "What does this mean", "Summarize",
        "Compare", "Contrast", "Interpret", "Paraphrase"
    ],
    "Apply": [
        "How would you use", "What would happen if", "Apply the concept",
        "Demonstrate", "Solve", "Show how", "Use this information"
    ],
    "Analyze": [
        "Why do you think", "What evidence supports", "What are the parts",
        "Analyze", "Examine", "What factors", "Break down"
    ],
    "Evaluate": [
        "Which is better", "Judge the value", "What criteria would you use",
        "Evaluate", "Critique", "Justify", "Assess"
    ],
    "Create": [
        "Design a", "Create a new", "What would you propose",
        "Develop", "Formulate", "Construct", "Generate"
    ]
}

# Subject-specific prompt templates
SUBJECT_PROMPTS = {
    "science": {
        "question": "Based on this scientific text, create a question that tests understanding of: {concept}",
        "distractor": "Generate scientifically plausible but incorrect alternatives to: {correct_answer}",
        "keywords": ["process", "theory", "hypothesis", "experiment", "observation", "analysis"]
    },
    "history": {
        "question": "Based on this historical text, create a question about: {concept}",
        "distractor": "Generate historically plausible but incorrect alternatives to: {correct_answer}",
        "keywords": ["event", "cause", "effect", "timeline", "significance", "impact"]
    },
    "literature": {
        "question": "Based on this literary text, create a question analyzing: {concept}",
        "distractor": "Generate literarily plausible but incorrect interpretations of: {correct_answer}",
        "keywords": ["theme", "character", "plot", "symbolism", "analysis", "interpretation"]
    },
    "general": {
        "question": "Based on this text, create a question testing understanding of: {concept}",
        "distractor": "Generate plausible but incorrect alternatives to: {correct_answer}",
        "keywords": ["concept", "idea", "information", "knowledge", "understanding", "application"]
    }
}

def get_difficulty_prompt(difficulty: str, text: str) -> str:
    """Get appropriate prompt based on difficulty level"""
    difficulty = difficulty.lower()
    if difficulty in ENHANCED_QUESTION_PROMPTS:
        prompt_config = ENHANCED_QUESTION_PROMPTS[difficulty]
        return prompt_config["template"].format(
            focus=prompt_config["focus"],
            text=text
        )
    else:
        return QUESTION_PROMPT.format(text=text)

def get_bloom_level_for_difficulty(difficulty: str) -> str:
    """Map difficulty to appropriate Bloom's level"""
    difficulty = difficulty.lower()
    if difficulty in ENHANCED_QUESTION_PROMPTS:
        levels = ENHANCED_QUESTION_PROMPTS[difficulty]["bloom_levels"]
        return levels[0]  # Return primary level for the difficulty
    return "Understand"  # Default

def get_distractor_prompt(distractor_type: str, correct_answer: str, context: str) -> str:
    """Get enhanced distractor prompt based on type"""
    if distractor_type in ENHANCED_DISTRACTOR_PROMPTS:
        return ENHANCED_DISTRACTOR_PROMPTS[distractor_type].format(
            correct_answer=correct_answer,
            context=context
        )
    else:
        return DISTRACTOR_PROMPT.format(
            correct_answer=correct_answer,
            context=context
        )

def get_explanation_prompt(explanation_type: str, answer: str, question: str) -> str:
    """Get enhanced explanation prompt based on type"""
    if explanation_type in ENHANCED_EXPLANATION_PROMPTS:
        return ENHANCED_EXPLANATION_PROMPTS[explanation_type].format(
            answer=answer,
            question=question
        )
    else:
        return EXPLANATION_PROMPT.format(
            answer=answer,
            question=question
        )

def detect_subject_area(text: str) -> str:
    """Detect the subject area of the text for specialized prompts"""
    text_lower = text.lower()
    
    science_keywords = ["experiment", "hypothesis", "theory", "analysis", "scientific", "research", "study", "data", "observation", "method"]
    history_keywords = ["century", "war", "empire", "historical", "period", "era", "ancient", "revolution", "society", "civilization"]
    literature_keywords = ["character", "theme", "plot", "author", "literary", "novel", "story", "poem", "narrative", "symbolism"]
    
    science_count = sum(1 for keyword in science_keywords if keyword in text_lower)
    history_count = sum(1 for keyword in history_keywords if keyword in text_lower)
    literature_count = sum(1 for keyword in literature_keywords if keyword in text_lower)
    
    max_count = max(science_count, history_count, literature_count)
    
    if max_count >= 2:  # At least 2 subject-specific keywords
        if science_count == max_count:
            return "science"
        elif history_count == max_count:
            return "history"
        elif literature_count == max_count:
            return "literature"
    
    return "general"
