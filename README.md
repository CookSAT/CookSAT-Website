# Azure AI Deepseek SAT Question Generator

This project provides a Python client for interacting with Azure AI Deepseek models to generate SAT questions and store responses in JSON format.

## Features

- 🔗 **Azure AI Integration**: Connect to your deployed Deepseek model via Azure AI
- 📝 **JSON Storage**: Automatically save all responses to `satQuestions.json`
- 🔄 **Batch Processing**: Process multiple prompts at once
- ⚙️ **Configurable Settings**: Customize token limits, temperature, and other parameters
- 📊 **Usage Tracking**: Monitor token usage and response metadata
- 🛡️ **Error Handling**: Robust error handling and logging

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Azure AI Settings

Edit `config.py` and replace the placeholder values with your actual Azure AI configuration:

```python
# Azure AI Configuration
AZURE_ENDPOINT = "https://your-resource.openai.azure.com/"
AZURE_API_KEY = "your-azure-ai-api-key"
AZURE_DEPLOYMENT_NAME = "your-deepseek-deployment-name"
```

### 3. Get Your Azure AI Credentials

1. Go to the [Azure Portal](https://portal.azure.com)
2. Navigate to your Azure AI resource
3. Go to "Keys and Endpoint" section
4. Copy the endpoint URL and one of the API keys
5. Note your deployment name from the "Deployments" section

## Usage

### Basic Usage

```python
from azure_deepseek_client import AzureDeepseekClient
from config import AZURE_ENDPOINT, AZURE_API_KEY, AZURE_DEPLOYMENT_NAME

# Initialize the client
client = AzureDeepseekClient(AZURE_ENDPOINT, AZURE_API_KEY, AZURE_DEPLOYMENT_NAME)

# Your custom prompt
prompt = "Generate a SAT Math question about algebra with 4 multiple choice options."

# Process the prompt and save to JSON
response = client.process_prompt_and_save(prompt)

print(f"Response: {response['response']}")
```

### Batch Processing

```python
# Process multiple prompts at once
prompts = [
    "Generate a SAT Reading question about science.",
    "Create a SAT Writing question about grammar.",
    "Design a SAT Math question about geometry."
]

responses = client.batch_process_prompts(prompts)
```

### Custom Settings

```python
# Use custom parameters
response = client.process_prompt_and_save(
    prompt="Your prompt here",
    max_tokens=1500,    # More tokens for longer responses
    temperature=0.9     # Higher temperature for more creativity
)
```

## File Structure

```
CookSAT/
├── azure_deepseek_client.py  # Main client class
├── config.py                 # Configuration settings
├── example_usage.py          # Usage examples
├── requirements.txt          # Python dependencies
├── README.md                # This file
├── main.py                  # Original file
└── satQuestions.json        # Generated output (created automatically)
```

## JSON Output Format

The `satQuestions.json` file contains an array of response objects with the following structure:

```json
[
  {
    "prompt": "Your input prompt",
    "response": "Deepseek model response",
    "model": "your-deployment-name",
    "timestamp": "2024-01-01T12:00:00.000000",
    "usage": {
      "prompt_tokens": 50,
      "completion_tokens": 200,
      "total_tokens": 250
    }
  }
]
```

## Example Scripts

### Run the main example:
```bash
python azure_deepseek_client.py
```

### Run usage examples:
```bash
python example_usage.py
```

## Error Handling

The client includes comprehensive error handling:

- **Network Errors**: Automatic retry and error logging
- **Invalid Credentials**: Clear error messages for authentication issues
- **Rate Limiting**: Handles Azure AI rate limits gracefully
- **JSON Errors**: Safe handling of corrupted JSON files

## Customization

### Adding Custom Prompts

Create your own prompt templates:

```python
def create_sat_math_prompt(topic, difficulty):
    return f"""
    Generate a SAT Math question with the following requirements:
    - Topic: {topic}
    - Difficulty: {difficulty}
    - Include 4 multiple choice options (A, B, C, D)
    - Provide the correct answer
    - Include a brief explanation of the solution
    """
```

### Modifying Output Format

You can customize the JSON structure by modifying the `generate_response` method in `azure_deepseek_client.py`.

## Troubleshooting

### Common Issues

1. **Authentication Error**: Double-check your Azure AI endpoint and API key
2. **Deployment Not Found**: Verify your deployment name in Azure AI
3. **Rate Limiting**: Reduce the frequency of requests or increase your Azure AI quota
4. **JSON File Issues**: Delete `satQuestions.json` if it becomes corrupted

### Debug Mode

Enable debug logging by modifying the client initialization:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Security Notes

- Never commit your API keys to version control
- Use environment variables for production deployments
- Consider using Azure Key Vault for secure credential management

## License

This project is provided as-is for educational and development purposes.
