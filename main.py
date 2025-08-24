import requests
import json
import re
from datetime import datetime

def read_prompt():
    """Read prompt from file"""
    with open('prompt.txt', 'r') as file:
        return file.read().strip()

def call_deepseek_api(prompt):
    """Call Deepseek API and return response"""
    try:
        url = "https://api.deepseek.com/chat/completions"
        headers = {"Authorization": "Bearer sk-1c1c6bbcfde04f16a8deaefe6023b1be", "Content-Type": "application/json"}
        data = {"model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}]}
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Connection failed: {e}"

def extract_tag_content(text, tag):
    """Extract content between XML-like tags"""
    pattern = f"<{tag}>(.*?)</{tag}>"
    match = re.search(pattern, text, re.DOTALL)
    return match.group(1).strip() if match else ""

def parse_deepseek_output(output):
    """Parse Deepseek output and extract all questions"""
    questions = []
    
    # Split by question blocks
    question_blocks = re.findall(r'<question-one>(.*?)</question-one>', output, re.DOTALL)
    
    for i, block in enumerate(question_blocks, 1):
        # Extract all the required fields
        question_data = {
            "question_number": i,
            "context": extract_tag_content(block, "context"),
            "passage": extract_tag_content(block, "passage"),
            "question": extract_tag_content(block, "question"),
            "answer_choices": {
                "A": extract_tag_content(block, "answer-choice-one"),
                "B": extract_tag_content(block, "answer-choice-two"),
                "C": extract_tag_content(block, "answer-choice-three"),
                "D": extract_tag_content(block, "answer-choice-four")
            },
            "explanations": {
                "A": extract_tag_content(block, "explanation-one"),
                "B": extract_tag_content(block, "explanation-two"),
                "C": extract_tag_content(block, "explanation-three"),
                "D": extract_tag_content(block, "explanation-four")
            },
            "correct_answer": None,
            "correct_explanation": None
        }
        
        # Find which answer is marked as correct
        for choice, letter in [("answer-choice-one", "A"), ("answer-choice-two", "B"), 
                              ("answer-choice-three", "C"), ("answer-choice-four", "D")]:
            choice_content = extract_tag_content(block, choice)
            if "<correct-answer>" in choice_content:
                question_data["correct_answer"] = letter
                # Clean the correct answer text (remove the correct-answer tags)
                clean_answer = re.sub(r'<correct-answer>.*?</correct-answer>', '', choice_content).strip()
                question_data["answer_choices"][letter] = clean_answer
                break
        
        # Find correct explanation
        for exp, letter in [("explanation-one", "A"), ("explanation-two", "B"), 
                           ("explanation-three", "C"), ("explanation-four", "D")]:
            exp_content = extract_tag_content(block, exp)
            if "<correct-explanation>" in exp_content:
                # Clean the explanation text
                clean_exp = re.sub(r'<correct-explanation>.*?</correct-explanation>', '', exp_content).strip()
                question_data["explanations"][letter] = clean_exp
                question_data["correct_explanation"] = letter
                break
        
        questions.append(question_data)
    
    return questions

def save_to_json(questions, filename="satQuestions.json"):
    """Save parsed questions to JSON file"""
    output_data = {
        "generated_on": datetime.now().isoformat(),
        "total_questions": len(questions),
        "questions": questions
    }
    
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(output_data, file, indent=2, ensure_ascii=False)
    
    print(f"✅ Saved {len(questions)} questions to {filename}")

def main():
    # Read prompt
    prompt = read_prompt()
    print(f"📝 Prompt: {prompt[:100]}...")
    
    # Call Deepseek API
    print("🤖 Calling Deepseek API...")
    response = call_deepseek_api(prompt)
    
    if "Error:" in response or "Connection failed:" in response:
        print(f"❌ {response}")
        return
    
    print("✅ Got response from Deepseek")
    print(f"📄 Response length: {len(response)} characters")
    
    # Write response to output.txt
    print("💾 Writing response to output.txt...")
    with open('output.txt', 'w', encoding='utf-8') as file:
        file.write(response)
    
    print("✅ Response saved to output.txt")
    print(f"📄 Response preview: {response[:200]}...")

if __name__ == "__main__":
    main()