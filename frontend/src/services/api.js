const BASE_URL = 'http://localhost:8000';

export const checkHealth = async () => {
  try {
    const response = await fetch(`${BASE_URL}/api/health`);
    if (!response.ok) {
      throw new Error('Backend not responding');
    }
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Health check failed:', error);
    return { status: 'error', model_loaded: false };
  }
};

export const generateQuestions = async (text, settings) => {
  try {
    const requestBody = {
      text: text,
      num_questions: settings.numQuestions,
      question_type: 'multiple_choice',
      difficulty: settings.difficulty.toLowerCase()
    };

    const response = await fetch(`${BASE_URL}/api/generate-questions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestBody)
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to generate questions');
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Question generation failed:', error);
    alert(`Error generating questions: ${error.message}`);
    throw error;
  }
};

export const exportQuestions = async (format, questionCount = 15) => {
  try {
    const response = await fetch(`${BASE_URL}/api/export/${format.toLowerCase()}?limit=${questionCount}`);
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Export failed');
    }

    // Get filename from Content-Disposition header
    const contentDisposition = response.headers.get('Content-Disposition');
    let filename = `quiz_export.${format}`;
    if (contentDisposition) {
      const filenameMatch = contentDisposition.match(/filename="?([^"]+)"?/);
      if (filenameMatch) {
        filename = filenameMatch[1];
      }
    }

    // Get the blob data
    const blob = await response.blob();
    
    // Create download link
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
    
    return { success: true, filename };
  } catch (error) {
    console.error('Export failed:', error);
    throw error;
  }
};

export const validateQuestions = async (questions) => {
  try {
    const response = await fetch(`${BASE_URL}/api/validate-questions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ questions })
    });

    if (!response.ok) {
      throw new Error('Validation failed');
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Validation failed:', error);
    return null;
  }
};
