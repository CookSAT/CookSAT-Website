"""
Example usage of the Azure Deepseek client for generating SAT questions.
This script shows how to use your own prompts and save responses to JSON.
"""

from azure_deepseek_client import AzureDeepseekClient
from config import AZURE_ENDPOINT, AZURE_API_KEY, AZURE_DEPLOYMENT_NAME


def example_single_prompt():
    """Example of processing a single prompt."""
    
    # Initialize the client
    client = AzureDeepseekClient(AZURE_ENDPOINT, AZURE_API_KEY, AZURE_DEPLOYMENT_NAME)
    
    # Your custom prompt
    custom_prompt = """
    Create a challenging SAT Math question about quadratic equations.
    The question should:
    - Be at a high difficulty level
    - Include a real-world scenario
    - Have 4 multiple choice options
    - Include the correct answer and detailed explanation
    
    Please format your response as a clear, well-structured question.
    """
    
    print("Processing custom prompt...")
    response = client.process_prompt_and_save(custom_prompt)
    
    if "error" in response:
        print(f"Error occurred: {response['error']}")
    else:
        print("✅ Response generated and saved to satQuestions.json")
        print(f"📝 Response preview: {response['response'][:300]}...")
        print(f"📊 Tokens used: {response['usage']['total_tokens']}")


def example_batch_prompts():
    """Example of processing multiple prompts in batch."""
    
    # Initialize the client
    client = AzureDeepseekClient(AZURE_ENDPOINT, AZURE_API_KEY, AZURE_DEPLOYMENT_NAME)
    
    # List of your custom prompts
    custom_prompts = [
        "Generate a SAT Reading question about historical events with 4 multiple choice options.",
        "Create a SAT Writing question focusing on punctuation and grammar rules.",
        "Design a SAT Math question about probability and statistics.",
        "Write a SAT Reading question about scientific discoveries."
    ]
    
    print("Processing batch prompts...")
    responses = client.batch_process_prompts(custom_prompts)
    
    print(f"✅ Successfully processed {len(responses)} prompts")
    for i, response in enumerate(responses, 1):
        if "error" in response:
            print(f"❌ Prompt {i} failed: {response['error']}")
        else:
            print(f"✅ Prompt {i} completed successfully")


def example_with_different_settings():
    """Example with custom model settings."""
    
    # Initialize the client
    client = AzureDeepseekClient(AZURE_ENDPOINT, AZURE_API_KEY, AZURE_DEPLOYMENT_NAME)
    
    # Custom prompt with specific requirements
    prompt = "Generate a creative SAT essay prompt about technology and society."
    
    # Use different settings for more creative output
    response = client.process_prompt_and_save(
        prompt=prompt,
        max_tokens=1500,  # More tokens for longer response
        temperature=0.9   # Higher temperature for more creativity
    )
    
    if "error" not in response:
        print("✅ Creative response generated with custom settings")
        print(f"🎨 Response: {response['response'][:200]}...")


if __name__ == "__main__":
    print("🚀 Azure Deepseek Client Examples")
    print("=" * 40)
    
    # Make sure to update config.py with your actual Azure AI credentials first
    if AZURE_ENDPOINT == "YOUR_AZURE_AI_ENDPOINT":
        print("⚠️  Please update config.py with your actual Azure AI credentials first!")
        print("   - Set AZURE_ENDPOINT to your Azure AI endpoint")
        print("   - Set AZURE_API_KEY to your Azure AI API key")
        print("   - Set AZURE_DEPLOYMENT_NAME to your Deepseek deployment name")
    else:
        print("1. Single prompt example:")
        example_single_prompt()
        
        print("\n2. Batch prompts example:")
        example_batch_prompts()
        
        print("\n3. Custom settings example:")
        example_with_different_settings()
        
        print("\n📁 All responses have been saved to satQuestions.json")
