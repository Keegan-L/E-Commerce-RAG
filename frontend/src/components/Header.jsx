import React from 'react';
import { AppBar, Toolbar, Typography, Box } from '@mui/material';
import { styled } from '@mui/material/styles';

const StyledAppBar = styled(AppBar)(({ theme }) => ({
  backgroundColor: theme.palette.background.paper,
  boxShadow: 'none',
  borderBottom: `1px solid ${theme.palette.divider}`,
}));

const Logo = styled('img')({
  height: '40px',
  marginRight: '16px',
});

const Header = () => {
  return (
    <StyledAppBar position="static">
      <Toolbar>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <Logo src="/PartSelect Logo.png" alt="PartSelect Logo" />
          <Typography variant="h6" color="text.primary">
            RAG Assistant
          </Typography>
        </Box>
      </Toolbar>
    </StyledAppBar>
  );
};

export default Header;