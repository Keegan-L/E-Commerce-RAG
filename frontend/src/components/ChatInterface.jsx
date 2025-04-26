import React, { useState, useEffect, useRef } from 'react';
import { 
  Box, 
  Paper, 
  TextField, 
  Button, 
  Typography, 
  CircularProgress,
  Chip,
  Divider
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import ChatMessage from './ChatMessage';
import ProductCard from './ProductCard';
import Cart from './Cart';
import { sendMessage } from '../services/api';

const ChatInterface = () => {
  const [messages, setMessages] = useState([
    { 
      role: 'assistant', 
      content: 'Hello! I\'m the PartSelect assistant. How can I help you with refrigerator or dishwasher parts today?',
      suggestions: [
        "My dishwasher door won't close properly",
        "My refrigerator is making strange noises",
        "I need help finding a replacement part"
      ]
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [cartItems, setCartItems] = useState([]);
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom when messages update
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSend = async (message = input) => {
    if (message.trim() === '') return;
    
    // Add user message
    const userMessage = { role: 'user', content: message };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);
    
    try {
      // Send to backend
      const chatHistory = messages.filter(msg => msg.role === 'user' || msg.role === 'assistant');
      const response = await sendMessage(message, chatHistory);
      
      // Add assistant response
      setMessages(prev => [
        ...prev, 
        { 
          role: 'assistant', 
          content: response.response,
          partInfo: response.part_info,
          suggestions: [
            "How do I install this part?",
            "What tools will I need?",
            "Is this part compatible with my model?"
          ]
        }
      ]);
    } catch (error) {
      console.error('Error sending message:', error);
      setMessages(prev => [
        ...prev, 
        { 
          role: 'assistant', 
          content: `Sorry, I encountered an error: ${error.message}. Please try again later.`
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleSuggestionClick = (suggestion) => {
    handleSend(suggestion);
  };

  const handleAddToCart = (partInfo) => {
    setCartItems(prev => [...prev, partInfo]);
  };

  const handleRemoveFromCart = (index) => {
    setCartItems(prev => prev.filter((_, i) => i !== index));
  };

  return (
    <Box sx={{ display: 'flex', gap: 2, height: '80vh' }}>
      {/* Chat Interface */}
      <Paper 
        elevation={3} 
        sx={{ 
          display: 'flex', 
          flexDirection: 'column', 
          flex: 1,
          borderRadius: '12px',
          overflow: 'hidden'
        }}
      >
        {/* Header */}
        <Box sx={{ p: 2, backgroundColor: '#2c3e50', color: 'white' }}>
          <Typography variant="h6">PartSelect Assistant</Typography>
          <Typography variant="body2">
            Ask me about refrigerator and dishwasher parts
          </Typography>
        </Box>
        
        {/* Messages Area */}
        <Box 
          sx={{ 
            flex: 1, 
            p: 2, 
            overflowY: 'auto',
            backgroundColor: '#f5f5f5'
          }}
        >
          {messages.map((message, index) => (
            <Box key={index} sx={{ mb: 2 }}>
              <ChatMessage 
                message={message} 
                onAddToCart={handleAddToCart}
              />
              {message.suggestions && (
                <Box sx={{ mt: 1, display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                  {message.suggestions.map((suggestion, idx) => (
                    <Chip
                      key={idx}
                      label={suggestion}
                      onClick={() => handleSuggestionClick(suggestion)}
                      sx={{ 
                        backgroundColor: '#e3f2fd',
                        '&:hover': {
                          backgroundColor: '#bbdefb',
                        }
                      }}
                    />
                  ))}
                </Box>
              )}
              {index < messages.length - 1 && <Divider sx={{ my: 1 }} />}
            </Box>
          ))}
          {loading && (
            <Box sx={{ display: 'flex', justifyContent: 'center', my: 2 }}>
              <CircularProgress size={24} />
            </Box>
          )}
          <div ref={messagesEndRef} />
        </Box>
        
        {/* Input Area */}
        <Box 
          sx={{ 
            p: 2,
            backgroundColor: 'white',
            borderTop: '1px solid #e0e0e0',
            display: 'flex'
          }}
        >
          <TextField
            fullWidth
            variant="outlined"
            placeholder="Type your message..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            size="small"
            sx={{ mr: 1 }}
            multiline
            maxRows={3}
          />
          <Button 
            variant="contained" 
            color="primary" 
            endIcon={<SendIcon />}
            onClick={() => handleSend()}
            disabled={loading}
          >
            Send
          </Button>
        </Box>
      </Paper>

      {/* Shopping Cart */}
      <Cart 
        items={cartItems}
        onRemoveItem={handleRemoveFromCart}
      />
    </Box>
  );
};

export default ChatInterface;
