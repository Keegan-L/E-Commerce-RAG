const API_BASE_URL = 'http://localhost:5001/api';

export const sendMessage = async (message, chatHistory) => {
  try {
    const response = await fetch(`${API_BASE_URL}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify({
        query: message,
        chat_history: chatHistory
      }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    if (error.message.includes('Failed to fetch')) {
      throw new Error('Could not connect to the server. Please make sure the backend is running on http://localhost:5000');
    }
    console.error('Error in sendMessage:', error);
    throw error;
  }
};

export const searchParts = async (query) => {
  try {
    const response = await fetch(`${API_BASE_URL}/search`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ query }),
    });

    if (!response.ok) {
      throw new Error('Failed to search parts');
    }

    return await response.json();
  } catch (error) {
    console.error('Error in searchParts:', error);
    throw error;
  }
};

export const getPartDetails = async (partId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/part/${partId}`, {
      method: 'GET',
    });

    if (!response.ok) {
      throw new Error('Failed to get part details');
    }

    return await response.json();
  } catch (error) {
    console.error('Error in getPartDetails:', error);
    throw error;
  }
}; 