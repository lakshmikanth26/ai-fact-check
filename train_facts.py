"""
Script to train the fact-checker with pre-verified facts.
This adds common knowledge facts to the knowledge base for instant responses.
"""

from factcheck import FactChecker
from datetime import datetime

# Initialize fact checker
fact_checker = FactChecker()

# Training data organized by category
training_data = {
    "Geography Facts": [
        ("Mount Everest is the tallest mountain on Earth", "True"),
        ("The Sahara Desert is located in South America", "False"),
        ("Australia is both a country and a continent", "True"),
        ("The Amazon River flows through Egypt", "False"),
        ("Antarctica has no permanent human residents", "True"),
    ],
    
    "Science Facts": [
        ("Water boils at 100°C at sea level", "True"),
        ("Humans have three lungs", "False"),
        ("The Earth revolves around the Sun", "True"),
        ("Sound travels faster than light", "False"),
        ("The human body has 206 bones", "True"),
    ],
    
    "History Facts": [
        ("World War II ended in 1945", "True"),
        ("The Roman Empire was founded in the 20th century", "False"),
        ("The Great Wall of China was built to protect against invasions", "True"),
        ("Mahatma Gandhi was born in South Africa", "False"),
        ("The first man on the Moon was Neil Armstrong", "True"),
    ],
    
    "Technology Facts": [
        ("HTML stands for HyperText Markup Language", "True"),
        ("Python was created before C", "False"),
        ("The iPhone was first released in 2007", "True"),
        ("AI stands for Automated Intelligence", "False"),
        ("JavaScript and Java are the same language", "False"),
    ],
    
    "Space Facts": [
        ("Jupiter is the largest planet in our solar system", "True"),
        ("The Sun is a planet", "False"),
        ("The Moon produces its own light", "False"),
        ("Venus is closer to the Sun than Earth", "True"),
        ("Pluto is no longer officially classified as a planet", "True"),
    ],
    
    "General Knowledge": [
        ("A leap year has 366 days", "True"),
        ("A leap year has 365 days", "False"),
        ("The human brain weighs around 1.4 kilograms", "True"),
        ("The Great Pyramid of Giza is in India", "False"),
        ("The chemical symbol for gold is Au", "True"),
        ("There are 25 hours in a day", "False"),
    ],
}

def train_all_facts():
    """Train the fact checker with all predefined facts."""
    total_facts = 0
    
    print("=" * 60)
    print("TRAINING FACT-CHECKER WITH VERIFIED FACTS")
    print("=" * 60)
    
    for category, facts in training_data.items():
        print(f"\n📚 {category}")
        print("-" * 60)
        
        for claim, classification in facts:
            # Add explanation based on classification
            if classification == "True":
                explanation = f"This is a verified true fact: {claim}"
            else:
                explanation = f"This is a verified false fact: {claim}"
            
            # Add to knowledge base with high confidence (0.99 for training data)
            fact_checker.add_user_feedback(
                claim=claim,
                is_correct=classification,
                user_answer=explanation,
                confidence=0.99
            )
            
            total_facts += 1
            print(f"  ✓ Added: {claim[:60]}... [{classification}]")
    
    print("\n" + "=" * 60)
    print(f"✅ TRAINING COMPLETE: {total_facts} facts added to knowledge base")
    print("=" * 60)
    print(f"\nKnowledge base saved to: {fact_checker.knowledge_base_file}")
    print(f"Total facts in database: {len(fact_checker.knowledge_base.get('facts', []))}")
    
    # Show some statistics
    true_facts = sum(1 for f in fact_checker.knowledge_base.get('facts', []) if f.get('classification') == 'True')
    false_facts = sum(1 for f in fact_checker.knowledge_base.get('facts', []) if f.get('classification') == 'False')
    
    print(f"\nStatistics:")
    print(f"  - True facts: {true_facts}")
    print(f"  - False facts: {false_facts}")
    print(f"  - Misleading/Other: {len(fact_checker.knowledge_base.get('facts', [])) - true_facts - false_facts}")

if __name__ == "__main__":
    train_all_facts()
    print("\n🎉 Fact-checker is now trained and ready to use!")
    print("Try testing with: 'Water boils at 100°C at sea level'")

