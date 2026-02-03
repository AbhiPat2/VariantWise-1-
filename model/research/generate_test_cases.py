"""
Generate 100 diverse test cases for benchmarking
Each test case includes:
- User persona
- Preferences (budget, fuel, body type, etc.)
- 3 relevant questions for RAG evaluation
"""

import json
import random
from datetime import datetime

# Diverse user personas
PERSONAS = [
    "Budget-conscious first-time buyer",
    "Safety-focused family person",
    "Performance enthusiast",
    "Eco-conscious buyer",
    "Luxury comfort seeker",
    "Practical daily commuter",
    "Tech-savvy millennial",
    "Senior citizen looking for comfort",
    "Young professional",
    "Adventure/off-road enthusiast",
    "City driver with parking concerns",
    "Long-distance highway driver",
    "Business executive",
    "College student on tight budget",
    "Growing family with kids",
    "Retired couple",
    "Ride-sharing driver",
    "Weekend road-tripper",
    "Status-conscious buyer",
    "Resale value focused buyer"
]

# Budget ranges (in lakhs)
BUDGET_RANGES = [
    (5, 8),    # Entry level
    (8, 12),   # Mid range
    (12, 18),  # Premium
    (18, 25),  # Luxury
    (25, 40),  # High-end luxury
    (6, 10),   # Compact premium
    (10, 15),  # Popular range
    (15, 20),  # Upper mid
    (7, 14),   # Wide range
    (20, 30),  # Premium luxury
]

FUEL_TYPES = ["Any", "Petrol", "Diesel", "Electric", "CNG", "Hybrid"]
BODY_TYPES = ["Any", "SUV", "Sedan", "Hatchback", "MUV", "Crossover"]
TRANSMISSIONS = ["Any", "Manual", "Automatic"]
SEATING = [5, 7, 8]

# Feature combinations based on persona
# Must match frontend options: Sunroof, Apple CarPlay/Android Auto, Automatic Climate Control, 
# 360 Camera, Lane Assist, Ventilated Seats, Wireless Charging
FEATURE_SETS = {
    "safety": ["Lane Assist", "360 Camera"],
    "tech": ["Apple CarPlay/Android Auto", "Wireless Charging", "360 Camera"],
    "comfort": ["Sunroof", "Ventilated Seats", "Automatic Climate Control"],
    "performance": ["Apple CarPlay/Android Auto", "Lane Assist"],
    "economy": ["Apple CarPlay/Android Auto", "Automatic Climate Control"],
    "luxury": ["Sunroof", "Ventilated Seats", "Automatic Climate Control", "Wireless Charging", "360 Camera"],
    "practical": ["Apple CarPlay/Android Auto", "360 Camera", "Automatic Climate Control"]
}

# Question templates
QUESTION_TEMPLATES = {
    "safety": [
        "Which car has the best safety features?",
        "Tell me about the safety ratings of these cars",
        "How many airbags do these cars have?",
        "Which one is safest for family?",
        "What safety features are included?"
    ],
    "price": [
        "Which car offers best value for money?",
        "What is the price difference between these options?",
        "Which is the most affordable option?",
        "Are there any hidden costs I should know?",
        "Which has the best resale value?"
    ],
    "mileage": [
        "Which car has the best fuel efficiency?",
        "What is the mileage of these cars?",
        "How much will I spend on fuel monthly?",
        "Compare the fuel economy of these options",
        "Which is most economical to run?"
    ],
    "features": [
        "What features do these cars offer?",
        "Which car has the most technology features?",
        "Tell me about the infotainment system",
        "Do these cars have Apple CarPlay?",
        "What comfort features are available?"
    ],
    "performance": [
        "Which car has the best performance?",
        "How is the engine power comparison?",
        "Which one accelerates faster?",
        "Tell me about the driving experience",
        "What is the top speed?"
    ],
    "comfort": [
        "Which car is most comfortable for long drives?",
        "How is the rear seat comfort?",
        "Tell me about the suspension quality",
        "Which has the most spacious interior?",
        "What about the ride quality?"
    ],
    "comparison": [
        "What are the main differences between these cars?",
        "Which car should I choose and why?",
        "How do these cars compare overall?",
        "What are the pros and cons of each?",
        "Why is one car ranked higher than others?"
    ],
    "maintenance": [
        "What are the maintenance costs?",
        "How reliable are these cars?",
        "Which has the lowest service cost?",
        "What is the warranty coverage?",
        "Are spare parts easily available?"
    ]
}


def generate_test_case(test_id, persona, budget_range):
    """Generate a single test case"""
    
    min_budget = budget_range[0] * 100000
    max_budget = budget_range[1] * 100000
    
    # Randomly select preferences
    fuel_type = random.choice(FUEL_TYPES)
    body_type = random.choice(BODY_TYPES)
    transmission = random.choice(TRANSMISSIONS)
    seating = random.choice(SEATING)
    performance = random.randint(1, 10)
    
    # Select 2-4 features based on persona
    if "safety" in persona.lower() or "family" in persona.lower():
        feature_category = "safety"
    elif "performance" in persona.lower() or "enthusiast" in persona.lower():
        feature_category = "performance"
    elif "budget" in persona.lower() or "economical" in persona.lower():
        feature_category = "economy"
    elif "luxury" in persona.lower() or "executive" in persona.lower():
        feature_category = "luxury"
    elif "tech" in persona.lower() or "millennial" in persona.lower():
        feature_category = "tech"
    elif "comfort" in persona.lower():
        feature_category = "comfort"
    else:
        feature_category = random.choice(list(FEATURE_SETS.keys()))
    
    features = random.sample(FEATURE_SETS[feature_category], k=min(random.randint(1, 3), len(FEATURE_SETS[feature_category])))
    
    # Generate 3 relevant questions
    # Question 1: Related to main preference
    # Question 2: Comparison or general
    # Question 3: Specific feature or concern
    
    question_categories = list(QUESTION_TEMPLATES.keys())
    questions = []
    
    # First question based on persona
    if "safety" in persona.lower():
        q1_category = "safety"
    elif "budget" in persona.lower():
        q1_category = "price"
    elif "performance" in persona.lower():
        q1_category = "performance"
    elif "comfort" in persona.lower():
        q1_category = "comfort"
    else:
        q1_category = random.choice(["comparison", "features", "mileage"])
    
    questions.append(random.choice(QUESTION_TEMPLATES[q1_category]))
    
    # Second question - comparison
    questions.append(random.choice(QUESTION_TEMPLATES["comparison"]))
    
    # Third question - another relevant category
    remaining_categories = [c for c in question_categories if c not in [q1_category, "comparison"]]
    q3_category = random.choice(remaining_categories)
    questions.append(random.choice(QUESTION_TEMPLATES[q3_category]))
    
    return {
        "id": test_id,
        "persona": persona,
        "preferences": {
            "min_budget": min_budget,
            "max_budget": max_budget,
            "fuel_type": fuel_type,
            "body_type": body_type,
            "transmission": transmission,
            "seating": seating,
            "features": features,
            "performance": performance
        },
        "questions": questions
    }


def generate_all_test_cases(num_cases=100):
    """Generate all test cases"""
    
    test_cases = []
    
    for i in range(num_cases):
        persona = random.choice(PERSONAS)
        budget_range = random.choice(BUDGET_RANGES)
        
        test_case = generate_test_case(i + 1, persona, budget_range)
        test_cases.append(test_case)
    
    return {
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "num_test_cases": num_cases,
            "total_questions": num_cases * 3,
            "version": "1.0"
        },
        "test_cases": test_cases
    }


if __name__ == "__main__":
    print("🔄 Generating 100 test cases...")
    
    data = generate_all_test_cases(100)
    
    # Save to file
    output_file = "test_data/test_cases.json"
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"✅ Generated {len(data['test_cases'])} test cases")
    print(f"✅ Total questions: {data['metadata']['total_questions']}")
    print(f"✅ Saved to: {output_file}")
    print("\n📊 Sample test case:")
    print(json.dumps(data['test_cases'][0], indent=2))
