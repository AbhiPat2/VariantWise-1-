"""
Advanced Evaluation with REAL DeepEval (using OpenAI)
This version uses the actual DeepEval library with full features
"""
import os
import asyncio
import nest_asyncio
from typing import Dict, List, Optional
import numpy as np
from dotenv import load_dotenv

# Enable nested event loops
nest_asyncio.apply()
load_dotenv()

# DeepEval imports
try:
    from deepeval import evaluate
    from deepeval.metrics import (
        AnswerRelevancyMetric,
        FaithfulnessMetric,
        ContextualRelevancyMetric,
        HallucinationMetric,
    )
    from deepeval.test_case import LLMTestCase
    from deepeval.models.base_model import DeepEvalBaseLLM
    DEEPEVAL_AVAILABLE = True
except ImportError:
    print("⚠️  DeepEval not available. Install with: pip install deepeval")
    DEEPEVAL_AVAILABLE = False

# RAGAS imports
try:
    from ragas import evaluate as ragas_evaluate
    from ragas.metrics import (
        faithfulness,
        answer_relevancy,
        context_precision,
        context_recall,
    )
    from datasets import Dataset
    from langchain_openai import ChatOpenAI
    RAGAS_AVAILABLE = True
except ImportError:
    print("⚠️  RAGAS not available. Install with: pip install ragas langchain-openai")
    RAGAS_AVAILABLE = False


class AdvancedEvaluator:
    """
    Advanced evaluator using REAL DeepEval and RAGAS with OpenAI
    """
    
    def __init__(self):
        """Initialize with OpenAI configuration"""
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.deepeval_model = os.getenv('DEEPEVAL_MODEL', 'gpt-4o-mini')
        
        if not self.openai_api_key or self.openai_api_key == 'your-new-openai-key-here':
            print("⚠️  OpenAI API key not configured. Advanced evaluation disabled.")
            self.deepeval_available = False
            self.ragas_available = False
            return
        
        self.deepeval_available = DEEPEVAL_AVAILABLE
        self.ragas_available = RAGAS_AVAILABLE
        
        # Set OpenAI key for DeepEval
        if self.deepeval_available:
            os.environ['OPENAI_API_KEY'] = self.openai_api_key
            print(f"✅ Real DeepEval initialized with model: {self.deepeval_model}")
        
        # Initialize LLM for RAGAS
        if self.ragas_available:
            try:
                self.ragas_llm = ChatOpenAI(
                    model=self.deepeval_model,
                    temperature=0.1,
                    openai_api_key=self.openai_api_key
                )
                print(f"✅ Real RAGAS initialized with model: {self.deepeval_model}")
            except Exception as e:
                print(f"⚠️  Failed to initialize RAGAS: {e}")
                self.ragas_available = False
    
    def is_available(self) -> bool:
        """Check if advanced evaluation is available"""
        # Recommendation metrics (NDCG, ILD, Novelty) are always available
        # Only Q&A metrics need DeepEval/RAGAS
        return True  # Recommendation metrics don't need external dependencies
    
    def is_qa_evaluation_available(self) -> bool:
        """Check if Q&A evaluation (DeepEval/RAGAS) is available"""
        return self.deepeval_available or self.ragas_available
    
    async def evaluate_qa_deepeval(self, question: str, answer: str, 
                                   context: str, ground_truth: Optional[str] = None) -> Dict:
        """
        Evaluate Q&A using REAL DeepEval framework with OpenAI
        
        This uses the actual DeepEval library with full features:
        - Answer Relevancy
        - Faithfulness
        - Contextual Relevancy
        - Hallucination Detection
        
        Args:
            question: User's question
            answer: Generated answer
            context: Retrieved context
            ground_truth: Optional expected answer
            
        Returns:
            Dictionary with DeepEval metrics
        """
        if not self.deepeval_available:
            return {'deepeval_available': False}
        
        try:
            # Create test case for DeepEval
            test_case = LLMTestCase(
                input=question,
                actual_output=answer,
                retrieval_context=[context],
                expected_output=ground_truth if ground_truth else None,
                context=[context]
            )
            
            # Initialize metrics
            metrics = []
            results = {}
            
            # 1. Answer Relevancy - Does answer address the question?
            try:
                answer_relevancy = AnswerRelevancyMetric(
                    threshold=0.7,
                    model=self.deepeval_model
                )
                answer_relevancy.measure(test_case)
                results['deepeval_answer_relevancy'] = answer_relevancy.score
                results['deepeval_answer_relevancy_reason'] = answer_relevancy.reason
                metrics.append(answer_relevancy.score)
            except Exception as e:
                print(f"DeepEval Answer Relevancy error: {e}")
                results['deepeval_answer_relevancy'] = 0.5
            
            # 2. Faithfulness - Is answer faithful to context?
            try:
                faithfulness = FaithfulnessMetric(
                    threshold=0.7,
                    model=self.deepeval_model
                )
                faithfulness.measure(test_case)
                results['deepeval_faithfulness'] = faithfulness.score
                results['deepeval_faithfulness_reason'] = faithfulness.reason
                metrics.append(faithfulness.score)
            except Exception as e:
                print(f"DeepEval Faithfulness error: {e}")
                results['deepeval_faithfulness'] = 0.5
            
            # 3. Contextual Relevancy - Is context relevant to question?
            try:
                contextual_relevancy = ContextualRelevancyMetric(
                    threshold=0.7,
                    model=self.deepeval_model
                )
                contextual_relevancy.measure(test_case)
                results['deepeval_contextual_relevancy'] = contextual_relevancy.score
                results['deepeval_contextual_relevancy_reason'] = contextual_relevancy.reason
                metrics.append(contextual_relevancy.score)
            except Exception as e:
                print(f"DeepEval Contextual Relevancy error: {e}")
                results['deepeval_contextual_relevancy'] = 0.5
            
            # 4. Hallucination Detection
            try:
                hallucination = HallucinationMetric(
                    threshold=0.5,
                    model=self.deepeval_model
                )
                hallucination.measure(test_case)
                results['deepeval_hallucination'] = hallucination.score
                results['deepeval_hallucination_reason'] = hallucination.reason
                # Note: Hallucination score is inverted (lower is better)
                # We invert it so higher is better for consistency
                results['deepeval_no_hallucination'] = 1 - hallucination.score
                metrics.append(1 - hallucination.score)
            except Exception as e:
                print(f"DeepEval Hallucination error: {e}")
                results['deepeval_hallucination'] = 0.5
                results['deepeval_no_hallucination'] = 0.5
            
            # Calculate overall score
            if metrics:
                results['deepeval_overall'] = np.mean(metrics)
            
            results['deepeval_available'] = True
            results['deepeval_method'] = 'real_deepeval_openai'
            results['deepeval_model'] = self.deepeval_model
            
            return results
            
        except Exception as e:
            print(f"Error in Real DeepEval evaluation: {e}")
            import traceback
            traceback.print_exc()
            return {
                'deepeval_available': True,
                'deepeval_error': str(e)
            }
    
    async def evaluate_qa_ragas(self, question: str, answer: str,
                               context: str, ground_truth: Optional[str] = None) -> Dict:
        """
        Evaluate Q&A using REAL RAGAS framework with OpenAI
        
        This uses the actual RAGAS library with full features:
        - Faithfulness
        - Answer Relevancy
        - Context Precision
        - Context Recall
        
        Args:
            question: User's question
            answer: Generated answer
            context: Retrieved context
            ground_truth: Optional expected answer
            
        Returns:
            Dictionary with RAGAS metrics
        """
        if not self.ragas_available:
            return {'ragas_available': False}
        
        try:
            # Prepare dataset for RAGAS
            data = {
                'question': [question],
                'answer': [answer],
                'contexts': [[context]],
            }
            
            # Add ground truth if available
            if ground_truth:
                data['ground_truth'] = [ground_truth]
            
            dataset = Dataset.from_dict(data)
            
            # Select metrics based on available data
            metrics_to_use = [faithfulness, answer_relevancy]
            
            # Context precision and recall need ground truth
            if ground_truth:
                metrics_to_use.extend([context_precision, context_recall])
            
            # Run RAGAS evaluation
            result = ragas_evaluate(
                dataset,
                metrics=metrics_to_use,
                llm=self.ragas_llm,
            )
            
            # Extract scores
            ragas_scores = {}
            
            if hasattr(result, 'to_pandas'):
                df = result.to_pandas()
                for col in df.columns:
                    if col in ['faithfulness', 'answer_relevancy', 'context_precision', 'context_recall']:
                        score = df[col].iloc[0]
                        ragas_scores[f'ragas_{col}'] = float(score) if not np.isnan(score) else 0.5
            
            # Calculate overall RAGAS score
            if ragas_scores:
                ragas_scores['ragas_overall'] = np.mean(list(ragas_scores.values()))
            
            ragas_scores['ragas_available'] = True
            ragas_scores['ragas_method'] = 'real_ragas_openai'
            ragas_scores['ragas_model'] = self.deepeval_model
            
            return ragas_scores
            
        except Exception as e:
            print(f"Error in Real RAGAS evaluation: {e}")
            import traceback
            traceback.print_exc()
            return {
                'ragas_available': True,
                'ragas_error': str(e)
            }
    
    def evaluate_recommendations_advanced(self, recommendations: List[Dict],
                                         user_prefs: Dict) -> Dict:
        """
        Advanced recommendation evaluation using custom algorithms
        This doesn't need OpenAI - uses mathematical metrics
        """
        try:
            results = {}
            
            # 1. DIVERSITY METRICS
            results.update(self._calculate_diversity_metrics(recommendations))
            
            # 2. RELEVANCE METRICS (NDCG, MRR, Precision, Recall)
            results.update(self._calculate_relevance_metrics(recommendations, user_prefs))
            
            # 3. NOVELTY & SERENDIPITY
            results.update(self._calculate_novelty_metrics(recommendations, user_prefs))
            
            # 4. EXPLAINABILITY
            results.update(self._calculate_explainability_metrics(recommendations, user_prefs))
            
            # Overall advanced score
            key_metrics = [
                results.get('advanced_ndcg', 0),
                results.get('advanced_diversity', 0),
                results.get('advanced_novelty', 0),
                results.get('advanced_explainability', 0),
            ]
            results['advanced_overall'] = sum(key_metrics) / len(key_metrics)
            results['advanced_available'] = True
            
            return results
            
        except Exception as e:
            print(f"Error in advanced recommendation evaluation: {e}")
            return {
                'advanced_available': False,
                'advanced_error': str(e)
            }
    
    def _calculate_diversity_metrics(self, recommendations: List[Dict]) -> Dict:
        """Calculate advanced diversity metrics"""
        if not recommendations:
            return {}
        
        metrics = {}
        
        # Intra-List Diversity (ILD) - average pairwise distance
        distances = []
        for i in range(len(recommendations)):
            for j in range(i + 1, len(recommendations)):
                car1 = recommendations[i].get('car', {})
                car2 = recommendations[j].get('car', {})
                
                # Calculate distance based on multiple attributes
                dist = 0
                
                # Price distance
                price1 = car1.get('numeric_price', 0)
                price2 = car2.get('numeric_price', 0)
                if price1 and price2:
                    max_price = max(price1, price2) or 1
                    dist += abs(price1 - price2) / max_price
                
                # Categorical differences
                if car1.get('Fuel Type') != car2.get('Fuel Type'):
                    dist += 1
                if car1.get('Body Type') != car2.get('Body Type'):
                    dist += 1
                if car1.get('Transmission Type') != car2.get('Transmission Type'):
                    dist += 1
                
                # Brand difference
                brand1 = car1.get('variant', '').split()[0]
                brand2 = car2.get('variant', '').split()[0]
                if brand1 != brand2:
                    dist += 0.5
                
                distances.append(dist)
        
        if distances:
            metrics['advanced_ild'] = np.mean(distances) / 4.5  # Normalize to 0-1
        
        # Coverage - how many different categories covered
        fuel_types = set()
        body_types = set()
        brands = set()
        
        for rec in recommendations:
            car = rec.get('car', {})
            if car.get('Fuel Type'):
                fuel_types.add(car['Fuel Type'])
            if car.get('Body Type'):
                body_types.add(car['Body Type'])
            brand = car.get('variant', '').split()[0]
            if brand:
                brands.add(brand)
        
        total_categories = len(fuel_types) + len(body_types) + len(brands)
        max_categories = 15  # 5 fuel + 5 body + 5 brands (reasonable max)
        metrics['advanced_coverage'] = min(total_categories / max_categories, 1.0)
        
        # Gini Coefficient - measure of inequality in recommendation distribution
        prices = [rec.get('car', {}).get('numeric_price', 0) for rec in recommendations if rec.get('car', {}).get('numeric_price')]
        if prices:
            prices_sorted = sorted(prices)
            n = len(prices)
            index = np.arange(1, n + 1)
            gini = (2 * np.sum(index * prices_sorted)) / (n * np.sum(prices_sorted)) - (n + 1) / n
            metrics['advanced_gini'] = 1 - gini  # Invert so higher is better
        
        # Overall diversity
        div_metrics = [v for k, v in metrics.items() if k.startswith('advanced_')]
        if div_metrics:
            metrics['advanced_diversity'] = np.mean(div_metrics)
        
        return metrics
    
    def _calculate_relevance_metrics(self, recommendations: List[Dict], user_prefs: Dict) -> Dict:
        """Calculate advanced relevance metrics (NDCG, MRR, etc.)"""
        metrics = {}
        
        # Calculate relevance scores for each recommendation
        relevance_scores = []
        for rec in recommendations:
            car = rec.get('car', {})
            score = 0
            max_score = 0
            
            # Budget relevance
            price = car.get('numeric_price', 0)
            min_budget = user_prefs.get('min_budget', 0)
            max_budget = user_prefs.get('max_budget', float('inf'))
            
            if price:
                if min_budget <= price <= max_budget:
                    score += 10
                elif price <= max_budget * 1.1:
                    score += 7
                elif price <= max_budget * 1.2:
                    score += 4
                max_score += 10
            
            # Feature matching
            pref_fuel = user_prefs.get('fuel_type', 'Any')
            if pref_fuel != 'Any':
                if car.get('Fuel Type', '').lower() == pref_fuel.lower():
                    score += 8
                max_score += 8
            
            pref_body = user_prefs.get('body_type', 'Any')
            if pref_body != 'Any':
                if car.get('Body Type', '').lower() == pref_body.lower():
                    score += 7
                max_score += 7
            
            pref_trans = user_prefs.get('transmission', 'Any')
            if pref_trans != 'Any':
                if car.get('Transmission Type', '').lower() == pref_trans.lower():
                    score += 6
                max_score += 6
            
            # Normalize
            relevance = score / max_score if max_score > 0 else 0
            relevance_scores.append(relevance)
        
        if relevance_scores:
            # NDCG@K (Normalized Discounted Cumulative Gain)
            dcg = sum((2**rel - 1) / np.log2(i + 2) for i, rel in enumerate(relevance_scores))
            ideal_scores = sorted(relevance_scores, reverse=True)
            idcg = sum((2**rel - 1) / np.log2(i + 2) for i, rel in enumerate(ideal_scores))
            metrics['advanced_ndcg'] = dcg / idcg if idcg > 0 else 0
            
            # MRR (Mean Reciprocal Rank)
            for i, score in enumerate(relevance_scores):
                if score >= 0.8:
                    metrics['advanced_mrr'] = 1 / (i + 1)
                    break
            if 'advanced_mrr' not in metrics:
                metrics['advanced_mrr'] = 0
            
            # Precision@K and Recall@K
            relevant_threshold = 0.7
            relevant_items = sum(1 for s in relevance_scores if s >= relevant_threshold)
            metrics['advanced_precision'] = relevant_items / len(relevance_scores)
            metrics['advanced_recall'] = relevant_items / min(5, len(relevance_scores))
        
        return metrics
    
    def _calculate_novelty_metrics(self, recommendations: List[Dict], user_prefs: Dict) -> Dict:
        """Calculate novelty and serendipity metrics"""
        metrics = {}
        
        novelty_scores = []
        
        for rec in recommendations:
            car = rec.get('car', {})
            novelty = 0
            
            # Different from preferences = novel
            pref_fuel = user_prefs.get('fuel_type', 'Any')
            if pref_fuel != 'Any' and car.get('Fuel Type', '').lower() != pref_fuel.lower():
                novelty += 0.3
            
            pref_body = user_prefs.get('body_type', 'Any')
            if pref_body != 'Any' and car.get('Body Type', '').lower() != pref_body.lower():
                novelty += 0.3
            
            # Slightly above budget but reasonable
            price = car.get('numeric_price', 0)
            max_budget = user_prefs.get('max_budget', 0)
            if price and max_budget:
                if 1.0 < price / max_budget <= 1.15:
                    novelty += 0.2
            
            # Non-mainstream brands
            brand = car.get('variant', '').split()[0]
            mainstream_brands = ['Maruti', 'Hyundai', 'Tata', 'Honda', 'Toyota']
            if brand not in mainstream_brands:
                novelty += 0.2
            
            novelty_scores.append(min(novelty, 1.0))
        
        if novelty_scores:
            metrics['advanced_novelty'] = np.mean(novelty_scores)
            metrics['advanced_serendipity'] = metrics['advanced_novelty'] * 0.7
        
        return metrics
    
    def _calculate_explainability_metrics(self, recommendations: List[Dict], user_prefs: Dict) -> Dict:
        """Calculate explainability and transparency metrics"""
        metrics = {}
        
        feature_matches = {
            'budget': 0,
            'fuel': 0,
            'body': 0,
            'transmission': 0,
            'features': 0
        }
        
        for rec in recommendations:
            car = rec.get('car', {})
            details = rec.get('details', {})
            
            if details.get('budget_match', False):
                feature_matches['budget'] += 1
            if details.get('fuel_match', False):
                feature_matches['fuel'] += 1
            if details.get('body_match', False):
                feature_matches['body'] += 1
            if details.get('transmission_match', False):
                feature_matches['transmission'] += 1
            if details.get('features_matched', 0) > 0:
                feature_matches['features'] += 1
        
        total_features_checked = len([v for v in user_prefs.values() if v and v != 'Any'])
        if total_features_checked > 0:
            total_matches = sum(feature_matches.values())
            max_possible_matches = len(recommendations) * total_features_checked
            metrics['advanced_explainability'] = total_matches / max_possible_matches if max_possible_matches > 0 else 0
        else:
            metrics['advanced_explainability'] = 1.0
        
        metrics['advanced_feature_importance'] = feature_matches
        
        return metrics


# Global instance
_advanced_evaluator = None

def get_advanced_evaluator() -> AdvancedEvaluator:
    """Get or create global advanced evaluator instance"""
    global _advanced_evaluator
    if _advanced_evaluator is None:
        _advanced_evaluator = AdvancedEvaluator()
    return _advanced_evaluator
