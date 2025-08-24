import json
import os
from datetime import datetime
from typing import Dict, Any, Optional
import requests
from azure.core.credentials import AzureKeyCredential
from azure.ai.openai import AzureOpenAI


class AzureDeepseekClient:
    """
    Client for interacting with Azure AI Deepseek model and storing responses in JSON format.
    """
    
    def __init__(self, endpoint: str, api_key: str, deployment_name: str):
        """
        Initialize the Azure Deepseek client.
        
        Args:
            endpoint: Azure AI endpoint URL
            api_key: Azure AI API key
            deployment_name: Name of the deployed Deepseek model
        """
        self.endpoint = endpoint
        self.api_key = api_key
        self.deployment_name = deployment_name
        
        # Initialize Azure OpenAI client
        self.client = AzureOpenAI(
            azure_endpoint=endpoint,
            api_key=api_key,
            api_version="2024-02-15-preview"  # Use latest API version
        )
        
        # JSON file path for storing responses
        self.json_file_path = "satQuestions.json"
        
    def load_existing_data(self) -> list:
        """
        Load existing data from the JSON file.
        
        Returns:
            List of existing questions/responses
        """
        if os.path.exists(self.json_file_path):
            try:
                with open(self.json_file_path, 'r', encoding='utf-8') as file:
                    return json.load(file)
            except (json.JSONDecodeError, FileNotFoundError):
                return []
        return []
    
    def save_to_json(self, data: list):
        """
        Save data to the JSON file with proper formatting.
        
        Args:
            data: List of data to save
        """
        with open(self.json_file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=2, ensure_ascii=False)
    
    def generate_response(self, prompt: str, max_tokens: int = 1000, temperature: float = 0.7) -> Dict[str, Any]:
        """
        Generate a response from the Azure Deepseek model.
        
        Args:
            prompt: The input prompt to send to the model
            max_tokens: Maximum number of tokens in the response
            temperature: Controls randomness in the response (0.0 to 1.0)
            
        Returns:
            Dictionary containing the response and metadata
        """
        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            return {
                "prompt": prompt,
                "response": response.choices[0].message.content,
                "model": self.deployment_name,
                "timestamp": datetime.now().isoformat(),
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
            
        except Exception as e:
            return {
                "prompt": prompt,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "model": self.deployment_name
            }
    
    def process_prompt_and_save(self, prompt: str, max_tokens: int = 1000, temperature: float = 0.7) -> Dict[str, Any]:
        """
        Process a prompt and save the response to the JSON file.
        
        Args:
            prompt: The input prompt
            max_tokens: Maximum number of tokens in the response
            temperature: Controls randomness in the response
            
        Returns:
            Dictionary containing the response data
        """
        # Generate response from the model
        response_data = self.generate_response(prompt, max_tokens, temperature)
        
        # Load existing data
        existing_data = self.load_existing_data()
        
        # Add new response to the data
        existing_data.append(response_data)
        
        # Save updated data to JSON file
        self.save_to_json(existing_data)
        
        return response_data
    
    def batch_process_prompts(self, prompts: list, max_tokens: int = 1000, temperature: float = 0.7) -> list:
        """
        Process multiple prompts in batch and save all responses.
        
        Args:
            prompts: List of prompts to process
            max_tokens: Maximum number of tokens per response
            temperature: Controls randomness in responses
            
        Returns:
            List of response data for all prompts
        """
        responses = []
        existing_data = self.load_existing_data()
        
        for i, prompt in enumerate(prompts):
            print(f"Processing prompt {i+1}/{len(prompts)}...")
            response_data = self.generate_response(prompt, max_tokens, temperature)
            responses.append(response_data)
            existing_data.append(response_data)
        
        # Save all responses to JSON file
        self.save_to_json(existing_data)
        
        return responses


def main():
    """
    Example usage of the Azure Deepseek client.
    """
    # Configuration - Replace with your actual Azure AI settings
    ENDPOINT = "YOUR_AZURE_AI_ENDPOINT"  # e.g., "https://your-resource.openai.azure.com/"
    API_KEY = "YOUR_AZURE_AI_API_KEY"
    DEPLOYMENT_NAME = "YOUR_DEEPSEEK_DEPLOYMENT_NAME"  # e.g., "deepseek-chat"
    
    # Initialize the client
    client = AzureDeepseekClient(ENDPOINT, API_KEY, DEPLOYMENT_NAME)
    
    # Example prompt for SAT questions
    sample_prompt = """
    Generate a SAT Math question with the following requirements:
    - Topic: Algebra
    - Difficulty: Medium
    - Include 4 multiple choice options (A, B, C, D)
    - Provide the correct answer
    - Include a brief explanation of the solution
    
    Format the response as JSON with the following structure:
    {
        "question": "The question text",
        "options": {
            "A": "Option A",
            "B": "Option B", 
            "C": "Option C",
            "D": "Option D"
        },
        "correct_answer": "A",
        "explanation": "Brief explanation of the solution"
    }
    """
    
    # Process the prompt and save to JSON
    print("Generating SAT question...")
    response = client.process_prompt_and_save(sample_prompt)
    
    if "error" in response:
        print(f"Error: {response['error']}")
    else:
        print("Response generated and saved to satQuestions.json")
        print(f"Response: {response['response'][:200]}...")  # Show first 200 characters
    
    # Example of batch processing multiple prompts
    batch_prompts = [
        "Generate a SAT Reading question about science.",
        "Generate a SAT Writing question about grammar.",
        "Generate a SAT Math question about geometry."
    ]
    
    print("\nProcessing batch prompts...")
    batch_responses = client.batch_process_prompts(batch_prompts)
    print(f"Processed {len(batch_responses)} prompts successfully.")


if __name__ == "__main__":
    main()
