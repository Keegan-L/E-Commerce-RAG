# PartSelect Chat Agent

A specialized chat agent for the PartSelect e-commerce website, focusing on refrigerator and dishwasher parts information and customer support.

## Overview

This application uses Retrieval-Augmented Generation (RAG) to provide accurate and contextual responses about refrigerator and dishwasher parts. The system integrates with the DeepSeek language model to generate human-like responses while maintaining focus on the specific product domain.

## Features

- **Specialized Knowledge Base**: Pre-populated with QA pairs about refrigerator and dishwasher parts
- **Vector Search**: Uses FAISS for efficient similarity search of relevant information
- **Product Information Display**: Shows relevant part details with the option to add to cart
- **Context-Aware Responses**: Maintains conversation history for coherent interactions
- **Focused Domain Expertise**: Strictly stays within the appliance parts domain

## Architecture

### Frontend

- Built with React.js and Material-UI for a clean, modern interface
- Responsive design that works across desktop and mobile devices
- Interactive chat interface with product cards for part information

### Backend

- Flask API server with CORS support
- FAISS vector database for efficient similarity search
- Integration with DeepSeek API for embeddings and chat completions
- JSON-based knowledge base for refrigerator and dishwasher parts

## Setup and Installation

### Prerequisites

- Python 3.8+
- Node.js 14+
- DeepSeek API key

### Backend Setup

1. Clone the repository
2. Install Python dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the root directory with your DeepSeek API key:
   ```
   DEEPSEEK_API_KEY=your_api_key_here
   ```
4. Ensure you have `dishwasher_qa_pairs.json` and `refrigerator_qa_pairs.json` in the backend directory
5. Start the backend server:
   ```
   python app.py
   ```

### Frontend Setup

1. Navigate to the frontend directory
2. Install dependencies:
   ```
   npm install
   ```
3. Start the development server:
   ```
   npm start
   ```

## Data Structure

The QA pairs are stored in JSON files with the following structure:

```json
{
  "part_id_1": {
    "part_info": {
      "name": "Part Name",
      "description": "Detailed description",
      "price": 49.99,
      "image_url": "https://example.com/part-image.jpg",
      "...": "other part details"
    },
    "qa_pairs": [
      {
        "question": "How do I install this part?",
        "answer": "Detailed installation instructions..."
      },
      {
        "question": "Is this compatible with model XYZ?",
        "answer": "Compatibility information..."
      }
    ]
  }
}
```

## API Endpoints

- **POST /api/chat**: Send a message to the chat agent
  - Request body: `{ "query": "user question", "chat_history": [] }`
  - Response: `{ "response": "agent response", "part_info": {}, "search_results": [] }`

- **POST /api/search**: Search for part information
  - Request body: `{ "query": "search term" }`
  - Response: `{ "results": [] }`

- **GET /api/part/{part_id}**: Get detailed information about a specific part
  - Response: `{ "part_id": "id", "part_info": {}, "appliance_type": "type" }`
