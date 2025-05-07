import pandas as pd
import numpy as np
import os
import re
import difflib
from flask import Flask, request, jsonify
from flask_cors import CORS
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import boto3
from langchain_community.chat_models import BedrockChat
import traceback
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve values from the environment
aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
aws_region = os.getenv("AWS_REGION")

app = Flask(__name__)
# Be more specific for security
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})

# === Constants ===
DATA_FILE = "../data/final_dataset.csv"
REVIEWS_DIR = "../data/reviews"

# === Enhanced Preference Structure ===
preference_config = {
    "budget": {
        "type": "range",
        "min_label": "Minimum budget (₹)",
        "max_label": "Maximum budget (₹)",
        "min_value": 100000,
        "max_value": 10000000,
        "weight": 10
    },
    "fuel_type": {
        "type": "select",
        "label": "Preferred fuel type",
        "options": ["Any", "Petrol", "Diesel", "Electric", "CNG", "Hybrid"],
        "weight": 8
    },
    "body_type": {
        "type": "select",
        "label": "Preferred body style",
        "options": ["Any", "SUV", "Sedan", "Hatchback", "MUV", "Crossover"],
        "weight": 7
    },
    "transmission": {
        "type": "select",
        "label": "Transmission preference",
        "options": ["Any", "Manual", "Automatic", "CVT", "DCT", "AMT"],
        "weight": 6
    },
    "seating": {
        "type": "slider",
        "label": "Minimum seats required",
        "min": 2,
        "max": 9,
        "weight": 5
    },
    "features": {
        "type": "multiselect",
        "label": "Must-have features",
        "options": ["Sunroof", "Apple CarPlay/Android Auto", "Automatic Climate Control",
                    "360 Camera", "Lane Assist", "Ventilated Seats", "Wireless Charging"],
        "weight": 3
    },
    "performance": {
        "type": "slider",
        "label": "Performance importance (1-10)",
        "min": 1,
        "max": 10,
        "weight": 4
    }
}

# === Helper Functions ===


def load_models():
    """Loads the Sentence Transformer model and initializes the Bedrock LLM client."""
    try:
        print("Loading Sentence Transformer model...")
        embedding_model = SentenceTransformer("msmarco-distilbert-base-v4")
        print("Sentence Transformer model loaded.")

        print("Initializing Bedrock client...")
        # Initialize the Bedrock client using the environment variables
        if not aws_access_key_id or not aws_secret_access_key:
            raise ValueError(
                "AWS Access Key ID or Secret Access Key not found in environment variables.")

        bedrock_client = boto3.client(
            "bedrock-runtime",
            region_name=aws_region,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key
            # aws_session_token=aws_session_token # Uncomment this line ONLY if using temporary credentials
        )
        print("Bedrock client initialized.")

        print("Initializing BedrockChat model...")
        llm = BedrockChat(
            model_id="mistral.mixtral-8x7b-instruct-v0:1",
            client=bedrock_client,  # Use the client created with credentials
            model_kwargs={"max_tokens": 1024, "temperature": 0.4}
        )
        print("BedrockChat model initialized.")
        return embedding_model, llm

    except ValueError as ve:  # Catch specific credential errors
        print(f"Configuration Error loading models: {ve}")
        print("Please ensure AWS credentials are set correctly.")
        return None, None
    except Exception as e:
        print(f"\n--- ERROR Loading Models ---")
        print(f"Error type: {type(e)}")
        print(f"Error message: {str(e)}")
        # Check specifically for common boto3/Bedrock errors
        if "UnrecognizedClientException" in str(e) or "AccessDeniedException" in str(e):
            print("Hint: Check if AWS credentials are correct, active, and have Bedrock permissions in ap-south-1.")
            print("Hint: Ensure you have requested and received access to the Mistral model in the Bedrock console (ap-south-1).")
        print(f"Traceback:\n{traceback.format_exc()}")
        return None, None


def load_car_data():
    try:
        df = pd.read_csv(DATA_FILE)
        df['numeric_price'] = df['price'].str.replace(
            r"[^\d]", "", regex=True).replace("", np.nan).astype(float)
        return df.fillna("N/A")
    except Exception as e:
        print(f"Error loading car data: {e}")
        return pd.DataFrame()


def generate_car_summary(row):
    features = []
    feature_map = {
        'Sunroof': ['sunroof', 'panoramic'],
        'Apple CarPlay/Android Auto': ['carplay', 'android auto'],
        'Automatic Climate Control': ['climate control'],
        '360 Camera': ['360', 'surround view'],
        'Lane Assist': ['lane assist', 'lane keep'],
        'Ventilated Seats': ['ventilated'],
        'Wireless Charging': ['wireless charging']
    }

    # Ensure 'row' is a Pandas Series for consistent access
    if not isinstance(row, pd.Series):
        row = pd.Series(row)  # Convert if it's a dict (e.g., from JSON)

    for feat, keywords in feature_map.items():
        # Access .values attribute, not call it as a function
        if any(any(kw in str(v).lower() for v in row.values) for kw in keywords):
            features.append(feat)

    # Extract numeric values from string fields
    try:
        power = int(re.findall(r'\d+', str(row.get('Max Power', '')))[0])
    except:
        power = 0  # Default if extraction fails

    comfort_scores = [
        row.get('front_seat_comfort_score', 0),
        row.get('rear_seat_comfort_score', 0),
        row.get('bump_absorption_score', 0),
        row.get('material_quality_score', 0)
    ]
    # Filter out non-numeric scores before calculating mean
    numeric_comfort_scores = [
        s for s in comfort_scores if isinstance(s, (int, float))]
    comfort = round(np.mean(numeric_comfort_scores),
                    2) if numeric_comfort_scores else 0

    # Use .get() for potentially missing columns to avoid KeyErrors
    return (
        f"{row.get('variant', 'N/A')} | {row.get('price', 'N/A')} | {row.get('Fuel Type', 'N/A')} | "
        f"{row.get('Body Type', 'N/A')} | {row.get('Transmission Type', 'N/A')} | "
        f"Seats: {row.get('Seating Capacity', 'N/A')} | "
        # Handle empty features
        f"Power: {power}bhp | Features: {', '.join(features) if features else 'None'} | "
        f"Comfort Score: {comfort}/5"
    )


def generate_user_summary(prefs):
    features = prefs.get('features', [])
    return (
        f"Budget: ₹{prefs['budget'][0]:,}-₹{prefs['budget'][1]:,} | "
        f"Fuel: {prefs['fuel_type']} | Body: {prefs['body_type']} | "
        f"Transmission: {prefs['transmission']} | Seats: {prefs['seating']}+ | "
        f"Features: {', '.join(features) if features else 'None'} | "
        f"Performance Priority: {prefs['performance']}/10"
    )

# === Core Matching Logic ===


def enhanced_matching(cars_df, prefs):
    results = []

    for _, car in cars_df.iterrows():
        score = 0
        details = {}

        # Price matching
        price = car.get('numeric_price')
        if pd.notna(price):
            min_p, max_p = prefs['budget']
            if min_p <= price <= max_p:
                score += 10
                details['price'] = "Within budget"
            elif price <= max_p * 1.2:
                score += 5
                details['price'] = "Slightly over budget"

        # Fuel type
        if prefs['fuel_type'] != 'Any' and car['Fuel Type'].lower() == prefs['fuel_type'].lower():
            score += 8
            details['fuel'] = "Exact match"

        # Body type
        if prefs['body_type'] != 'Any' and car['Body Type'].lower() == prefs['body_type'].lower():
            score += 7
            details['body'] = "Exact match"

        # Transmission
        if prefs['transmission'] != 'Any' and car['Transmission Type'].lower() == prefs['transmission'].lower():
            score += 6
            details['transmission'] = "Exact match"

        # Seating capacity
        try:
            if int(car['Seating Capacity']) >= prefs['seating']:
                score += 5
                details['seating'] = "Meets requirement"
        except:
            pass

        # Feature matching
        matched_features = []
        for feat in prefs.get('features', []):
            if any(feat.lower() in str(v).lower() for v in car.values):
                matched_features.append(feat)
                score += 3
        if matched_features:
            details['features'] = f"Matched: {', '.join(matched_features)}"

        # Performance consideration
        if prefs['performance'] > 5:
            try:
                power = int(re.findall(
                    r'\d+', str(car.get('Max Power', '')))[0])
                if power > 100:
                    score += int(prefs['performance'] * 0.4)
                    details['performance'] = f"Power: {power}bhp"
            except:
                pass

        results.append({
            'car': car,
            'score': score,
            'details': details
        })

    return sorted(results, key=lambda x: x['score'], reverse=True)

# === Review Processing ===


def load_reviews(top_cars):
    reviews = {}
    for car in top_cars:
        variant = car['variant']
        closest_match = difflib.get_close_matches(
            variant,
            [f[:-4] for f in os.listdir(REVIEWS_DIR)],
            n=1,
            cutoff=0.6
        )
        if closest_match:
            try:
                # Added encoding
                with open(os.path.join(REVIEWS_DIR, f"{closest_match[0]}.txt"), 'r', encoding='utf-8') as f:
                    reviews[variant] = f.read()
            except FileNotFoundError:
                print(f"Review file not found for {closest_match[0]}")
            except Exception as e:
                print(f"Error reading review file {closest_match[0]}.txt: {e}")
    return reviews


# Global variables to store models and data
embedding_model, llm = None, None
df = None
car_matches = {}
car_reviews = {}

# Load models and data at startup
# @app.before_first_request # This decorator is deprecated


def initialize():
    global embedding_model, llm, df
    print("Initializing models and data...")  # Added print statement
    embedding_model, llm = load_models()
    df = load_car_data()
    if embedding_model and llm and not df.empty:
        print("Initialization complete.")
    else:
        print("Initialization failed.")

# === API Endpoints ===


@app.route('/api/recommend', methods=['POST'])
def recommend_cars():
    global df, embedding_model  # Ensure globals are accessible
    if df is None or embedding_model is None:
        return jsonify({'error': 'Server not initialized properly. Please wait or check logs.'}), 503

    try:
        # Get user preferences from request
        data = request.json

        # Validate required fields
        required_fields = ['min_budget', 'max_budget', 'fuel_type', 'body_type',
                           'transmission', 'seating', 'features', 'performance']

        for field in required_fields:
            if field not in data:
                # Check for potential variations like 'budget' instead of min/max
                if field == 'min_budget' and 'budget' in data and isinstance(data['budget'], list) and len(data['budget']) == 2:
                    continue  # Skip if 'budget' array exists
                elif field == 'max_budget' and 'budget' in data and isinstance(data['budget'], list) and len(data['budget']) == 2:
                    continue  # Skip if 'budget' array exists
                else:
                    return jsonify({'error': f'Missing required field: {field}'}), 400

        # Format preferences for processing
        # Handle both ['min_budget', 'max_budget'] and ['budget'][0], ['budget'][1]
        min_budget = int(data.get('min_budget', data.get('budget', [0, 0])[0]))
        max_budget = int(data.get('max_budget', data.get('budget', [0, 0])[1]))

        prefs = {
            'budget': (min_budget, max_budget),
            'fuel_type': data['fuel_type'],
            'body_type': data['body_type'],
            'transmission': data['transmission'],
            'seating': int(data['seating']),  # Ensure seating is int
            'features': data.get('features', []),  # Use get with default
            # Ensure performance is int
            'performance': int(data['performance'])
        }

        # First stage filtering
        filtered = df[
            (df['numeric_price'] >= prefs['budget'][0]) &
            # Allow slightly over budget
            (df['numeric_price'] <= prefs['budget'][1] * 1.2)
        ].copy()  # Use copy to avoid SettingWithCopyWarning

        if filtered.empty:
            return jsonify({'session_id': 'N/A', 'matches': [], 'reviews': {}})

        # Enhanced matching
        ranked_cars = enhanced_matching(filtered, prefs)

        # Semantic reranking
        user_summary = generate_user_summary(prefs)
        # Pass the Pandas Series directly from the ranked_cars list
        car_summaries = [generate_car_summary(
            car_match['car']) for car_match in ranked_cars[:20]]  # Limit to top 20 for embedding

        if not car_summaries:
            return jsonify({'session_id': 'N/A', 'matches': [], 'reviews': {}})

        user_embed = embedding_model.encode([user_summary])
        car_embeds = embedding_model.encode(car_summaries)

        similarities = cosine_similarity(user_embed, car_embeds)[0]
        # Use car_match consistently
        for i, car_match in enumerate(ranked_cars[:20]):
            car_match['semantic_score'] = float(
                similarities[i])  # Ensure float
            car_match['combined_score'] = car_match['score'] * 0.7 + \
                similarities[i] * 100 * 0.3  # Adjust weighting if needed

        # Get top 10 matches
        top_matches = sorted(
            ranked_cars[:20],
            key=lambda x: x['combined_score'],
            reverse=True
        )[:10]

        # Convert car objects to dictionaries
        top_matches_serializable = []
        for car_match in top_matches:
            # Convert numpy types to standard Python types for JSON serialization
            # Ensure car_match['car'] is a Series before calling .astype
            car_series = car_match['car'] if isinstance(
                car_match['car'], pd.Series) else pd.Series(car_match['car'])
            car_dict = car_series.astype(object).where(
                pd.notnull(car_series), None).to_dict()
            top_matches_serializable.append({
                'car': car_dict,
                'score': float(car_match['score']),  # Ensure float
                # Ensure float
                'semantic_score': float(car_match['semantic_score']),
                # Ensure float
                'combined_score': float(car_match['combined_score']),
                'details': car_match['details']
            })

        # Store matches in session (using a simple dict for now)
        session_id = data.get('session_id', str(hash(user_summary)))
        # Store serializable version
        car_matches[session_id] = top_matches_serializable

        # Load reviews using the car dictionary from the serializable list
        reviews = load_reviews([m['car'] for m in top_matches_serializable])
        car_reviews[session_id] = reviews

        # Return top 5 for display
        return jsonify({
            'session_id': session_id,
            # Return serializable version
            'matches': top_matches_serializable[:5],
            'reviews': reviews
        })

    except Exception as e:
        import traceback
        print(f"Error in recommendation: {str(e)}")
        print(traceback.format_exc())  # Print full traceback
        return jsonify({'error': f'An internal error occurred: {str(e)}'}), 500


@app.route('/api/ask', methods=['POST'])
def ask_question():
    global llm, car_matches, car_reviews  # Ensure globals are accessible
    if llm is None:
        return jsonify({'error': 'LLM not initialized properly. Please wait or check logs.'}), 503

    try:
        data = request.json
        question = data.get('question')
        session_id = data.get('session_id')

        if not question:
            return jsonify({'error': 'No question provided'}), 400

        if not session_id or session_id not in car_matches:
            return jsonify({'error': 'Invalid or expired session'}), 400

        matches = car_matches[session_id]
        reviews = car_reviews.get(session_id, {})  # Use get with default

        # Build context for the LLM
        context = "Cars:\n" + "\n".join([
            # Pass the car dictionary directly to generate_car_summary
            f"{car['car'].get('variant', 'N/A')} - {generate_car_summary(car['car'])}"
            for car in matches
        ])
        if reviews:
            context += "\n\nReviews:\n" + "\n\n".join(
                [f"{k}:\n{v}" for k, v in reviews.items()]
            )

        prompt = f"""You are a car expert assistant. Use this context to answer the user's question concisely. If the context doesn't contain the answer, say you don't have enough information.

        Context:
        {context}

        Question: {question}

        Answer:"""

        response = llm.invoke(prompt)
        return jsonify({'answer': response.content})

    except Exception as e:
        import traceback
        print(f"Error in question answering: {str(e)}")
        print(traceback.format_exc())  # Print full traceback
        return jsonify({'error': f'An internal error occurred: {str(e)}'}), 500

# For testing the API is working


@app.route('/health', methods=['GET'])
def health_check():
    global llm, df  # Ensure globals are accessible
    return jsonify({'status': 'ok', 'initialized': llm is not None and df is not None})


if __name__ == '__main__':
    initialize()  # Call initialize directly before running the app
    app.run(host='0.0.0.0', port=5000)
