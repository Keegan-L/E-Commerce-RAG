import React from 'react';
import { 
  Box, 
  Paper, 
  Typography, 
  List, 
  ListItem, 
  ListItemText,
  Divider
} from '@mui/material';
import ProductCard from './ProductCard';

const ChatMessage = ({ message, onAddToCart }) => {
  const isAssistant = message.role === 'assistant';

  // Function to format the message content with bullet points and sections
  const formatMessage = (content) => {
    // Split the content into sections based on common patterns
    const sections = content.split('\n\n');
    
    return sections.map((section, index) => {
      if (section.startsWith('- ')) {
        const items = section.split('\n').map(item => item.replace('- ', ''));
        return (
          <List key={index} dense sx={{ pl: 2 }}>
            {items.map((item, i) => (
              <ListItem key={i} sx={{ py: 0.5 }}>
                <ListItemText primary={item} />
              </ListItem>
            ))}
          </List>
        );
      }
      
      return (
        <Typography 
          key={index} 
          variant="body1" 
          sx={{ mb: 1 }}
        >
          {section}
        </Typography>
      );
    });
  };

  return (
    <Box 
      sx={{ 
        display: 'flex', 
        justifyContent: isAssistant ? 'flex-start' : 'flex-end',
        mb: 2
      }}
    >
      <Paper
        elevation={1}
        sx={{
          p: 2,
          maxWidth: '80%',
          backgroundColor: isAssistant ? '#e3f2fd' : '#f5f5f5',
          borderRadius: isAssistant ? '16px 16px 16px 0' : '16px 16px 0 16px',
        }}
      >
        {formatMessage(message.content)}
        {message.partInfo && (
          <Box sx={{ mt: 2 }}>
            <Divider sx={{ my: 1 }} />
            <ProductCard 
              partInfo={message.partInfo}
              onAddToCart={onAddToCart}
            />
          </Box>
        )}
      </Paper>
    </Box>
  );
};

export default ChatMessage;