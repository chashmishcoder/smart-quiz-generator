import React from 'react';

const TextInput = ({ 
  inputText, 
  setInputText, 
  numQuestions, 
  setNumQuestions, 
  difficulty, 
  setDifficulty, 
  onGenerate, 
  loading, 
  backendConnected 
}) => {
  const handleGenerate = () => {
    if (inputText.length < 100) {
      alert('Please enter at least 100 characters of text');
      return;
    }
    onGenerate();
  };

  return (
    <div className="text-input-container">
      <h2>Input Text</h2>
      
      <div className="form-group">
        <label htmlFor="inputText">Educational Content:</label>
        <textarea
          id="inputText"
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          placeholder="Paste your educational content here (minimum 100 characters)..."
          className="text-area"
          rows={8}
          disabled={loading}
        />
        <div className="character-count">
          Characters: {inputText.length} / 100 minimum
        </div>
      </div>

      <div className="settings-row">
        <div className="form-group">
          <label htmlFor="numQuestions">Number of Questions:</label>
          <select
            id="numQuestions"
            value={numQuestions}
            onChange={(e) => setNumQuestions(parseInt(e.target.value))}
            disabled={loading}
          >
            <option value={3}>3 Questions</option>
            <option value={5}>5 Questions</option>
            <option value={10}>10 Questions</option>
            <option value={15}>15 Questions</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="difficulty">Difficulty:</label>
          <select
            id="difficulty"
            value={difficulty}
            onChange={(e) => setDifficulty(e.target.value)}
            disabled={loading}
          >
            <option value="Easy">Easy</option>
            <option value="Medium">Medium</option>
            <option value="Hard">Hard</option>
            <option value="Mixed">Mixed</option>
          </select>
        </div>
      </div>

      <button
        onClick={handleGenerate}
        disabled={loading || !backendConnected || inputText.length < 100}
        className={`generate-button ${!backendConnected ? 'disabled' : ''}`}
      >
        {loading ? 'Generating Questions...' : 'Generate Questions'}
      </button>

      {!backendConnected && (
        <div className="error-message">
          Backend not connected. Please ensure the backend server is running on port 8000.
        </div>
      )}
    </div>
  );
};

export default TextInput;
