from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
import time
from evaluation_utils import calculate_recommendation_quality, calculate_answer_quality

app = Flask(__name__)

# Configure CORS to allow requests from both localhost:3000 and localhost:3001
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000", "http://localhost:3001"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Load the dataset
df = pd.read_csv('../data/final_dataset.csv')

# Initialize the model for embeddings
model = SentenceTransformer('all-MiniLM-L6-v2')

# Precompute embeddings for all cars
print("Precomputing embeddings for all cars...")
car_texts = []
for idx, row in df.iterrows():
    text = f"{row['Brand']} {row['Model']} {row['Variant']} {row['Fuel Type']} {row['Body Type']}"
    car_texts.append(text)
df['embedding'] = list(model.encode(car_texts))
print("Embeddings precomputed!")

def create_user_query(preferences):
    """Create a text query from user preferences"""
    query_parts = []
    
    if preferences.get('fuelType') and preferences['fuelType'] != 'Any':
        query_parts.append(preferences['fuelType'])
    
    if preferences.get('bodyType') and preferences['bodyType'] != 'Any':
        query_parts.append(preferences['bodyType'])
    
    if preferences.get('transmission') and preferences['transmission'] != 'Any':
        query_parts.append(preferences['transmission'])
    
    if preferences.get('seatingCapacity'):
        query_parts.append(f"{preferences['seatingCapacity']} seater")
    
    if preferences.get('features'):
        query_parts.extend(preferences['features'])
    
    return ' '.join(query_parts)

def calculate_relevance_score(car, preferences):
    """Calculate how well a car matches user preferences"""
        score = 0
    total_weight = 0
    
    # Budget match (weight: 0.3)
    budget_weight = 0.3
    min_budget = preferences.get('minBudget', 0)
    max_budget = preferences.get('maxBudget', float('inf'))
    
    if pd.notna(car.get('Ex-Showroom Price')):
        price = car['Ex-Showroom Price']
        if min_budget <= price <= max_budget:
            score += budget_weight * 1.0
        elif price < min_budget and price >= min_budget * 0.9:
            score += budget_weight * 0.8
        elif price > max_budget and price <= max_budget * 1.1:
            score += budget_weight * 0.8
        total_weight += budget_weight
    
    # Fuel type match (weight: 0.2)
    fuel_weight = 0.2
    if preferences.get('fuelType') and preferences['fuelType'] != 'Any':
        if pd.notna(car.get('Fuel Type')):
            if car['Fuel Type'] == preferences['fuelType']:
                score += fuel_weight * 1.0
            elif preferences['fuelType'] == 'Any':
                score += fuel_weight * 0.8
            total_weight += fuel_weight
    
    # Body type match (weight: 0.2)
    body_weight = 0.2
    if preferences.get('bodyType') and preferences['bodyType'] != 'Any':
        if pd.notna(car.get('Body Type')):
            if car['Body Type'] == preferences['bodyType']:
                score += body_weight * 1.0
            elif preferences['bodyType'] == 'Any':
                score += body_weight * 0.8
            total_weight += body_weight
    
    # Transmission match (weight: 0.1)
    trans_weight = 0.1
    if preferences.get('transmission') and preferences['transmission'] != 'Any':
        if pd.notna(car.get('Transmission')):
            if car['Transmission'] == preferences['transmission']:
                score += trans_weight * 1.0
            elif preferences['transmission'] == 'Any':
                score += trans_weight * 0.9
            total_weight += trans_weight
    
    # Seating capacity match (weight: 0.1)
    seat_weight = 0.1
    if preferences.get('seatingCapacity'):
        if pd.notna(car.get('Seating Capacity')):
            if car['Seating Capacity'] == preferences['seatingCapacity']:
                score += seat_weight * 1.0
            elif car['Seating Capacity'] > preferences['seatingCapacity']:
                score += seat_weight * 0.5
            total_weight += seat_weight
    
    # Features match (weight: 0.1)
    feature_weight = 0.1
    if preferences.get('features') and len(preferences['features']) > 0:
        car_features_str = str(car.get('Features', '')).lower()
        if car_features_str and car_features_str != 'nan':
            matched_features = sum(1 for f in preferences['features'] if f.lower() in car_features_str)
            if len(preferences['features']) > 0:
                score += feature_weight * (matched_features / len(preferences['features']))
        total_weight += feature_weight
    
    return score / total_weight if total_weight > 0 else 0

@app.route('/api/recommend', methods=['POST', 'OPTIONS'])
def recommend():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        start_time = time.time()
        data = request.json

        # Extract preferences
        prefs = {
            'minBudget': data.get('minBudget', 0),
            'maxBudget': data.get('maxBudget', 10000000),
            'fuelType': data.get('fuelType', 'Any'),
            'bodyType': data.get('bodyType', 'Any'),
            'transmission': data.get('transmission', 'Any'),
            'seatingCapacity': data.get('seatingCapacity'),
            'features': data.get('features', [])
        }
        
        # Filter by budget first
        filtered_df = df[
            (df['Ex-Showroom Price'] >= prefs['minBudget'] * 0.9) & 
            (df['Ex-Showroom Price'] <= prefs['maxBudget'] * 1.1)
        ].copy()
        
        if len(filtered_df) == 0:
            return jsonify({
                'success': False,
                'error': 'No cars found in the specified budget range'
            }), 404
        
        # Create query and get embedding
        query = create_user_query(prefs)
        query_embedding = model.encode(query)
        
        # Calculate semantic similarity
        filtered_df['semantic_score'] = filtered_df['embedding'].apply(
            lambda x: np.dot(query_embedding, x) / (np.linalg.norm(query_embedding) * np.linalg.norm(x))
        )
        
        # Calculate relevance scores
        filtered_df['relevance_score'] = filtered_df.apply(
            lambda row: calculate_relevance_score(row, prefs), axis=1
        )
        
        # Combined score (70% relevance, 30% semantic)
        filtered_df['combined_score'] = (
            0.7 * filtered_df['relevance_score'] + 
            0.3 * filtered_df['semantic_score']
        )
        
        # Get top matches
        top_matches = filtered_df.nlargest(10, 'combined_score')
        
        # Convert to serializable format
        top_matches_serializable = []
        for idx, row in top_matches.iterrows():
            car_dict = row.to_dict()
            # Remove embedding from response
            if 'embedding' in car_dict:
                del car_dict['embedding']
            # Convert numpy types to Python types
            for key, value in car_dict.items():
                if isinstance(value, (np.integer, np.floating)):
                    car_dict[key] = float(value)
                elif pd.isna(value):
                    car_dict[key] = None
            top_matches_serializable.append(car_dict)
        
        response_time = time.time() - start_time
        
        # Calculate quality metrics with advanced evaluation enabled
        # Set use_advanced=True to enable DeepEval/RAGAS (slower but more comprehensive)
        quality_metrics = calculate_recommendation_quality(
            top_matches_serializable[:5],
            prefs,
            response_time,
            use_llm_judge=True,
            use_advanced=True  # Enable DeepEval/RAGAS
        )
        
        return jsonify({
            'success': True,
            'recommendations': top_matches_serializable,
            'metrics': quality_metrics,
            'response_time': response_time
        })

    except Exception as e:
        print(f"Error in recommend: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/ask', methods=['POST', 'OPTIONS'])
def ask():
    if request.method == 'OPTIONS':
        return '', 200

    try:
        data = request.json
        question = data.get('question', '')
        context = data.get('context', [])

        if not question:
            return jsonify({
                'success': False,
                'error': 'Question is required'
            }), 400
        
        # Simple Q&A based on context
        if context and len(context) > 0:
            # Use the first car in context as reference
            car = context[0]
            
            # Generate answer based on question keywords
            question_lower = question.lower()
            
            if 'price' in question_lower or 'cost' in question_lower or 'expensive' in question_lower:
                price = car.get('Ex-Showroom Price', 'N/A')
                answer = f"The {car['Brand']} {car['Model']} {car['Variant']} is priced at ₹{price:,.0f} (ex-showroom)."
            
            elif 'mileage' in question_lower or 'fuel efficiency' in question_lower:
                mileage = car.get('Mileage', 'N/A')
                answer = f"The {car['Brand']} {car['Model']} offers a mileage of {mileage}."
            
            elif 'feature' in question_lower or 'features' in question_lower:
                features = car.get('Features', 'N/A')
                answer = f"The {car['Brand']} {car['Model']} {car['Variant']} comes with the following features: {features}"
            
            elif 'engine' in question_lower or 'power' in question_lower:
                engine = car.get('Engine', 'N/A')
                power = car.get('Power', 'N/A')
                answer = f"The {car['Brand']} {car['Model']} is powered by a {engine} engine that produces {power} of power."
            
            elif 'fuel' in question_lower or 'petrol' in question_lower or 'diesel' in question_lower:
                fuel = car.get('Fuel Type', 'N/A')
                answer = f"The {car['Brand']} {car['Model']} {car['Variant']} runs on {fuel}."
            
            elif 'compare' in question_lower or 'difference' in question_lower:
                if len(context) >= 2:
                    car1 = context[0]
                    car2 = context[1]
                    answer = f"Comparing {car1['Brand']} {car1['Model']} and {car2['Brand']} {car2['Model']}: "
                    answer += f"The {car1['Brand']} {car1['Model']} is priced at ₹{car1.get('Ex-Showroom Price', 'N/A'):,.0f} "
                    answer += f"while the {car2['Brand']} {car2['Model']} costs ₹{car2.get('Ex-Showroom Price', 'N/A'):,.0f}. "
                else:
                    answer = f"I can provide details about the {car['Brand']} {car['Model']}. To compare, please provide another car."
            
            else:
                # Generic answer
                answer = f"The {car['Brand']} {car['Model']} {car['Variant']} is a {car.get('Body Type', 'N/A')} "
                answer += f"with {car.get('Fuel Type', 'N/A')} fuel type, priced at ₹{car.get('Ex-Showroom Price', 'N/A'):,.0f}."
        else:
            answer = "I need some context (recommended cars) to answer your question accurately."
        
        # Prepare context for evaluation
        context_str = ""
        if context and len(context) > 0:
            for i, car in enumerate(context[:3]):  # Use top 3 cars as context
                context_str += f"\nCar {i+1}: {car.get('Brand', '')} {car.get('Model', '')} {car.get('Variant', '')} "
                context_str += f"- Price: ₹{car.get('Ex-Showroom Price', 'N/A')}, "
                context_str += f"Fuel: {car.get('Fuel Type', 'N/A')}, "
                context_str += f"Mileage: {car.get('Mileage', 'N/A')}, "
                context_str += f"Features: {car.get('Features', 'N/A')}\n"
        
        # Calculate answer quality with advanced evaluation enabled
        # Set use_advanced=True to enable DeepEval/RAGAS (slower but more comprehensive)
        answer_quality = calculate_answer_quality(
            answer, 
            context_str,
            use_llm_judge=True,
            use_advanced=True  # Enable DeepEval/RAGAS
        )
        
        return jsonify({
            'success': True,
            'answer': answer,
            'metrics': answer_quality
        })

    except Exception as e:
        print(f"Error in ask: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'message': 'Model server is running'})

if __name__ == '__main__':
    print("Starting Flask server on port 5001...")
    app.run(host='0.0.0.0', port=5001, debug=True)
