import axios from 'axios';

const API_URL = 'http://localhost:5000/api';

/**
 * Send a message to the chat API
 * @param {string} query - The user's message
 * @param {Array} chatHistory - Previous messages in the conversation
 * @returns {Promise} - Promise resolving to the API response
 */
export const sendMessage = async (query, chatHistory) => {
  try {
    const response = await axios.post(`${API_URL}/chat`, {
      query,
      chat_history: chatHistory
    });
    return response.data;
  } catch (error) {
    console.error('Error in API call:', error);
    throw error;
  }
};

/**
 * Search for product information
 * @param {string} query - The search query
 * @returns {Promise} - Promise resolving to search results
 */
export const searchProducts = async (query) => {
  try {
    const response = await axios.post(`${API_URL}/search`, {
      query
    });
    return response.data.results;
  } catch (error) {
    console.error('Error in search API call:', error);
    throw error;
  }
};