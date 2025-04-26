# PartSelect Assistant RAG

A RAG (Retrieval-Augmented Generation) system for appliance parts information and customer support, built with React and Flask.

## Overview

This project implements a RAG system that helps customers find information about appliance parts, get installation instructions, and troubleshoot issues. The system combines:

- A React frontend for user interaction
- A Flask backend for processing queries and generating responses
- A RAG system that retrieves relevant information from a knowledge base
- Integration with DeepSeek's API for generating responses

## Features

- **Natural Language Queries**: Users can ask questions about appliance parts in natural language
- **Contextual Responses**: The system provides relevant, contextual answers based on the knowledge base
- **Product Suggestions**: Intelligent product recommendations when appropriate
- **Installation Guidance**: Clear, step-by-step installation instructions
- **Troubleshooting Help**: Assistance with common appliance issues

## Project Structure

```
.
├── backend/
│   ├── app.py                    # Flask application and RAG system
│   ├── dishwasher_qa_pairs.json  # Knowledge base for dishwasher parts
│   ├── refridgerator_qa_pairs.json  # Knowledge base for refrigerator parts
│   ├── dishwasher_data.json      # Raw dishwasher part data
│   ├── refridgerator_data.json   # Raw refrigerator part data
│   ├── QA_pair_generator.py      # Script to generate QA pairs
│   ├── saved_embeddings.npy      # Pre-computed embeddings
│   └── saved_embeddings.npy.questions  # Questions corresponding to embeddings
├── frontend/
│   ├── public/                   # Static files
│   ├── src/                      # React source code
│   │   ├── components/           # React components
│   │   │   ├── ChatInterface.jsx # Main chat interface
│   │   │   ├── ProductCard.jsx   # Product display component
│   │   │   └── Cart.jsx          # Shopping cart component
│   │   ├── App.jsx               # Main application component
│   │   └── index.jsx             # Entry point
│   ├── package.json              # Node.js dependencies
│   └── package-lock.json         # Locked dependency versions
└── README.md                     # This file
```

## Setup

### Prerequisites

- Python 3.8+
- Node.js 14+
- npm or yarn
- DeepSeek API key
- OpenAI API key

### Environment Setup

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file and add your API keys:
   ```
   DEEPSEEK_API_KEY=your_deepseek_api_key
   OPENAI_API_KEY=your_openai_api_key
   ```

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install required Python packages:
   ```bash
   pip install flask flask-cors python-dotenv numpy faiss-cpu requests openai
   ```

4. Generate embeddings (if not already present):
   ```bash
   python QA_pair_generator.py
   ```

5. Start the Flask server:
   ```bash
   python app.py
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm start
   ```

## Usage

1. Open your browser and navigate to `http://localhost:3000`
2. Type your question about appliance parts in the chat interface
3. The system will provide relevant information, installation instructions, or product suggestions

## API Documentation

### Chat Endpoint
- **URL**: `/api/chat`
- **Method**: `POST`
- **Request Body**:
  ```json
  {
    "query": "How do I replace my dishwasher pump?"
  }
  ```
- **Response**:
  ```json
  {
    "response": "To replace your dishwasher pump...",
    "products": [
      {
        "id": "123",
        "name": "Dishwasher Pump",
        "price": 49.99
      }
    ]
  }
  ```

### Search Endpoint
- **URL**: `/api/search`
- **Method**: `POST`
- **Request Body**:
  ```json
  {
    "query": "dishwasher pump"
  }
  ```
- **Response**: List of relevant parts and information

### Part Information Endpoint
- **URL**: `/api/part/<part_id>`
- **Method**: `GET`
- **Response**: Detailed information about a specific part

## Data Generation

The QA pairs in the knowledge base were generated using the `QA_pair_generator.py` script, which:
1. Takes raw part data from JSON files
2. Generates relevant questions and answers
3. Creates embeddings for efficient retrieval
4. Saves the embeddings for future use

## Development

### Running Tests
```bash
# Backend tests
cd backend
python -m pytest

# Frontend tests
cd frontend
npm test
```

### Code Style
- Backend: Follow PEP 8 guidelines
- Frontend: Use ESLint with React rules

### Contributing
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## Troubleshooting

### Common Issues

1. **API Key Errors**
   - Ensure your `.env` file is properly set up
   - Check that the API keys are correct
   - Verify API rate limits

2. **Embedding Generation**
   - If embeddings are missing, run `QA_pair_generator.py`
   - Ensure you have sufficient disk space
   - Check OpenAI API access

3. **Frontend Connection Issues**
   - Verify backend server is running
   - Check CORS settings
   - Ensure correct port configuration

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [React](https://reactjs.org/)
- [Flask](https://flask.palletsprojects.com/)
- [DeepSeek](https://deepseek.com/)
- [OpenAI](https://openai.com/)
- [FAISS](https://github.com/facebookresearch/faiss)

