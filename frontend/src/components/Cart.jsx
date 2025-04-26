import React, { useState } from 'react';
import { 
  Box, 
  Paper, 
  Typography, 
  List, 
  ListItem, 
  ListItemText, 
  IconButton,
  Divider,
  TextField,
  Stack
} from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';

const Cart = ({ items, onRemoveItem }) => {
  const [taxRate, setTaxRate] = useState(0);

  const calculateSubtotal = () => {
    return items.reduce((total, item) => {
      const price = parseFloat(item.part_details?.price?.replace('$', '') || 0);
      return total + price;
    }, 0);
  };

  const calculateTax = () => {
    return calculateSubtotal() * (taxRate / 100);
  };

  const calculateTotal = () => {
    return calculateSubtotal() + calculateTax();
  };

  return (
    <Paper 
      elevation={3} 
      sx={{ 
        width: '300px',
        height: '100%',
        p: 2,
        backgroundColor: 'white',
        borderRadius: '12px'
      }}
    >
      <Typography variant="h6" sx={{ mb: 2 }}>
        Shopping Cart ({items.length})
      </Typography>
      
      {items.length === 0 ? (
        <Typography variant="body2" color="text.secondary">
          Your cart is empty
        </Typography>
      ) : (
        <>
          <List>
            {items.map((item, index) => (
              <React.Fragment key={index}>
                <ListItem
                  secondaryAction={
                    <IconButton 
                      edge="end" 
                      aria-label="delete"
                      onClick={() => onRemoveItem(index)}
                    >
                      <DeleteIcon />
                    </IconButton>
                  }
                >
                  <ListItemText
                    primary={item.part_name}
                    secondary={
                      <React.Fragment>
                        <Typography
                          component="span"
                          variant="body2"
                          color="text.primary"
                        >
                          Part #: {item.part_id}
                        </Typography>
                        <br />
                        <Typography
                          component="span"
                          variant="body2"
                          color="text.secondary"
                        >
                          {item.appliance_type}
                        </Typography>
                        <br />
                        <Typography
                          component="span"
                          variant="body2"
                          color="primary"
                          sx={{ fontWeight: 'bold' }}
                        >
                          {item.part_details?.price}
                        </Typography>
                      </React.Fragment>
                    }
                  />
                </ListItem>
                {index < items.length - 1 && <Divider />}
              </React.Fragment>
            ))}
          </List>

          <Divider sx={{ my: 2 }} />

          <Stack spacing={2}>
            <Box>
              <Typography variant="body2" color="text.secondary">
                Subtotal: ${calculateSubtotal().toFixed(2)}
              </Typography>
            </Box>

            <Box>
              <TextField
                label="Tax Rate (%)"
                type="number"
                size="small"
                value={taxRate}
                onChange={(e) => setTaxRate(parseFloat(e.target.value) || 0)}
                inputProps={{ min: 0, max: 100, step: 0.1 }}
                sx={{ width: '100%' }}
              />
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                Tax: ${calculateTax().toFixed(2)}
              </Typography>
            </Box>

            <Box>
              <Typography variant="h6" color="primary">
                Total: ${calculateTotal().toFixed(2)}
              </Typography>
            </Box>
          </Stack>
        </>
      )}
    </Paper>
  );
};

export default Cart; 