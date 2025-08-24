import firebase_admin
from firebase_admin import credentials, firestore
import json
import re
from datetime import datetime
import os

# Firebase Configuration - Updated with your actual Firebase project details
FIREBASE_PROJECT_ID = "cooksat-sat-questions"
FIREBASE_SERVICE_ACCOUNT_KEY_PATH = "./cooksat-sat-questions-firebase-adminsdk-fbsvc-25a836b83a.json"
FIRESTORE_COLLECTION_NAME = "questions"

class FirebaseParser:
    def __init__(self):
        """Initialize Firebase connection"""
        self.db = None
        self.initialize_firebase()
    
    def initialize_firebase(self):
        """Initialize Firebase Admin SDK"""
        try:
            # Check if Firebase app is already initialized
            if not firebase_admin._apps:
                # Initialize Firebase with service account credentials
                cred = credentials.Certificate(FIREBASE_SERVICE_ACCOUNT_KEY_PATH)
                firebase_admin.initialize_app(cred, {
                    'projectId': FIREBASE_PROJECT_ID
                })
                print("✅ Firebase initialized successfully")
            else:
                print("✅ Firebase already initialized")
            
            # Get Firestore client
            self.db = firestore.client()
            print("✅ Firestore client ready")
            
        except FileNotFoundError:
            print("❌ Error: Service account key file not found!")
            print(f"   Please download your service account key from Firebase Console")
            print(f"   and save it as: {FIREBASE_SERVICE_ACCOUNT_KEY_PATH}")
            print("\n📋 Steps to get your service account key:")
            print("   1. Go to https://console.firebase.google.com/")
            print("   2. Select your project")
            print("   3. Click ⚙️ (Settings) > Project settings")
            print("   4. Go to 'Service accounts' tab")
            print("   5. Click 'Generate new private key'")
            print("   6. Save the JSON file as 'serviceAccountKey.json' in this folder")
        except Exception as e:
            print(f"❌ Error initializing Firebase: {e}")
    
    def read_deepseek_output(self, filename="output.txt"):
        """Read the Deepseek output from file"""
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                content = file.read()
            print(f"✅ Read {len(content)} characters from {filename}")
            return content
        except FileNotFoundError:
            print(f"❌ Error: {filename} not found!")
            print("   Please run main.py first to generate the output")
            return None
        except Exception as e:
            print(f"❌ Error reading file: {e}")
            return None
    
    def extract_tag_content(self, text, tag):
        """Extract content between XML-like tags"""
        pattern = f"<{tag}>(.*?)</{tag}>"
        match = re.search(pattern, text, re.DOTALL)
        return match.group(1).strip() if match else ""
    
    def extract_clean_content(self, text, tag):
        """Extract content between XML-like tags, handling nested tags"""
        pattern = f"<{tag}>(.*?)</{tag}>"
        match = re.search(pattern, text, re.DOTALL)
        if match:
            content = match.group(1).strip()
            # If the content contains nested tags like <correct-answer>, extract the inner content
            if "<correct-answer>" in content:
                inner_match = re.search(r"<correct-answer>(.*?)</correct-answer>", content, re.DOTALL)
                if inner_match:
                    return inner_match.group(1).strip()
            elif "<correct-explanation>" in content:
                inner_match = re.search(r"<correct-explanation>(.*?)</correct-explanation>", content, re.DOTALL)
                if inner_match:
                    return inner_match.group(1).strip()
            return content
        return ""
    
    def parse_context(self, context):
        """Parse context to extract subject, category, and difficulty"""
        # Example: "Reading: Information and Ideas: Central Ideas: Hard"
        parts = context.split(": ")
        
        if len(parts) >= 4:
            subject = parts[0].strip()  # "Reading"
            category = parts[1].strip()  # "Information and Ideas"
            subcategory = parts[2].strip()  # "Central Ideas"
            difficulty = parts[3].strip()  # "Hard"
        elif len(parts) >= 3:
            subject = parts[0].strip()
            category = parts[1].strip()
            difficulty = parts[2].strip()
            subcategory = "General"
        else:
            subject = "Unknown"
            category = "Unknown"
            subcategory = "Unknown"
            difficulty = "Unknown"
        
        return {
            "subject": subject,
            "category": category,
            "subcategory": subcategory,
            "difficulty": difficulty
        }
    
    def parse_sat_questions(self, content):
        """Parse SAT questions from the XML-like format"""
        questions = []
        
        # Split by question blocks - handle both question-one and question-two formats
        question_blocks = re.findall(r'<question-[^>]+>(.*?)</question-[^>]+>', content, re.DOTALL)
        
        for i, block in enumerate(question_blocks, 1):
            # Extract all the required fields
            context = self.extract_tag_content(block, "context")
            context_info = self.parse_context(context)
            
            question_data = {
                "question_id": f"q_{i:03d}",
                "context": context,
                "subject": context_info["subject"],
                "category": context_info["category"],
                "subcategory": context_info["subcategory"],
                "difficulty": context_info["difficulty"],
                "passage": self.extract_tag_content(block, "passage"),
                "question": self.extract_tag_content(block, "question"),
                "answer_choices": {
                    "A": self.extract_tag_content(block, "answer-choice-one"),
                    "B": self.extract_tag_content(block, "answer-choice-two"),
                    "C": self.extract_tag_content(block, "answer-choice-three"),
                    "D": self.extract_tag_content(block, "answer-choice-four")
                },
                "explanations": {
                    "A": self.extract_tag_content(block, "explanation-one"),
                    "B": self.extract_tag_content(block, "explanation-two"),
                    "C": self.extract_tag_content(block, "explanation-three"),
                    "D": self.extract_tag_content(block, "explanation-four")
                },
                "correct_answer": None,
                "correct_explanation": None,
                "created_at": datetime.now().isoformat()
            }
            
            # Process all answer choices and find the correct one
            for choice, letter in [("answer-choice-one", "A"), ("answer-choice-two", "B"), 
                                  ("answer-choice-three", "C"), ("answer-choice-four", "D")]:
                choice_content = self.extract_tag_content(block, choice)
                if "<correct-answer>" in choice_content:
                    question_data["correct_answer"] = letter
                    # Get the clean content (without tags)
                    clean_answer = self.extract_clean_content(block, choice)
                    question_data["answer_choices"][letter] = clean_answer
                else:
                    # Store the answer choice as is
                    question_data["answer_choices"][letter] = choice_content
            
            # Process all explanations and find the correct one
            for exp, letter in [("explanation-one", "A"), ("explanation-two", "B"), 
                               ("explanation-three", "C"), ("explanation-four", "D")]:
                exp_content = self.extract_tag_content(block, exp)
                if "<correct-explanation>" in exp_content:
                    # Store the actual explanation text, not just the letter
                    clean_exp = self.extract_clean_content(block, exp)
                    question_data["correct_explanation"] = clean_exp
                    question_data["explanations"][letter] = clean_exp
                else:
                    # Store the explanation as is
                    question_data["explanations"][letter] = exp_content
            
            questions.append(question_data)
        
        return questions
    
    def save_questions_to_firestore(self, questions):
        """Save parsed questions to Firestore with hierarchical subcollection structure"""
        if not self.db:
            print("❌ Firestore client not initialized")
            return False
        
        try:
            saved_count = 0
            for question in questions:
                # Create hierarchical subcollection path: questions/subject/category/subcategory/difficulty/question_id
                
                # Navigate through the subcollections
                subject_collection = self.db.collection('questions').document(question['subject'])
                category_collection = subject_collection.collection(question['category'])
                subcategory_collection = category_collection.document(question['subcategory'])
                difficulty_collection = subcategory_collection.collection(question['difficulty'])
                question_doc = difficulty_collection.document(question['question_id'])
                
                # Save the question
                question_doc.set(question)
                saved_count += 1
                
                print(f"✅ Saved question {question['question_id']}")
                print(f"   Path: questions/{question['subject']}/{question['category']}/{question['subcategory']}/{question['difficulty']}/{question['question_id']}")
                print(f"   Question: {question['question'][:50]}...")
                print(f"   Correct Answer: {question['correct_answer']}")
                print()
            
            print(f"🎉 Successfully saved {saved_count} questions to Firestore!")
            print("📁 Questions are organized in subcollections: questions/subject/category/subcategory/difficulty/")
            return True
        except Exception as e:
            print(f"❌ Error saving to Firestore: {e}")
            print("   This might be due to Firestore security rules. Make sure your rules allow writing to subcollections.")
            return False
    
    def process_output(self, output_file="output.txt"):
        """Main method to process the output and save to Firebase"""
        print("🚀 Starting Firebase parsing process...")
        
        # Read the output
        content = self.read_deepseek_output(output_file)
        if not content:
            return False
        
        # Parse the SAT questions
        print("🔍 Parsing SAT questions...")
        questions = self.parse_sat_questions(content)
        
        if questions:
            print(f"✅ Parsed {len(questions)} questions")
            
            # Save to Firestore
            success = self.save_questions_to_firestore(questions)
            
            if success:
                print("\n📊 Questions Summary:")
                for q in questions:
                    print(f"   - {q['question_id']}: {q['subject']} → {q['category']} → {q['difficulty']}")
                    print(f"     Correct Answer: {q['correct_answer']}")
                    print(f"     Question: {q['question'][:40]}...")
                    print()
            else:
                print("❌ Failed to save questions to Firebase")
        else:
            print("❌ No questions found in the response")
            print("Raw response preview:")
            print(content[:500] + "..." if len(content) > 500 else content)
        
        return len(questions) > 0

def main():
    """Main function to run the parser"""
    parser = FirebaseParser()
    
    # Process the output and save to Firestore
    success = parser.process_output()
    
    if success:
        print("\n✅ Firebase parsing completed successfully!")
        print("📝 Your questions are now organized in Firestore by subject → category → difficulty!")
    else:
        print("\n❌ Firebase parsing failed. Please check the configuration.")

if __name__ == "__main__":
    main()
