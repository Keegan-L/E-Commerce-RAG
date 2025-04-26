import json
import numpy as np
import faiss
import requests
import os
from pathlib import Path
from dotenv import load_dotenv
from typing import List, Dict, Any, Tuple, Optional
from flask import Flask, request, jsonify
from flask_cors import CORS
import openai

# Load environment variables
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

# Get API keys from environment variables
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Configure OpenAI
openai.api_key = OPENAI_API_KEY

# DeepSeek API endpoints
DEEPSEEK_EMBEDDING_URL = "https://api.deepseek.com/v1/embeddings"
DEEPSEEK_CHAT_URL = "https://api.deepseek.com/v1/chat/completions"

class PartSelectRAG:
    def __init__(self, 
                 dishwasher_qa_path: str = "dishwasher_qa_pairs.json",
                 refrigerator_qa_path: str = "refridgerator_qa_pairs.json",
                 index_dimension: int = 1536,
                 temperature: float = 0.7,
                 embeddings_file: str = "saved_embeddings.npy"):  # Added embeddings file path
        """
        Initialize the RAG system for PartSelect with QA pairs data and FAISS index.
        
        Args:
            dishwasher_qa_path: Path to the JSON file containing dishwasher QA pairs
            refrigerator_qa_path: Path to the JSON file containing refrigerator QA pairs
            index_dimension: Dimension of the embedding vectors (1536 for OpenAI's text-embedding-3-small)
            temperature: Temperature parameter for the DeepSeek model
            embeddings_file: Path to save/load embeddings
        """
        self.dishwasher_qa_path = dishwasher_qa_path
        self.refrigerator_qa_path = refrigerator_qa_path
        self.index_dimension = index_dimension
        self.deepseek_temperature = temperature
        self.embeddings_file = embeddings_file
        
        # Load data
        self.all_qa_data = {}
        self.load_qa_data()
        
        # Initialize FAISS index
        self.index = None
        self.questions = []
        self.metadata = []
        
        # Build index if data is available
        if self.all_qa_data:
            self.build_index()
    
    def load_qa_data(self):
        """Load QA pairs from JSON files."""
        try:
            if os.path.exists(self.dishwasher_qa_path):
                with open(self.dishwasher_qa_path, 'r') as f:
                    dishwasher_data = json.load(f)
                    for part_id, data in dishwasher_data.items():
                        # Add appliance type to metadata
                        data["appliance_type"] = "dishwasher"
                        self.all_qa_data[part_id] = data
                print(f"Loaded dishwasher QA pairs: {len(dishwasher_data)} parts")
            
            if os.path.exists(self.refrigerator_qa_path):
                with open(self.refrigerator_qa_path, 'r') as f:
                    refrigerator_data = json.load(f)
                    for part_id, data in refrigerator_data.items():
                        # Add appliance type to metadata
                        data["appliance_type"] = "refrigerator"
                        self.all_qa_data[part_id] = data
                print(f"Loaded refrigerator QA pairs: {len(refrigerator_data)} parts")
        except Exception as e:
            print(f"Error loading QA data: {e}")
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for the given text using OpenAI's embedding model.
        
        Args:
            text: The text to generate embedding for
            
        Returns:
            List of floats representing the embedding vector
        """
        try:
            client = openai.OpenAI(api_key=OPENAI_API_KEY)
            response = client.embeddings.create(
                input=text,
                model="text-embedding-3-small"
            )
            embedding = response.data[0].embedding
            client.close()  # Close the client
            return embedding
        except Exception as e:
            print(f"Error generating embedding: {str(e)}")
            return None
    
    def build_index(self):
        """Build FAISS index from QA pairs."""
        # Extract questions and answers
        all_questions = []
        all_metadata = []
        
        for part_id, data in self.all_qa_data.items():
            part_info = data["part_info"]
            appliance_type = data.get("appliance_type", "unknown")
            
            for qa_pair in data["qa_pairs"]:
                question = qa_pair["question"]
                answer = qa_pair["answer"]
                
                all_questions.append(question)
                all_metadata.append({
                    "question": question,
                    "answer": answer,
                    "part_id": part_id,
                    "part_name": part_info["name"],
                    "appliance_type": appliance_type,
                    "part_info": part_info
                })
        
        print(f"Generating embeddings for {len(all_questions)} questions...")
        
        # Try to load saved embeddings first
        embeddings = self.load_saved_embeddings(all_questions)
        
        if embeddings is None:
            # Generate embeddings if not saved
            embeddings = []
            for i, question in enumerate(all_questions):
                if i % 10 == 0:
                    print(f"Processing embedding {i+1}/{len(all_questions)}")
                
                embedding = self.generate_embedding(question)
                if embedding:
                    embeddings.append(embedding)
                else:
                    print(f"Skipping question {i} due to embedding failure")
                    continue
            
            # Save the embeddings
            self.save_embeddings(embeddings, all_questions)
        
        # Store the questions and metadata
        self.questions = [all_questions[i] for i in range(len(embeddings))]
        self.metadata = [all_metadata[i] for i in range(len(embeddings))]
        
        # Convert to numpy array
        embeddings_array = np.array(embeddings).astype('float32')
        
        # Initialize FAISS index - using L2 distance
        self.index = faiss.IndexFlatL2(self.index_dimension)
        
        # Add vectors to the index
        self.index.add(embeddings_array)
        
        print(f"FAISS index built with {self.index.ntotal} vectors")
    
    def save_embeddings(self, embeddings: List[List[float]], questions: List[str]):
        """Save embeddings and corresponding questions to file."""
        try:
            # Save embeddings
            with open(self.embeddings_file, 'wb') as f:
                np.save(f, np.array(embeddings))
            # Save questions
            with open(f"{self.embeddings_file}.questions", 'w') as f:
                json.dump(questions, f)
            print(f"Saved embeddings to {self.embeddings_file}")
        except Exception as e:
            print(f"Error saving embeddings: {e}")

    def load_saved_embeddings(self, questions: List[str]) -> Optional[List[List[float]]]:
        """Load saved embeddings if they exist and match the current questions."""
        try:
            if os.path.exists(self.embeddings_file) and os.path.exists(f"{self.embeddings_file}.questions"):
                # Load saved questions
                with open(f"{self.embeddings_file}.questions", 'r') as f:
                    saved_questions = json.load(f)
                
                # Check if questions match
                if saved_questions == questions:
                    # Load embeddings
                    with open(self.embeddings_file, 'rb') as f:
                        embeddings = np.load(f)
                    print(f"Loaded saved embeddings from {self.embeddings_file}")
                    return embeddings.tolist()
                else:
                    print("Saved embeddings don't match current questions, regenerating...")
            return None
        except Exception as e:
            print(f"Error loading saved embeddings: {e}")
            return None
    
    def search(self, query: str, k: int = 3) -> List[Dict]:
        """
        Search for similar questions in the index.
        
        Args:
            query: The user's query
            k: Number of results to return
            
        Returns:
            List of dictionaries containing question, answer, and part info
        """
        # Generate embedding for the query
        query_embedding = self.generate_embedding(query)
        if not query_embedding:
            return []
        
        # Convert to numpy array
        query_embedding = np.array([query_embedding]).astype('float32')
        
        # Search the index
        distances, indices = self.index.search(query_embedding, k)
        
        # Get the results
        results = []
        for i, idx in enumerate(indices[0]):
            if idx >= 0 and idx < len(self.metadata):
                result = self.metadata[idx].copy()
                result["distance"] = float(distances[0][i])
                results.append(result)
        
        return results
    
    def generate_response(self, query: str, chat_history: List[Dict] = None) -> Dict:
        """
        Generate a response to the user's query using RAG approach.
        
        Args:
            query: The user's query
            chat_history: List of previous messages in the chat
            
        Returns:
            Dictionary containing the response and relevant part information
        """
        # Initialize chat history if not provided
        if chat_history is None:
            chat_history = []
        
        # Search for relevant QA pairs
        search_results = self.search(query, k=3)
        
        # Construct context from search results
        context = ""
        part_info = None
        
        if search_results:
            for i, result in enumerate(search_results):
                context += f"Q: {result['question']}\nA: {result['answer']}\n\n"
                
                # Store part info from the most relevant result
                if i == 0:
                    part_info = {
                        "part_id": result["part_id"],
                        "part_name": result["part_name"],
                        "appliance_type": result["appliance_type"],
                        "part_details": result["part_info"]
                    }
        
        # Construct prompt for DeepSeek
        system_prompt = """
You are a helpful assistant for PartSelect, an e-commerce website specializing in appliance parts. 
Your role is to help customers find information about refrigerator and dishwasher parts, assist with installation, 
compatibility questions, and troubleshooting issues. ONLY answer questions related to refrigerator and dishwasher parts.

For any questions outside this scope, politely explain that you can only help with refrigerator and dishwasher parts
and redirect the conversation back to these topics.

When providing information about parts:
1. Be specific about part numbers, compatibility, and installation procedures
2. Include relevant details about the part's features and benefits
3. Explain how the part solves specific problems or symptoms
4. Recommend proper tools or additional parts if needed for installation

IMPORTANT: Only suggest a specific part when:
- The user is asking about a specific part they need to purchase
- The user is experiencing symptoms that can be fixed by a specific part
- The user is comparing different parts or asking for recommendations
- The user explicitly asks for a part recommendation

DO NOT suggest parts when:
- The user is asking about installation steps for a part they already have
- The user is asking about troubleshooting steps that don't require a new part
- The user is asking general questions about appliance maintenance
- The conversation is about a part they already have and are trying to use/install
- The user is asking how to install a specific part they already have

When providing installation instructions or troubleshooting steps, use EXACTLY this format:

**Installation Steps:**
1. Step one description
2. Step two description
   - Sub-point if needed
   - Another sub-point
3. Step three description

**Important Notes:**
- Note one
- Note two
- Note three

DO NOT:
- Mix numbered steps with bullet points in the same section
- Add extra text between steps
- Include product suggestions unless explicitly asked for
- Add unnecessary formatting or styling

If you don't know the answer, acknowledge that and suggest that the customer may want to 
contact PartSelect customer service for more detailed assistance.
"""
        
        # Build messages array
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        # Add chat history
        for message in chat_history:
            messages.append({
                "role": message["role"],
                "content": message["content"]
            })
        
        # Add context and user query
        if context:
            messages.append({
                "role": "user", 
                "content": f"Based on the following relevant information, please answer my question. Only use this information if it's directly relevant to my question:\n\n{context}\n\nMy question is: {query}"
            })
        else:
            messages.append({"role": "user", "content": query})
        
        # Generate response using DeepSeek API
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "deepseek-chat",
            "messages": messages,
            "temperature": self.deepseek_temperature,
            "max_tokens": 1000
        }
        
        try:
            response = requests.post(DEEPSEEK_CHAT_URL, headers=headers, json=data)
            response.raise_for_status()
            
            # Parse the response
            result = response.json()
            assistant_response = result["choices"][0]["message"]["content"]
            
            # Only include part_info if the response suggests a specific part
            should_include_part = any(keyword in assistant_response.lower() for keyword in [
                "part number", "part id", "you need", "recommend", "suggest", "replace with"
            ])
            
            return {
                "response": assistant_response,
                "part_info": part_info if should_include_part else None,
                "search_results": search_results
            }
            
        except requests.exceptions.RequestException as e:
            print(f"API request failed: {e}")
            return {
                "response": "I'm sorry, I'm having trouble connecting to my knowledge base. Please try again later.",
                "part_info": None,
                "search_results": []
            }

# API Server
app = Flask(__name__)
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000"],  # React's default port
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})  # Enable CORS for all routes

# Initialize RAG system
rag_system = None

@app.route('/api/chat', methods=['POST'])
def chat():
    global rag_system
    
    try:
        # Initialize RAG system if not already done
        if rag_system is None:
            rag_system = PartSelectRAG()
        
        # Get request data
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        query = data.get('query', '')
        if not query:
            return jsonify({"error": "No query provided"}), 400
            
        chat_history = data.get('chat_history', [])
        
        # Generate response
        response_data = rag_system.generate_response(query, chat_history)
        
        return jsonify(response_data)
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        return jsonify({
            "error": "An error occurred while processing your request",
            "details": str(e)
        }), 500

@app.route('/api/search', methods=['POST'])
def search():
    global rag_system
    
    # Initialize RAG system if not already done
    if rag_system is None:
        rag_system = PartSelectRAG()
    
    # Get request data
    data = request.json
    query = data.get('query', '')
    
    # Search for relevant QA pairs
    search_results = rag_system.search(query, k=5)
    
    return jsonify({"results": search_results})

# Add a new endpoint to get part information by ID
@app.route('/api/part/<part_id>', methods=['GET'])
def get_part(part_id):
    global rag_system
    
    # Initialize RAG system if not already done
    if rag_system is None:
        rag_system = PartSelectRAG()
    
    # Find part in QA data
    if part_id in rag_system.all_qa_data:
        part_data = rag_system.all_qa_data[part_id]
        return jsonify({
            "part_id": part_id,
            "part_info": part_data["part_info"],
            "appliance_type": part_data.get("appliance_type", "unknown")
        })
    else:
        return jsonify({"error": "Part not found"}), 404

if __name__ == "__main__":
    # Initialize RAG system
    rag_system = PartSelectRAG()
    
    # Run API server
    app.run(debug=True, port=5001)