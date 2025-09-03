import React, { useState, useEffect, useCallback } from 'react';
import './App.css';
import TextInput from './components/TextInput';
import QuestionDisplay from './components/QuestionDisplay';
import ExportPanel from './components/ExportPanel';
import { checkHealth, generateQuestions } from './services/api';

function App() {
  const [inputText, setInputText] = useState('');
  const [questions, setQuestions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [backendStatus, setBackendStatus] = useState({ connected: false, modelLoaded: false });
  const [numQuestions, setNumQuestions] = useState(5);
  const [difficulty, setDifficulty] = useState('Medium');
  const [retryAttempts, setRetryAttempts] = useState(0);
  const [lastSaveTime, setLastSaveTime] = useState(null);

  // Auto-save to localStorage
  const saveToLocalStorage = useCallback(() => {
    const dataToSave = {
      inputText,
      questions,
      numQuestions,
      difficulty,
      timestamp: new Date().toISOString()
    };
    localStorage.setItem('smart-quiz-generator-data', JSON.stringify(dataToSave));
    setLastSaveTime(new Date());
  }, [inputText, questions, numQuestions, difficulty]);

  // Load from localStorage on mount
  useEffect(() => {
    const savedData = localStorage.getItem('smart-quiz-generator-data');
    if (savedData) {
      try {
        const parsed = JSON.parse(savedData);
        setInputText(parsed.inputText || '');
        setQuestions(parsed.questions || []);
        setNumQuestions(parsed.numQuestions || 5);
        setDifficulty(parsed.difficulty || 'Medium');
        console.log('📂 Restored data from localStorage');
      } catch (error) {
        console.error('Error loading saved data:', error);
      }
    }
  }, []);

  // Auto-save whenever data changes
  useEffect(() => {
    if (inputText || questions.length > 0) {
      const timeoutId = setTimeout(() => {
        saveToLocalStorage();
      }, 2000); // Save after 2 seconds of inactivity

      return () => clearTimeout(timeoutId);
    }
  }, [inputText, questions, numQuestions, difficulty, saveToLocalStorage]);

  // Connection retry with exponential backoff
  const checkBackendHealth = useCallback(async (attempt = 0) => {
    try {
      const health = await checkHealth();
      setBackendStatus({
        connected: health.status === 'running',
        modelLoaded: health.model_loaded
      });
      setRetryAttempts(0); // Reset on success
      return true;
    } catch (error) {
      console.log(`Backend connection attempt ${attempt + 1} failed:`, error.message);
      setBackendStatus({ connected: false, modelLoaded: false });
      
      // Exponential backoff retry
      if (attempt < 5) {
        const delay = Math.min(1000 * Math.pow(2, attempt), 30000); // Max 30 seconds
        setTimeout(() => {
          setRetryAttempts(attempt + 1);
          checkBackendHealth(attempt + 1);
        }, delay);
      }
      return false;
    }
  }, []);

  // Check backend health on mount and periodically
  useEffect(() => {
    // Check immediately
    checkBackendHealth();

    // Check every 30 seconds
    const interval = setInterval(() => checkBackendHealth(), 30000);

    return () => clearInterval(interval);
  }, [checkBackendHealth]);

  const handleGenerateQuestions = async () => {
    if (!inputText || inputText.length < 100) {
      alert('Please enter at least 100 characters of text');
      return;
    }

    if (!backendStatus.connected) {
      alert('Backend is not connected. Attempting to reconnect...');
      const connected = await checkBackendHealth();
      if (!connected) {
        alert('Could not connect to backend. Please ensure the server is running.');
        return;
      }
    }

    setLoading(true);
    try {
      const settings = {
        numQuestions: numQuestions,
        difficulty: difficulty
      };

      const response = await generateQuestions(inputText, settings);
      
      if (response && response.questions) {
        setQuestions(response.questions);
        console.log(`✅ Generated ${response.questions.length} questions`);
      } else {
        alert('No questions were generated. Please try with different text.');
      }
    } catch (error) {
      console.error('Error generating questions:', error);
      
      // Try to reconnect on error
      const connected = await checkBackendHealth();
      if (connected) {
        alert('Connection restored. Please try generating questions again.');
      } else {
        alert('Failed to generate questions. Backend connection lost.');
      }
    } finally {
      setLoading(false);
    }
  };

  // Clear localStorage on successful export
  const handleSuccessfulExport = () => {
    localStorage.removeItem('smart-quiz-generator-data');
    console.log('🗑️ Cleared localStorage after successful export');
  };

  return (
    <div className="App">
      <div className="app-header">
        <h1 className="app-title">Smart Quiz Generator</h1>
        <p className="app-subtitle">AI-powered question generation from educational content</p>
      </div>

      <div className={`backend-status ${backendStatus.connected ? 'connected' : 'disconnected'}`}>
        <div className={`status-indicator ${backendStatus.connected ? 'connected' : 'disconnected'}`}></div>
        {backendStatus.connected ? (
          <span>
            Backend Connected {backendStatus.modelLoaded ? '• AI Model Loaded' : '• AI Model Loading...'}
            {lastSaveTime && <span className="save-indicator"> • Auto-saved {lastSaveTime.toLocaleTimeString()}</span>}
          </span>
        ) : (
          <span>
            Backend Disconnected 
            {retryAttempts > 0 && <span> • Retrying... (attempt {retryAttempts}/5)</span>}
          </span>
        )}
      </div>

      <TextInput
        inputText={inputText}
        setInputText={setInputText}
        numQuestions={numQuestions}
        setNumQuestions={setNumQuestions}
        difficulty={difficulty}
        setDifficulty={setDifficulty}
        onGenerate={handleGenerateQuestions}
        loading={loading}
        backendConnected={backendStatus.connected}
      />

      <QuestionDisplay 
        questions={questions} 
        setQuestions={setQuestions}
      />

      <ExportPanel 
        questions={questions} 
        onSuccessfulExport={handleSuccessfulExport}
      />
    </div>
  );
}

export default App;
