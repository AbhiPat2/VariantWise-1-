"""
Quick test to verify everything is working WITHOUT the slow DeepEval/RAGAS
"""
import requests
import json
import time

API_URL = "http://localhost:5001"

print("="*60)
print("QUICK TEST - Fast evaluation only")
print("="*60)

# Test 1: Recommendations
print("\n1️⃣ Testing Recommendations...")
start = time.time()

response = requests.post(f"{API_URL}/api/recommend", json={
    "min_budget": 500000,
    "max_budget": 1000000,
    "fuel_type": "Petrol",
    "body_type": "SUV",
    "transmission": "Automatic",
    "seating": 5,
    "features": ["Sunroof", "Leather Seats"],
    "performance": 7
}, timeout=30)

rec_time = time.time() - start

if response.status_code == 200:
    data = response.json()
    print(f"✅ Got {len(data['matches'])} recommendations ({rec_time:.2f}s)")
    print(f"Session ID: {data['session_id']}")
    
    metrics = data.get('quality_metrics', {})
    print(f"\n📊 Metrics:")
    print(f"   Overall Quality: {metrics.get('overall_quality', 'N/A')}")
    print(f"   LLM Judge: {metrics.get('llm_overall', 'N/A')}")
    print(f"   NDCG: {metrics.get('advanced_ndcg', 'N/A')}")
    print(f"   ILD: {metrics.get('advanced_ild', 'N/A')}")
    
    session_id = data['session_id']
    
    # Test 2: Q&A (this is the slow part!)
    print(f"\n2️⃣ Testing Q&A...")
    qa_start = time.time()
    
    qa_response = requests.post(f"{API_URL}/api/ask", json={
        "question": "What are the key differences between these cars?",
        "session_id": session_id
    }, timeout=60)
    
    qa_time = time.time() - qa_start
    
    if qa_response.status_code == 200:
        qa_data = qa_response.json()
        print(f"✅ Got answer ({qa_time:.2f}s)")
        print(f"\nAnswer: {qa_data['answer'][:150]}...")
        
        qa_metrics = qa_data.get('quality_metrics', {})
        print(f"\n📊 Q&A Metrics:")
        print(f"   Overall: {qa_metrics.get('overall_quality', 'N/A')}")
        print(f"   LLM Judge: {qa_metrics.get('llm_overall', 'N/A')}")
        
        # Check if DeepEval ran (the slow part)
        if 'deepeval_overall' in qa_metrics:
            print(f"   ⚠️  DeepEval: {qa_metrics['deepeval_overall']} (SLOW!)")
        else:
            print(f"   ✅ DeepEval: SKIPPED (fast!)")
            
        if 'ragas_overall' in qa_metrics:
            print(f"   ⚠️  RAGAS: {qa_metrics['ragas_overall']} (SLOW!)")
        else:
            print(f"   ✅ RAGAS: SKIPPED (fast!)")
    else:
        print(f"❌ Q&A Failed: {qa_response.status_code}")
        
else:
    print(f"❌ Recommendations Failed: {response.status_code}")

print(f"\n{'='*60}")
print(f"Total time: {time.time() - start:.2f}s")
print(f"{'='*60}")
