import React, { useState } from 'react';
import { exportQuestions } from '../services/api';

const ExportPanel = ({ questions, onSuccessfulExport }) => {
  const [exporting, setExporting] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleExport = async (format) => {
    if (!questions || questions.length === 0) {
      setError('No questions to export');
      return;
    }

    setExporting(true);
    setError('');
    setSuccess('');
    
    try {
      await exportQuestions(format, questions.length);
      setSuccess(`Successfully exported ${questions.length} questions as ${format.toUpperCase()}! Check your downloads folder.`);
      
      // Call the callback to clear localStorage
      if (onSuccessfulExport) {
        onSuccessfulExport();
      }
      
      // Clear success message after 5 seconds
      setTimeout(() => setSuccess(''), 5000);
    } catch (error) {
      console.error('Export failed:', error);
      setError(`Export failed: ${error.message}`);
      
      // Clear error message after 5 seconds
      setTimeout(() => setError(''), 5000);
    } finally {
      setExporting(false);
    }
  };

  const handleCopyToClipboard = () => {
    if (!questions || questions.length === 0) {
      setError('No questions to copy');
      return;
    }

    const questionsText = questions.map((q, index) => {
      return `Question ${index + 1}: ${q.question}\n` +
             `Options:\n${q.options.map((opt, i) => `${String.fromCharCode(65 + i)}. ${opt}`).join('\n')}\n` +
             `Correct Answer: ${q.correct_answer}\n` +
             `Explanation: ${q.explanation}\n\n`;
    }).join('');

    navigator.clipboard.writeText(questionsText).then(() => {
      setSuccess('Questions copied to clipboard!');
    }).catch(err => {
      console.error('Failed to copy to clipboard:', err);
      setError('Failed to copy to clipboard');
    });
  };

  if (!questions || questions.length === 0) {
    return null;
  }

  return (
    <div className="export-container">
      <h2>Export Questions</h2>
      
      {error && <div className="error-message">{error}</div>}
      {success && <div className="success-message">{success}</div>}
      
      <div className="export-buttons">
        <button
          onClick={() => handleExport('json')}
          disabled={exporting}
          className="export-button json-button"
        >
          {exporting ? 'Exporting...' : 'Export JSON'}
        </button>

        <button
          onClick={() => handleExport('csv')}
          disabled={exporting}
          className="export-button csv-button"
        >
          {exporting ? 'Exporting...' : 'Export CSV'}
        </button>

        <button
          onClick={() => handleExport('moodle')}
          disabled={exporting}
          className="export-button moodle-button"
        >
          {exporting ? 'Exporting...' : 'Export Moodle XML'}
        </button>

        <button
          onClick={() => handleExport('gift')}
          disabled={exporting}
          className="export-button gift-button"
        >
          {exporting ? 'Exporting...' : 'Export GIFT'}
        </button>

        <button
          onClick={handleCopyToClipboard}
          className="export-button copy-button"
        >
          Copy to Clipboard
        </button>
      </div>

      <div className="export-info">
        <p>Total questions: {questions.length}</p>
        <p>Export formats: JSON (data), CSV (spreadsheet), Moodle XML (LMS), GIFT (Moodle text)</p>
      </div>
    </div>
  );
};

export default ExportPanel;
