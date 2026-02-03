"""
Real-time evaluation utilities for VariantWise
Calculate metrics on-the-fly during recommendations

Now includes:
- Rule-based metrics (fast baseline)
- LLM-as-a-Judge (AWS Bedrock semantic evaluation)
- Advanced frameworks (Real DeepEval & RAGAS with OpenAI)
"""
import numpy as np
import asyncio
from typing import List, Dict, Optional
from llm_judge import get_llm_judge
from advanced_evaluation import get_advanced_evaluator


def calculate_diversity_score(recommendations: List[Dict]) -> float:
    """
    Calculate diversity of recommendations based on different attributes
    
    Args:
        recommendations: List of car recommendation dictionaries
        
    Returns:
        Diversity score (0-1)
    """
    if len(recommendations) < 2:
        return 0.0
    
    # Check diversity across key attributes
    fuel_types = set()
    body_types = set()
    brands = set()
    price_ranges = []
    
    for rec in recommendations:
        car = rec.get('car', {})
        
        # Extract attributes
        fuel_type = car.get('Fuel Type', '')
        if fuel_type:
            fuel_types.add(fuel_type)
        
        body_type = car.get('Body Type', '')
        if body_type:
            body_types.add(body_type)
        
        # Extract brand (first word of variant name)
        variant = car.get('variant', '')
        if variant:
            brand = variant.split()[0]
            brands.add(brand)
        
        # Price
        price = car.get('numeric_price')
        if price:
            price_ranges.append(price)
    
    # Calculate diversity components
    fuel_diversity = len(fuel_types) / min(len(recommendations), 5)  # Max 5 fuel types
    body_diversity = len(body_types) / min(len(recommendations), 5)  # Max 5 body types
    brand_diversity = len(brands) / len(recommendations)
    
    # Price diversity (coefficient of variation)
    price_diversity = 0
    if len(price_ranges) > 1:
        price_std = np.std(price_ranges)
        price_mean = np.mean(price_ranges)
        if price_mean > 0:
            price_diversity = min(price_std / price_mean, 1.0)
    
    # Weighted average
    diversity_score = (
        fuel_diversity * 0.25 +
        body_diversity * 0.25 +
        brand_diversity * 0.3 +
        price_diversity * 0.2
    )
    
    return round(diversity_score, 3)


def calculate_relevance_score(recommendations: List[Dict], preferences: Dict) -> float:
    """
    Calculate how well recommendations match user preferences
    
    Args:
        recommendations: List of car recommendations
        preferences: User preferences dictionary
        
    Returns:
        Relevance score (0-1)
    """
    if not recommendations:
        return 0.0
    
    total_score = 0
    max_possible_score = 0
    
    for rec in recommendations:
        car = rec.get('car', {})
        score = 0
        possible = 0
        
        # Budget match (10 points)
        price = car.get('numeric_price')
        if price:
            min_budget = preferences.get('min_budget', 0)
            max_budget = preferences.get('max_budget', float('inf'))
            
            if min_budget <= price <= max_budget:
                score += 10
            elif price <= max_budget * 1.2:  # Within 20% over budget
                score += 5
            possible += 10
        
        # Fuel type match (8 points)
        pref_fuel = preferences.get('fuel_type', 'Any')
        if pref_fuel != 'Any':
            car_fuel = car.get('Fuel Type', '')
            if car_fuel.lower() == pref_fuel.lower():
                score += 8
            possible += 8
        
        # Body type match (7 points)
        pref_body = preferences.get('body_type', 'Any')
        if pref_body != 'Any':
            car_body = car.get('Body Type', '')
            if car_body.lower() == pref_body.lower():
                score += 7
            possible += 7
        
        # Transmission match (6 points)
        pref_trans = preferences.get('transmission', 'Any')
        if pref_trans != 'Any':
            car_trans = car.get('Transmission Type', '')
            if car_trans.lower() == pref_trans.lower():
                score += 6
            possible += 6
        
        # Seating capacity (5 points)
        pref_seating = preferences.get('seating', 0)
        car_seating = car.get('Seating Capacity', 0)
        try:
            if int(car_seating) >= pref_seating:
                score += 5
            possible += 5
        except:
            pass
        
        # Feature matching (3 points per feature)
        pref_features = preferences.get('features', [])
        if pref_features:
            for feature in pref_features:
                # Check if feature exists in any car attribute
                car_str = ' '.join(str(v).lower() for v in car.values() 
                                 if v is not None and str(v).lower() not in ['nan', 'none', ''])
                if feature.lower() in car_str:
                    score += 3
                possible += 3
        
        total_score += score
        max_possible_score += possible if possible > 0 else 36  # Default max
    
    relevance = total_score / max_possible_score if max_possible_score > 0 else 0
    return round(relevance, 3)


def calculate_recommendation_quality(recommendations: List[Dict], 
                                    preferences: Dict,
                                    response_time: float,
                                    use_llm_judge: bool = True,
                                    use_advanced: bool = True) -> Dict:
    """
    Calculate comprehensive quality metrics for recommendations
    
    Args:
        recommendations: List of recommendations
        preferences: User preferences
        response_time: API response time in seconds
        use_llm_judge: Whether to use LLM-as-a-Judge evaluation
        
    Returns:
        Dictionary with quality metrics
    """
    # Rule-based metrics
    diversity = calculate_diversity_score(recommendations)
    relevance = calculate_relevance_score(recommendations, preferences)
    
    # Performance score (based on response time)
    if response_time < 1.0:
        performance = 1.0
    elif response_time < 2.0:
        performance = 0.9
    elif response_time < 3.0:
        performance = 0.7
    else:
        performance = 0.5
    
    # Base metrics
    metrics = {
        'diversity_score': diversity,
        'relevance_score': relevance,
        'performance_score': round(performance, 3),
        'response_time': round(response_time, 2),
        'num_recommendations': len(recommendations)
    }
    
    # Advanced evaluation (if enabled)
    if use_advanced:
        try:
            advanced_eval = get_advanced_evaluator()
            if advanced_eval.is_available():
                advanced_scores = advanced_eval.evaluate_recommendations_advanced(
                    recommendations, preferences
                )
                metrics.update(advanced_scores)
        except Exception as e:
            print(f"Error in advanced evaluation: {e}")
            metrics['advanced_error'] = str(e)
    
    # LLM-based evaluation (if enabled)
    if use_llm_judge:
        try:
            judge = get_llm_judge()
            if judge.is_available():
                llm_scores = judge.evaluate_recommendations(preferences, recommendations)
                metrics.update(llm_scores)
                
                # If LLM evaluation succeeded, use hybrid score
                if 'llm_overall' in llm_scores:
                    # Combine rule-based and LLM scores
                    rule_based_score = (
                        relevance * 0.5 +
                        diversity * 0.3 +
                        performance * 0.2
                    )
                    
                    # Multi-tier hybrid scoring
                    if metrics.get('advanced_overall'):
                        # Best: Advanced + LLM + Rule-based
                        metrics['overall_quality'] = round(
                            metrics['advanced_overall'] * 0.4 +
                            llm_scores['llm_overall'] * 0.4 +
                            rule_based_score * 0.2,
                            3
                        )
                        metrics['evaluation_method'] = 'advanced_hybrid'
                    else:
                        # Good: LLM + Rule-based
                        metrics['overall_quality'] = round(
                            llm_scores['llm_overall'] * 0.6 + rule_based_score * 0.4,
                            3
                        )
                        metrics['evaluation_method'] = 'llm_hybrid'
                else:
                    # Fallback to rule-based
                    metrics['overall_quality'] = round(
                        relevance * 0.5 + diversity * 0.3 + performance * 0.2,
                        3
                    )
                    metrics['evaluation_method'] = 'rule_based'
            else:
                # LLM not available, use rule-based only
                metrics['overall_quality'] = round(
                    relevance * 0.5 + diversity * 0.3 + performance * 0.2,
                    3
                )
                metrics['evaluation_method'] = 'rule_based'
                metrics['llm_available'] = False
        except Exception as e:
            print(f"Error in LLM evaluation: {e}")
            # Fallback to rule-based
            metrics['overall_quality'] = round(
                relevance * 0.5 + diversity * 0.3 + performance * 0.2,
                3
            )
            metrics['evaluation_method'] = 'rule_based'
            metrics['llm_error'] = str(e)
    else:
        # Rule-based only (when LLM disabled)
        metrics['overall_quality'] = round(
            relevance * 0.5 + diversity * 0.3 + performance * 0.2,
            3
        )
        metrics['evaluation_method'] = 'rule_based'
    
    return metrics


def calculate_answer_quality(answer: str, question: str, context: str, 
                           use_llm_judge: bool = True, use_advanced: bool = True,
                           ground_truth: Optional[str] = None) -> Dict:
    """
    Calculate Q&A answer quality metrics
    
    Args:
        answer: Generated answer
        question: User question
        context: Retrieved context
        use_llm_judge: Whether to use LLM-as-a-Judge evaluation
        
    Returns:
        Dictionary with answer quality metrics
    """
    # Rule-based metrics
    answer_length = len(answer.split())
    if 10 <= answer_length <= 200:
        length_score = 1.0
    elif answer_length < 10:
        length_score = answer_length / 10
    else:
        length_score = 200 / answer_length
    
    # Relevance (check if question keywords appear in answer)
    question_words = set(question.lower().split()) - {
        'what', 'which', 'how', 'why', 'when', 'where', 'is', 'are', 'the', 'a', 'an', 'do', 'does'
    }
    answer_words = set(answer.lower().split())
    
    if question_words:
        relevance = len(question_words & answer_words) / len(question_words)
    else:
        relevance = 0.5
    
    # Groundedness (check if answer content appears in context)
    answer_tokens = set(answer.lower().split())
    context_tokens = set(context.lower().split())
    
    # Remove common words
    common_words = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'has', 'have', 
                   'had', 'with', 'for', 'to', 'of', 'in', 'on', 'at', 'by'}
    answer_tokens = answer_tokens - common_words
    
    if answer_tokens:
        groundedness = len(answer_tokens & context_tokens) / len(answer_tokens)
    else:
        groundedness = 1.0
    
    # Base metrics
    metrics = {
        'relevance_score': round(relevance, 3),
        'groundedness_score': round(groundedness, 3),
        'length_score': round(length_score, 3),
        'answer_length': answer_length
    }
    
    # Advanced evaluation (DeepEval + RAGAS with OpenAI)
    if use_advanced:
        try:
            advanced_eval = get_advanced_evaluator()
            if advanced_eval.is_available():
                # Run async evaluation synchronously
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                # DeepEval
                deepeval_scores = loop.run_until_complete(
                    advanced_eval.evaluate_qa_deepeval(question, answer, context, ground_truth)
                )
                metrics.update(deepeval_scores)
                
                # RAGAS
                ragas_scores = loop.run_until_complete(
                    advanced_eval.evaluate_qa_ragas(question, answer, context, ground_truth)
                )
                metrics.update(ragas_scores)
                
                loop.close()
        except Exception as e:
            print(f"Error in advanced evaluation: {e}")
            metrics['advanced_error'] = str(e)
    
    # LLM-based evaluation (if enabled)
    if use_llm_judge:
        try:
            judge = get_llm_judge()
            if judge.is_available():
                # Get LLM evaluation
                llm_scores = judge.evaluate_answer_quality(question, answer, context)
                metrics.update(llm_scores)
                
                # Get hallucination detection
                hallucination = judge.detect_hallucination(answer, context)
                metrics.update(hallucination)
                
                # If LLM evaluation succeeded, use hybrid score
                if 'llm_overall' in llm_scores:
                    # Combine rule-based and LLM scores
                    rule_based_score = (relevance * 0.4 + groundedness * 0.4 + length_score * 0.2)
                    
                    # Multi-framework hybrid scoring
                    if metrics.get('deepeval_overall') or metrics.get('ragas_overall'):
                        # Best: DeepEval/RAGAS + LLM + Rule-based
                        advanced_score = metrics.get('deepeval_overall', metrics.get('ragas_overall', 0))
                        metrics['overall_quality'] = round(
                            advanced_score * 0.5 +
                            llm_scores['llm_overall'] * 0.3 +
                            rule_based_score * 0.2,
                            3
                        )
                        metrics['evaluation_method'] = 'advanced_hybrid'
                    else:
                        # Good: LLM + Rule-based
                        metrics['overall_quality'] = round(
                            llm_scores['llm_overall'] * 0.7 + rule_based_score * 0.3,
                            3
                        )
                        metrics['evaluation_method'] = 'llm_hybrid'
                    
                    # Penalize if hallucination detected
                    if hallucination.get('hallucination_detected', False):
                        penalty = hallucination.get('hallucination_confidence', 0.5) * 0.3
                        metrics['overall_quality'] = round(
                            max(0, metrics['overall_quality'] - penalty),
                            3
                        )
                        metrics['hallucination_penalty'] = round(penalty, 3)
                else:
                    # Fallback to rule-based
                    metrics['overall_quality'] = round(
                        relevance * 0.4 + groundedness * 0.4 + length_score * 0.2,
                        3
                    )
                    metrics['evaluation_method'] = 'rule_based'
            else:
                # LLM not available
                metrics['overall_quality'] = round(
                    relevance * 0.4 + groundedness * 0.4 + length_score * 0.2,
                    3
                )
                metrics['evaluation_method'] = 'rule_based'
                metrics['llm_available'] = False
        except Exception as e:
            print(f"Error in LLM evaluation: {e}")
            # Fallback to rule-based
            metrics['overall_quality'] = round(
                relevance * 0.4 + groundedness * 0.4 + length_score * 0.2,
                3
            )
            metrics['evaluation_method'] = 'rule_based'
            metrics['llm_error'] = str(e)
    else:
        # Rule-based only
        metrics['overall_quality'] = round(
            relevance * 0.4 + groundedness * 0.4 + length_score * 0.2,
            3
        )
        metrics['evaluation_method'] = 'rule_based'
    
    return metrics
