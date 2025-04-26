import React from 'react';
import { 
  Box, 
  Paper, 
  Typography, 
  Button, 
  Chip 
} from '@mui/material';
import ShoppingCartIcon from '@mui/icons-material/ShoppingCart';
import OpenInNewIcon from '@mui/icons-material/OpenInNew';

const ProductCard = ({ partInfo, onAddToCart }) => {
  if (!partInfo) return null;

  // Debug logging
  console.log('ProductCard partInfo:', partInfo);
  console.log('Part Details Keys:', Object.keys(partInfo.part_details || {}));

  return (
    <Paper 
      elevation={2} 
      sx={{ 
        p: 2, 
        backgroundColor: '#f8f9fa',
        borderRadius: '8px'
      }}
    >
      <Box sx={{ mb: 2 }}>
        <Typography variant="h6" sx={{ mb: 1 }}>
          {partInfo.part_name}
        </Typography>
        <Chip 
          label={partInfo.appliance_type} 
          size="small" 
          sx={{ mb: 1 }}
        />
        <Typography variant="body2" color="text.secondary">
          Part #: {partInfo.part_id}
        </Typography>
        {partInfo.part_details?.price && (
          <Typography variant="h6" color="primary" sx={{ mt: 1 }}>
            {partInfo.part_details.price}
          </Typography>
        )}
      </Box>

      <Box sx={{ display: 'flex', gap: 1 }}>
        <Button
          id={`view-details-${partInfo.part_id}`}
          variant="outlined"
          size="small"
          startIcon={<OpenInNewIcon />}
          href={partInfo.part_details?.product_url}
          target="_blank"
          rel="noopener noreferrer"
          onClick={(e) => {
            if (!partInfo.part_details?.product_url) {
              e.preventDefault();
            }
          }}
        >
          View Details
        </Button>
        <Button
          id={`add-to-cart-${partInfo.part_id}`}
          variant="contained"
          size="small"
          startIcon={<ShoppingCartIcon />}
          onClick={() => onAddToCart(partInfo)}
        >
          Add to Cart
        </Button>
      </Box>
    </Paper>
  );
};

export default ProductCard;