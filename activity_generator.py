import os
import json
from typing import Dict, List, Any, Optional

class ActivityGenerator:
    """
    Service for generating interactive activities for educational platforms
    """
    
    def __init__(self, output_folder: str):
        """
        Initialize the activity generator
        
        Args:
            output_folder: Path to the folder where generated activities will be saved
        """
        self.output_folder = output_folder
        
        # Ensure output folder exists
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
    
    def generate_kahoot_activities(self, content: Dict[str, Any], activity_name: str = None) -> str:
        """
        Generate Kahoot activities from extracted content
        
        Args:
            content: Dictionary containing extracted content
            activity_name: Name of the activity
            
        Returns:
            Path to the generated activity file
        """
        # Generate activity name if not provided
        if activity_name is None:
            activity_name = f"kahoot_{os.path.basename(content.get('title', 'untitled'))}"
        
        # Create Kahoot activity structure
        kahoot_activity = {
            "title": content.get("title", "Untitled Activity"),
            "description": "Interactive quiz generated from lesson content",
            "questions": self._generate_kahoot_questions(content)
        }
        
        # Save activity to file
        output_path = os.path.join(self.output_folder, f"{activity_name}.json")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(kahoot_activity, f, ensure_ascii=False, indent=2)
        
        return output_path
    
    def generate_nearpod_activities(self, content: Dict[str, Any], activity_name: str = None) -> str:
        """
        Generate Nearpod activities from extracted content
        
        Args:
            content: Dictionary containing extracted content
            activity_name: Name of the activity
            
        Returns:
            Path to the generated activity file
        """
        # Generate activity name if not provided
        if activity_name is None:
            activity_name = f"nearpod_{os.path.basename(content.get('title', 'untitled'))}"
        
        # Create Nearpod activity structure
        nearpod_activity = {
            "title": content.get("title", "Untitled Activity"),
            "description": "Interactive activities generated from lesson content",
            "activities": self._generate_nearpod_activities(content)
        }
        
        # Save activity to file
        output_path = os.path.join(self.output_folder, f"{activity_name}.json")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(nearpod_activity, f, ensure_ascii=False, indent=2)
        
        return output_path
    
    def _generate_kahoot_questions(self, content: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate Kahoot questions from content
        
        Args:
            content: Dictionary containing extracted content
            
        Returns:
            List of Kahoot questions
        """
        questions = []
        
        # Generate multiple choice questions from headings
        if "structure" in content and "headings" in content["structure"]:
            for heading in content["structure"]["headings"]:
                # Skip very short headings
                if len(heading["text"]) < 10:
                    continue
                
                # Create a question based on the heading
                question = {
                    "type": "quiz",
                    "question": f"ما هو المفهوم الصحيح لـ {heading['text']}؟",  # "What is the correct concept for {heading}?" in Arabic
                    "time": 20000,  # 20 seconds
                    "points": 1000,
                    "answers": [
                        {"text": "الإجابة الصحيحة", "correct": True},  # "Correct answer" in Arabic
                        {"text": "إجابة خاطئة 1", "correct": False},  # "Wrong answer 1" in Arabic
                        {"text": "إجابة خاطئة 2", "correct": False},  # "Wrong answer 2" in Arabic
                        {"text": "إجابة خاطئة 3", "correct": False}   # "Wrong answer 3" in Arabic
                    ]
                }
                
                questions.append(question)
        
        # Generate true/false questions from paragraphs
        if "structure" in content and "paragraphs" in content["structure"]:
            for paragraph in content["structure"]["paragraphs"]:
                # Skip very short or very long paragraphs
                if len(paragraph) < 20 or len(paragraph) > 200:
                    continue
                
                # Create a true/false question based on the paragraph
                question = {
                    "type": "true_false",
                    "question": paragraph[:100] + "...",  # Use first 100 characters of paragraph
                    "time": 10000,  # 10 seconds
                    "points": 500,
                    "answers": [
                        {"text": "صحيح", "correct": True},  # "True" in Arabic
                        {"text": "خطأ", "correct": False}   # "False" in Arabic
                    ]
                }
                
                questions.append(question)
        
        # Generate matching questions from bullet points
        if "structure" in content and "bullet_points" in content["structure"]:
            for bullet_list in content["structure"]["bullet_points"]:
                # Skip lists with fewer than 2 items
                if len(bullet_list) < 2:
                    continue
                
                # Create a matching question based on the bullet list
                question = {
                    "type": "matching",
                    "question": "طابق بين العناصر التالية:",  # "Match the following items:" in Arabic
                    "time": 30000,  # 30 seconds
                    "points": 1000,
                    "pairs": []
                }
                
                # Add pairs (limited to 4)
                for i in range(min(4, len(bullet_list))):
                    pair = {
                        "left": bullet_list[i],
                        "right": f"التعريف {i+1}"  # "Definition {i+1}" in Arabic
                    }
                    question["pairs"].append(pair)
                
                questions.append(question)
        
        # Limit to 10 questions
        return questions[:10]
    
    def _generate_nearpod_activities(self, content: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate Nearpod activities from content
        
        Args:
            content: Dictionary containing extracted content
            
        Returns:
            List of Nearpod activities
        """
        activities = []
        
        # Generate classification board activity
        classification_activity = {
            "type": "classification_board",
            "title": "تصنيف المفاهيم",  # "Concept Classification" in Arabic
            "description": "اسحب المفاهيم إلى الفئات المناسبة",  # "Drag concepts to appropriate categories" in Arabic
            "categories": ["الفئة 1", "الفئة 2", "الفئة 3"],  # "Category 1, 2, 3" in Arabic
            "items": []
        }
        
        # Add items to classification board
        if "structure" in content and "bullet_points" in content["structure"]:
            for bullet_list in content["structure"]["bullet_points"]:
                for bullet in bullet_list:
                    classification_activity["items"].append({
                        "text": bullet,
                        "category": "الفئة 1"  # Default category
                    })
        
        activities.append(classification_activity)
        
        # Generate drawing activity
        drawing_activity = {
            "type": "drawing",
            "title": "رسم توضيحي",  # "Illustrative Drawing" in Arabic
            "description": "ارسم شكلاً توضيحياً للمفهوم",  # "Draw an illustrative diagram for the concept" in Arabic
            "background_image": None
        }
        
        activities.append(drawing_activity)
        
        # Generate matching pairs activity
        matching_activity = {
            "type": "matching_pairs",
            "title": "مطابقة المفاهيم",  # "Matching Concepts" in Arabic
            "description": "اربط كل مفهوم بتعريفه المناسب",  # "Connect each concept with its appropriate definition" in Arabic
            "pairs": []
        }
        
        # Add pairs to matching activity
        if "structure" in content and "headings" in content["structure"]:
            for i, heading in enumerate(content["structure"]["headings"]):
                if i < 5:  # Limit to 5 pairs
                    matching_activity["pairs"].append({
                        "left": heading["text"],
                        "right": f"تعريف {heading['text']}"  # "Definition of {heading}" in Arabic
                    })
        
        activities.append(matching_activity)
        
        # Generate quiz activity
        quiz_activity = {
            "type": "quiz",
            "title": "اختبار قصير",  # "Short Quiz" in Arabic
            "description": "أجب عن الأسئلة التالية",  # "Answer the following questions" in Arabic
            "questions": []
        }
        
        # Add questions to quiz
        if "structure" in content and "paragraphs" in content["structure"]:
            for i, paragraph in enumerate(content["structure"]["paragraphs"]):
                if i < 3:  # Limit to 3 questions
                    quiz_activity["questions"].append({
                        "question": f"ما هي الفكرة الرئيسية في النص التالي: {paragraph[:50]}...؟",  # "What is the main idea in the following text: {paragraph}...?" in Arabic
                        "options": [
                            "الخيار 1",  # "Option 1" in Arabic
                            "الخيار 2",  # "Option 2" in Arabic
                            "الخيار 3",  # "Option 3" in Arabic
                            "الخيار 4"   # "Option 4" in Arabic
                        ],
                        "correct_answer": 0  # Index of correct answer
                    })
        
        activities.append(quiz_activity)
        
        # Generate collaborative activity
        collaborative_activity = {
            "type": "collaborative_board",
            "title": "لوحة تعاونية",  # "Collaborative Board" in Arabic
            "description": "شارك أفكارك حول الموضوع",  # "Share your thoughts about the topic" in Arabic
            "prompt": content.get("title", "شارك أفكارك")  # "Share your thoughts" in Arabic
        }
        
        activities.append(collaborative_activity)
        
        return activities
