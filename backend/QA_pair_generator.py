import json
import requests
import os
import sys
from typing import List, Dict, Any
import time
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from one directory up
env_path = Path('..') / '.env'
load_dotenv(dotenv_path=env_path)

# Get API key from environment variable
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

if not DEEPSEEK_API_KEY:
    print("Error: DEEPSEEK_API_KEY not found in .env file.")
    print("Please make sure you have a .env file in the parent directory with DEEPSEEK_API_KEY=your_api_key")
    sys.exit(1)
else:
    print("DeepSeek API key loaded successfully.")

# DeepSeek API endpoint
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

# Load the dishwasher parts data
def load_data(file_path: str) -> List[Dict[str, Any]]:
    """Load the dishwasher parts data from a JSON file."""
    with open(file_path, 'r') as f:
        return json.load(f)

# Function to generate QA pairs using DeepSeek API
def generate_qa_pairs(part_data: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    Generate QA pairs for a dishwasher part using DeepSeek API.
    
    Args:
        part_data: Dictionary containing the part information
        
    Returns:
        List of dictionaries, each containing a question and answer pair
    """
    # Construct a detailed prompt for DeepSeek
    prompt = f"""
You are an expert in dishwasher parts and repairs. Your task is to generate comprehensive question-answer pairs for the following dishwasher part:

PART ID: {part_data.get('id', 'N/A')}
NAME: {part_data.get('name', 'N/A')}
PRICE: {part_data.get('price', 'N/A')}
DESCRIPTION: {part_data.get('product_description', 'N/A')}
FIXES SYMPTOMS: {part_data.get('fixes_symptoms', 'N/A')}
TROUBLESHOOTING: {part_data.get('troubleshooting', 'N/A')}
CUSTOMER RATING: {part_data.get('customer_rating', 'N/A')}

Generate at least 15 diverse question-answer pairs that cover different aspects of this part:

1. Questions users might ask about specific symptoms (e.g., "My dishwasher rack won't slide smoothly" or "Why is my dishwasher making noise?")
2. Questions about compatibility with different dishwasher models
3. Questions about installation difficulty and procedures
5. Questions about price and value
6. Questions using everyday language and colloquial terms (how people actually describe problems)
7. Questions that might contain misspellings or incorrect terminology
8. Questions about specific features of the part
9. Any other details that are included in the metadata of the product

For each question, provide a detailed answer that directly addresses the query and explains why this part would be the right solution (or not).

Format each QA pair as:
{{
  "question": "The full question text",
  "answer": "The complete answer"
}}

Return your response as a JSON array of these QA pairs.
"""

    # Make API call to DeepSeek
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "deepseek-chat",  # Use the appropriate DeepSeek model
        "messages": [
            {"role": "system", "content": "You are a helpful assistant that generates question-answer pairs about dishwasher parts."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,  # Slightly creative but mostly factual
        "max_tokens": 2000   # Adjust based on expected response length
    }
    
    try:
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=data)
        response.raise_for_status()
        
        # Parse the response
        result = response.json()
        response_text = result['choices'][0]['message']['content']
        
        # Try to extract the JSON array from the response
        return extract_json_from_llm_response(response_text, part_data['id'])
            
    except requests.exceptions.RequestException as e:
        print(f"API request failed for part {part_data['id']}: {e}")
        return []

def extract_json_from_llm_response(response_text: str, part_id: str) -> List[Dict[str, str]]:
    """
    Extract JSON content from LLM response that might include markdown formatting.
    
    Args:
        response_text: The raw text response from the LLM
        part_id: ID of the part being processed (for error logging)
        
    Returns:
        List of QA pair dictionaries
    """
    # Try several strategies to extract valid JSON
    try:
        # First attempt: Try to parse the entire response as JSON
        return json.loads(response_text)
    except json.JSONDecodeError:
        pass
    
    try:
        # Second attempt: Extract content from markdown code blocks
        import re
        json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', response_text)
        if json_match:
            json_content = json_match.group(1).strip()
            return json.loads(json_content)
    except (json.JSONDecodeError, AttributeError):
        pass
    
    try:
        # Third attempt: Try to find a JSON array pattern in the text
        import re
        # Look for a pattern that starts with [ and ends with ] with any content in between
        array_match = re.search(r'\[\s*{[\s\S]*}\s*\]', response_text)
        if array_match:
            json_content = array_match.group(0).strip()
            return json.loads(json_content)
    except (json.JSONDecodeError, AttributeError):
        pass
    
    # If we got here, we couldn't parse the JSON
    print(f"Error parsing response for part {part_id}")
    print(f"Raw response: {response_text}")
    return []

# Process all parts and save results
def process_all_parts(data_path: str, output_path: str):
    """
    Process all dishwasher parts and generate QA pairs.
    
    Args:
        data_path: Path to the JSON file containing dishwasher parts
        output_path: Path to save the generated QA pairs
    """
    parts_data = load_data(data_path)
    all_qa_pairs = {}
    
    for i, part in enumerate(parts_data):
        print(f"Processing part {i+1}/{len(parts_data)}: {part['id']} - {part['name']}")
        
        # Generate QA pairs for this part
        qa_pairs = generate_qa_pairs(part)
        
        # Add part information to each QA pair
        for qa_pair in qa_pairs:
            qa_pair["part_id"] = part["id"]
            qa_pair["part_name"] = part["name"]
        
        # Store the QA pairs
        all_qa_pairs[part['id']] = {
            "part_info": part,
            "qa_pairs": qa_pairs
        }
        
        # Introduce a delay to avoid rate limiting
        time.sleep(1)
    
    # Save all QA pairs to a JSON file
    with open(output_path, 'w') as f:
        json.dump(all_qa_pairs, f, indent=2)
    
    print(f"QA pairs generated and saved to {output_path}")
    
    # Print some statistics
    total_pairs = sum(len(data["qa_pairs"]) for data in all_qa_pairs.values())
    print(f"Total parts processed: {len(parts_data)}")
    print(f"Total QA pairs generated: {total_pairs}")
    print(f"Average QA pairs per part: {total_pairs / len(parts_data):.2f}")

# Example usage
if __name__ == "__main__":
    # Customize these paths as needed
    input_path = "refridgerator_data.json"
    output_path = "refridgerator_qa_pairs.json"
    
    process_all_parts(input_path, output_path)


def analyze_qa_pairs(qa_pairs_path: str):
    """
    Analyze the generated QA pairs to identify coverage and patterns.
    
    Args:
        qa_pairs_path: Path to the JSON file containing generated QA pairs
    """
    with open(qa_pairs_path, 'r') as f:
        all_qa_pairs = json.load(f)
    
    # Extract all questions
    all_questions = []
    for part_id, data in all_qa_pairs.items():
        for qa in data["qa_pairs"]:
            all_questions.append({
                "part_id": part_id,
                "part_name": data["part_info"]["name"],
                "question": qa["question"]
            })
    
    # Analyze question types/patterns
    question_patterns = {
        "symptom": 0,
        "compatibility": 0,
        "installation": 0,
        "comparison": 0,
        "price": 0,
        "feature": 0,
        "durability": 0,
        "multiple_symptoms": 0
    }
    
    # Simple keyword-based classification
    keywords = {
        "symptom": ["not", "isn't", "doesn't", "won't", "problem", "issue", "symptom", "broken", "fix", "repair"],
        "compatibility": ["compatible", "work with", "fit", "model", "brand", "replacement"],
        "installation": ["install", "replace", "difficult", "easy", "how to", "steps", "tool"],
        "comparison": ["better", "worse", "alternative", "other", "difference", "compare", "versus", "vs"],
        "price": ["price", "cost", "expensive", "cheap", "worth", "value"],
        "feature": ["feature", "color", "size", "material", "plastic", "metal"],
        "durability": ["last", "long", "durable", "lifetime", "warranty", "break again"]
    }
    
    for q in all_questions:
        question = q["question"].lower()
        
        # Count pattern occurrences
        for pattern, terms in keywords.items():
            if any(term in question for term in terms):
                question_patterns[pattern] += 1
        
        # Check for multiple symptoms
        symptom_count = sum(1 for term in keywords["symptom"] if term in question)
        if symptom_count > 1:
            question_patterns["multiple_symptoms"] += 1
    
    print("\nQuestion Pattern Analysis:")
    for pattern, count in question_patterns.items():
        print(f"{pattern}: {count} questions ({count/len(all_questions)*100:.1f}%)")
    
    print("\nSample Questions by Part:")
    for part_id, data in list(all_qa_pairs.items())[:3]:  # Show first 3 parts
        print(f"\n{data['part_info']['name']} ({part_id}):")
        for qa in data["qa_pairs"][:3]:  # Show first 3 questions
            print(f"- {qa['question']}")