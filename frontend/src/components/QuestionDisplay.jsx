import React, { useState } from 'react';

const QuestionDisplay = ({ questions, setQuestions }) => {
  const [editingQuestion, setEditingQuestion] = useState(null);
  const [editText, setEditText] = useState('');
  const [revealedAnswers, setRevealedAnswers] = useState({});

  const handleEdit = (index) => {
    setEditingQuestion(index);
    setEditText(questions[index].question);
  };

  const handleSaveEdit = (index) => {
    const updatedQuestions = [...questions];
    updatedQuestions[index].question = editText;
    setQuestions(updatedQuestions);
    setEditingQuestion(null);
    setEditText('');
  };

  const handleCancelEdit = () => {
    setEditingQuestion(null);
    setEditText('');
  };

  const handleDelete = (index) => {
    if (window.confirm('Are you sure you want to delete this question?')) {
      const updatedQuestions = questions.filter((_, i) => i !== index);
      setQuestions(updatedQuestions);
    }
  };

  const handleRevealAnswer = (index) => {
    setRevealedAnswers(prev => ({
      ...prev,
      [index]: !prev[index]
    }));
  };

  if (!questions || questions.length === 0) {
    return null;
  }

  return (
    <div className="questions-container">
      <h2>Generated Questions ({questions.length})</h2>
      
      {questions.map((question, index) => (
        <div key={index} className="question-card">
          <div className="question-header">
            <span className="question-number">Question {index + 1}</span>
            <div className="question-actions">
              <button
                onClick={() => handleEdit(index)}
                className="edit-button"
                disabled={editingQuestion === index}
              >
                Edit
              </button>
              <button
                onClick={() => handleDelete(index)}
                className="delete-button"
              >
                Delete
              </button>
            </div>
          </div>

          <div className="question-content">
            {editingQuestion === index ? (
              <div className="edit-form">
                <textarea
                  value={editText}
                  onChange={(e) => setEditText(e.target.value)}
                  className="edit-textarea"
                  rows={3}
                />
                <div className="edit-actions">
                  <button onClick={() => handleSaveEdit(index)} className="save-button">
                    Save
                  </button>
                  <button onClick={handleCancelEdit} className="cancel-button">
                    Cancel
                  </button>
                </div>
              </div>
            ) : (
              <p className="question-text">{question.question}</p>
            )}

            <div className="options-container">
              {question.options && question.options.map((option, optionIndex) => (
                <div key={optionIndex} className="option-item">
                  <input
                    type="radio"
                    id={`q${index}_option${optionIndex}`}
                    name={`question_${index}`}
                    value={option}
                    disabled
                  />
                  <label htmlFor={`q${index}_option${optionIndex}`} className="option-label">
                    {String.fromCharCode(65 + optionIndex)}. {option}
                  </label>
                </div>
              ))}
            </div>

            <div className="answer-section">
              <button
                onClick={() => handleRevealAnswer(index)}
                className="reveal-button"
              >
                {revealedAnswers[index] ? 'Hide Answer' : 'Reveal Answer'}
              </button>

              {revealedAnswers[index] && (
                <div className="answer-reveal">
                  <div className="correct-answer">
                    <strong>Correct Answer:</strong> {question.correct_answer}
                  </div>
                  {question.explanation && (
                    <div className="explanation">
                      <strong>Explanation:</strong> {question.explanation}
                    </div>
                  )}
                  <div className="metadata">
                    <span className="difficulty">Difficulty: {question.difficulty}</span>
                    {question.bloom_level && (
                      <span className="bloom-level">Level: {question.bloom_level}</span>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default QuestionDisplay;
