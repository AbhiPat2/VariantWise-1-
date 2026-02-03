"""
Run comprehensive benchmark evaluation
Tests both recommendation system and RAG chatbot
"""

import json
import requests
import time
from datetime import datetime
from typing import Dict, List
import sys

API_BASE_URL = "http://localhost:5001"


def run_single_test(test_case: Dict) -> Dict:
    """
    Run a single test case
    Returns results for both recommendations and Q&A
    """
    test_id = test_case["id"]
    persona = test_case["persona"]
    preferences = test_case["preferences"]
    questions = test_case["questions"]
    
    print(f"\n{'='*60}")
    print(f"TEST: Test Case #{test_id}: {persona}")
    print(f"{'='*60}")
    
    # Display user preferences in one line
    pref_summary = f"Budget: ₹{preferences.get('min_budget', 0):,}-₹{preferences.get('max_budget', 0):,} | " \
                   f"Fuel: {preferences.get('fuel_type', 'Any')} | " \
                   f"Body: {preferences.get('body_type', 'Any')} | " \
                   f"Trans: {preferences.get('transmission', 'Any')} | " \
                   f"Seats: {preferences.get('seating', 'Any')}"
    if preferences.get('features'):
        pref_summary += f" | Features: {', '.join(preferences['features'][:3])}"
        if len(preferences['features']) > 3:
            pref_summary += f" (+{len(preferences['features'])-3} more)"
    print(f"PREFS: {pref_summary}")
    print()
    
    results = {
        "test_id": test_id,
        "persona": persona,
        "preferences": preferences,
        "timestamp": datetime.now().isoformat(),
        "recommendation_results": None,
        "qa_results": [],
        "errors": []
    }
    
    # Step 1: Get Recommendations
    print(f"STATS: Getting recommendations...")
    rec_start_time = time.time()
    
    try:
        # Add use_advanced flag to get NDCG, ILD, Novelty, Serendipity metrics
        prefs_with_advanced = preferences.copy()
        prefs_with_advanced['use_advanced'] = True
        
        response = requests.post(
            f"{API_BASE_URL}/api/recommend",
            json=prefs_with_advanced,
            timeout=120  # 2 minute timeout
        )
        rec_end_time = time.time()
        rec_response_time = rec_end_time - rec_start_time
        
        if response.status_code == 200:
            rec_data = response.json()
            
            recommendations = rec_data.get("matches", [])
            
            results["recommendation_results"] = {
                "success": True,
                "num_recommendations": len(recommendations),
                "recommendations": recommendations,  # Store actual recommendations
                "response_time": rec_response_time,
                "quality_metrics": rec_data.get("quality_metrics", {}),
                "session_id": rec_data.get("session_id", "")
            }
            
            session_id = rec_data.get("session_id", "")
            
            print(f"   SUCCESS: Got {len(recommendations)} recommendations")
            print(f"   TIME:  Response time: {rec_response_time:.2f}s")
            
            # Print the actual recommendations
            print(f"\n   CARS: Recommended Cars:")
            for idx, rec in enumerate(recommendations[:5], 1):  # Show top 5
                car = rec.get('car', {})
                variant = car.get('variant', 'Unknown')
                price = car.get('price', 'N/A')
                fuel = car.get('Fuel Type', 'N/A')
                transmission = car.get('Transmission', 'N/A')
                score = rec.get('score', 0)
                print(f"      {idx}. {variant}")
                print(f"         Price: {price} | Fuel: {fuel} | Trans: {transmission}")
                print(f"         Match Score: {score:.3f}")
            
            if rec_data.get("quality_metrics"):
                metrics = rec_data["quality_metrics"]
                print(f"   STATS: Overall Quality: {metrics.get('overall_quality', 'N/A')}")
                print(f"   STATS: Relevance: {metrics.get('relevance_score', 'N/A')}")
                print(f"   STATS: Diversity: {metrics.get('diversity_score', 'N/A')}")
                
                # Advanced metrics
                if metrics.get('advanced_ndcg'):
                    print(f"   STATS: NDCG@K: {metrics.get('advanced_ndcg', 'N/A'):.4f}")
                if metrics.get('advanced_ild'):
                    print(f"   STATS: ILD (Diversity): {metrics.get('advanced_ild', 'N/A'):.4f}")
                if metrics.get('advanced_novelty'):
                    print(f"   STATS: Novelty: {metrics.get('advanced_novelty', 'N/A'):.4f}")
                if metrics.get('advanced_serendipity'):
                    print(f"   STATS: Serendipity: {metrics.get('advanced_serendipity', 'N/A'):.4f}")
            
            # Step 2: Ask Questions (RAG evaluation)
            print(f"\nQ💬A: Asking {len(questions)} questions...")
            
            for q_idx, question in enumerate(questions, 1):
                print(f"\n   Q{q_idx}: {question}")
                
                qa_start_time = time.time()
                
                try:
                    qa_response = requests.post(
                        f"{API_BASE_URL}/api/ask",
                        json={
                            "question": question,
                            "session_id": session_id
                        },
                        timeout=180  # 3 minute timeout for RAG (DeepEval can be slow)
                    )
                    qa_end_time = time.time()
                    qa_response_time = qa_end_time - qa_start_time
                    
                    if qa_response.status_code == 200:
                        qa_data = qa_response.json()
                        
                        qa_result = {
                            "question": question,
                            "answer": qa_data.get("answer", ""),
                            "response_time": qa_response_time,
                            "quality_metrics": qa_data.get("quality_metrics", {}),
                            "success": True
                        }
                        
                        results["qa_results"].append(qa_result)
                        
                        print(f"      SUCCESS: Answer generated ({qa_response_time:.2f}s)")
                        
                        # Print the actual answer
                        answer_text = qa_data.get("answer", "")
                        if len(answer_text) > 300:
                            print(f"      Q💬A: Answer: {answer_text[:300]}...")
                        else:
                            print(f"      Q💬A: Answer: {answer_text}")
                        
                        if qa_data.get("quality_metrics"):
                            qa_metrics = qa_data["quality_metrics"]
                            print(f"      STATS: Overall Quality: {qa_metrics.get('overall_quality', 'N/A')}")
                            print(f"      STATS: Faithfulness: {qa_metrics.get('deepeval_faithfulness', qa_metrics.get('ragas_faithfulness', 'N/A'))}")
                            print(f"      STATS: Relevancy: {qa_metrics.get('deepeval_answer_relevancy', qa_metrics.get('ragas_answer_relevancy', 'N/A'))}")
                    
                    else:
                        error_msg = f"Q&A request failed with status {qa_response.status_code}"
                        print(f"      ERROR: {error_msg}")
                        results["errors"].append(error_msg)
                        results["qa_results"].append({
                            "question": question,
                            "success": False,
                            "error": error_msg
                        })
                    
                    # Small delay between questions to avoid rate limits
                    time.sleep(1)
                    
                except requests.exceptions.Timeout:
                    error_msg = f"Q&A request timed out for question: {question}"
                    print(f"      TIME:  {error_msg}")
                    results["errors"].append(error_msg)
                    results["qa_results"].append({
                        "question": question,
                        "success": False,
                        "error": "timeout"
                    })
                
                except Exception as e:
                    error_msg = f"Q&A error: {str(e)}"
                    print(f"      ERROR: {error_msg}")
                    results["errors"].append(error_msg)
                    results["qa_results"].append({
                        "question": question,
                        "success": False,
                        "error": str(e)
                    })
        
        else:
            error_msg = f"Recommendation request failed with status {response.status_code}"
            print(f"   ERROR: {error_msg}")
            results["errors"].append(error_msg)
            results["recommendation_results"] = {
                "success": False,
                "error": error_msg
            }
    
    except requests.exceptions.Timeout:
        error_msg = "Recommendation request timed out"
        print(f"   TIME:  {error_msg}")
        results["errors"].append(error_msg)
        results["recommendation_results"] = {
            "success": False,
            "error": "timeout"
        }
    
    except Exception as e:
        error_msg = f"Recommendation error: {str(e)}"
        print(f"   ERROR: {error_msg}")
        results["errors"].append(error_msg)
        results["recommendation_results"] = {
            "success": False,
            "error": str(e)
        }
    
    return results


def run_benchmark(test_cases_file: str, num_tests: int = None):
    """
    Run benchmark on all test cases
    """
    # Load test cases
    print("LOAD: Loading test cases...")
    with open(test_cases_file, 'r') as f:
        data = json.load(f)
    
    test_cases = data["test_cases"]
    
    if num_tests:
        test_cases = test_cases[:num_tests]
        print(f"STATS: Running first {num_tests} test cases (for testing)")
    else:
        print(f"STATS: Running all {len(test_cases)} test cases")
    
    print(f"STATS: Total questions: {len(test_cases) * 3}")
    print(f"START: Starting benchmark...\n")
    
    # Run all tests
    all_results = []
    start_time = time.time()
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'#'*60}")
        print(f"Progress: {i}/{len(test_cases)} ({i/len(test_cases)*100:.1f}%)")
        
        # Estimate remaining time
        if i > 1:
            elapsed = time.time() - start_time
            avg_time_per_test = elapsed / (i - 1)
            remaining_tests = len(test_cases) - i + 1
            est_remaining = avg_time_per_test * remaining_tests
            print(f"TIME:  Estimated time remaining: {est_remaining/60:.1f} minutes")
        
        result = run_single_test(test_case)
        all_results.append(result)
        
        # Save intermediate results every 10 tests
        if i % 10 == 0:
            intermediate_file = f"results/intermediate_results_{i}.json"
            with open(intermediate_file, 'w') as f:
                json.dump({
                    "completed": i,
                    "total": len(test_cases),
                    "results": all_results
                }, f, indent=2)
            print(f"\n💾 Saved intermediate results to {intermediate_file}")
        
        # Delay between tests to avoid overwhelming the server
        time.sleep(2)
    
    end_time = time.time()
    total_time = end_time - start_time
    
    # Save final results
    output_file = f"results/benchmark_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    final_data = {
        "metadata": {
            "completed_at": datetime.now().isoformat(),
            "total_tests": len(test_cases),
            "total_time_seconds": total_time,
            "total_time_minutes": total_time / 60,
            "avg_time_per_test": total_time / len(test_cases)
        },
        "results": all_results
    }
    
    with open(output_file, 'w') as f:
        json.dump(final_data, f, indent=2)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"SUCCESS: BENCHMARK COMPLETE!")
    print(f"{'='*60}")
    print(f"STATS: Total tests: {len(test_cases)}")
    print(f"TIME:  Total time: {total_time/60:.1f} minutes")
    print(f"TIME:  Avg time per test: {total_time/len(test_cases):.1f} seconds")
    print(f"💾 Results saved to: {output_file}")
    
    # Quick stats
    successful_recs = sum(1 for r in all_results if r.get("recommendation_results", {}).get("success"))
    total_qa = sum(len(r.get("qa_results", [])) for r in all_results)
    successful_qa = sum(1 for r in all_results for qa in r.get("qa_results", []) if qa.get("success"))
    
    print(f"\nPROGRESS: Quick Stats:")
    print(f"   Successful recommendations: {successful_recs}/{len(test_cases)} ({successful_recs/len(test_cases)*100:.1f}%)")
    print(f"   Successful Q&A: {successful_qa}/{total_qa} ({successful_qa/total_qa*100:.1f}%)")
    
    return output_file


if __name__ == "__main__":
    import sys
    
    # Check if server is running
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=5)
        print("SUCCESS: Server is running\n")
    except:
        print("ERROR: Error: Server is not running at http://localhost:5001")
        print("Please start the model server first: python3 app.py")
        sys.exit(1)
    
    # Default: run all 100 tests
    # Or pass a number as argument to run fewer tests: python run_benchmark.py 20
    num_tests = int(sys.argv[1]) if len(sys.argv) > 1 else None
    
    test_cases_file = "test_data/test_cases.json"
    
    try:
        results_file = run_benchmark(test_cases_file, num_tests)
        print(f"\nDONE: Next step: Run analysis on {results_file}")
        print(f"   python3 analyze_results.py {results_file}")
    except KeyboardInterrupt:
        print("\n\n⚠️  Benchmark interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nERROR: Error running benchmark: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
