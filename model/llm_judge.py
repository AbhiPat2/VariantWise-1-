"""
LLM-as-a-Judge Evaluation System for VariantWise
Uses AWS Bedrock to evaluate recommendation and Q&A quality
"""
import os
import json
from typing import Dict, List
import boto3
from langchain_community.chat_models import BedrockChat


class LLMJudge:
    """LLM-based evaluation judge using AWS Bedrock"""
    
    def __init__(self):
        """Initialize the LLM judge with Bedrock"""
        try:
            # Use existing Bedrock configuration
            aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
            aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
            aws_region = os.getenv('AWS_REGION', 'us-east-1')
            
            if not aws_access_key or not aws_secret_key:
                print("Warning: AWS credentials not found. LLM Judge will be disabled.")
                self.llm = None
                return
            
            # Initialize Bedrock client
            bedrock_runtime = boto3.client(
                service_name='bedrock-runtime',
                region_name=aws_region,
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=aws_secret_key
            )
            
            # Use Mistral for judging (fast and cost-effective)
            self.llm = BedrockChat(
                client=bedrock_runtime,
                model_id="mistral.mistral-7b-instruct-v0:2",
                model_kwargs={
                    "temperature": 0.1,  # Low temperature for consistent judgments
                    "max_tokens": 500
                }
            )
            print("✅ LLM Judge initialized successfully")
            
        except Exception as e:
            print(f"Warning: Failed to initialize LLM Judge: {e}")
            self.llm = None
    
    def is_available(self) -> bool:
        """Check if LLM judge is available"""
        return self.llm is not None
    
    def evaluate_answer_quality(self, question: str, answer: str, context: str) -> Dict:
        """
        Evaluate Q&A answer quality using LLM
        
        Args:
            question: User's question
            answer: Generated answer
            context: Context used to generate answer
            
        Returns:
            Dictionary with LLM-based quality scores
        """
        if not self.is_available():
            return {
                'llm_available': False,
                'error': 'LLM Judge not available'
            }
        
        try:
            prompt = f"""You are an expert evaluator assessing the quality of an AI assistant's answer about cars.

Question: {question}

Context Available:
{context[:1000]}...  [truncated]

Generated Answer:
{answer}

Evaluate the answer on these criteria (score 0-10 for each):

1. RELEVANCE: Does the answer directly address the question?
2. ACCURACY: Is the answer factually correct based on the context?
3. COMPLETENESS: Does it provide sufficient information?
4. HELPFULNESS: Would this answer help the user make a decision?
5. GROUNDEDNESS: Is the answer based on the provided context (not hallucinated)?

Respond ONLY with a JSON object in this exact format:
{{
    "relevance": <score 0-10>,
    "accuracy": <score 0-10>,
    "completeness": <score 0-10>,
    "helpfulness": <score 0-10>,
    "groundedness": <score 0-10>,
    "reasoning": "<brief explanation>"
}}"""

            response = self.llm.invoke(prompt)
            result_text = response.content.strip()
            
            # Extract JSON from response
            # Sometimes LLM adds extra text, so find the JSON part
            start_idx = result_text.find('{')
            end_idx = result_text.rfind('}') + 1
            
            if start_idx == -1 or end_idx == 0:
                raise ValueError("No JSON found in response")
            
            json_str = result_text[start_idx:end_idx]
            scores = json.loads(json_str)
            
            # Normalize scores to 0-1 range
            normalized = {
                'llm_relevance': scores.get('relevance', 0) / 10,
                'llm_accuracy': scores.get('accuracy', 0) / 10,
                'llm_completeness': scores.get('completeness', 0) / 10,
                'llm_helpfulness': scores.get('helpfulness', 0) / 10,
                'llm_groundedness': scores.get('groundedness', 0) / 10,
                'llm_reasoning': scores.get('reasoning', ''),
                'llm_available': True
            }
            
            # Calculate overall LLM score
            normalized['llm_overall'] = (
                normalized['llm_relevance'] * 0.25 +
                normalized['llm_accuracy'] * 0.25 +
                normalized['llm_completeness'] * 0.15 +
                normalized['llm_helpfulness'] * 0.15 +
                normalized['llm_groundedness'] * 0.20
            )
            
            return normalized
            
        except Exception as e:
            print(f"Error in LLM evaluation: {e}")
            return {
                'llm_available': True,
                'error': str(e),
                'llm_overall': 0.5  # Neutral score on error
            }
    
    def evaluate_recommendations(self, user_prefs: Dict, recommendations: List[Dict]) -> Dict:
        """
        Evaluate recommendation quality using LLM
        
        Args:
            user_prefs: User preferences dictionary
            recommendations: List of recommended cars
            
        Returns:
            Dictionary with LLM-based quality scores
        """
        if not self.is_available():
            return {
                'llm_available': False,
                'error': 'LLM Judge not available'
            }
        
        try:
            # Format recommendations for evaluation
            rec_summary = []
            for i, rec in enumerate(recommendations[:5], 1):
                car = rec.get('car', {})
                rec_summary.append(
                    f"{i}. {car.get('variant', 'N/A')} - "
                    f"₹{car.get('price', 'N/A')}, "
                    f"{car.get('Fuel Type', 'N/A')}, "
                    f"{car.get('Body Type', 'N/A')}, "
                    f"{car.get('Transmission Type', 'N/A')}"
                )
            
            recommendations_text = "\n".join(rec_summary)
            
            # Format preferences
            prefs_text = f"""
Budget: ₹{user_prefs.get('min_budget', 0):,} - ₹{user_prefs.get('max_budget', 0):,}
Fuel Type: {user_prefs.get('fuel_type', 'Any')}
Body Type: {user_prefs.get('body_type', 'Any')}
Transmission: {user_prefs.get('transmission', 'Any')}
Seating: {user_prefs.get('seating', 'Any')}
Features: {', '.join(user_prefs.get('features', [])) or 'None specified'}
Performance Priority: {user_prefs.get('performance', 5)}/10
"""
            
            prompt = f"""You are an expert car consultant evaluating AI-generated car recommendations.

User Preferences:
{prefs_text}

Recommended Cars:
{recommendations_text}

Evaluate these recommendations on these criteria (score 0-10 for each):

1. RELEVANCE: Do the cars match the user's stated preferences?
2. DIVERSITY: Is there good variety in the recommendations?
3. PRACTICALITY: Are these realistic, practical choices for the user?
4. VALUE: Do the recommendations offer good value for money?
5. REASONING: Is the selection well-reasoned and appropriate?

Respond ONLY with a JSON object in this exact format:
{{
    "relevance": <score 0-10>,
    "diversity": <score 0-10>,
    "practicality": <score 0-10>,
    "value": <score 0-10>,
    "reasoning_quality": <score 0-10>,
    "explanation": "<brief explanation>"
}}"""

            response = self.llm.invoke(prompt)
            result_text = response.content.strip()
            
            # Extract JSON
            start_idx = result_text.find('{')
            end_idx = result_text.rfind('}') + 1
            
            if start_idx == -1 or end_idx == 0:
                raise ValueError("No JSON found in response")
            
            json_str = result_text[start_idx:end_idx]
            scores = json.loads(json_str)
            
            # Normalize scores to 0-1 range
            normalized = {
                'llm_relevance': scores.get('relevance', 0) / 10,
                'llm_diversity': scores.get('diversity', 0) / 10,
                'llm_practicality': scores.get('practicality', 0) / 10,
                'llm_value': scores.get('value', 0) / 10,
                'llm_reasoning_quality': scores.get('reasoning_quality', 0) / 10,
                'llm_explanation': scores.get('explanation', ''),
                'llm_available': True
            }
            
            # Calculate overall LLM score
            normalized['llm_overall'] = (
                normalized['llm_relevance'] * 0.30 +
                normalized['llm_diversity'] * 0.20 +
                normalized['llm_practicality'] * 0.20 +
                normalized['llm_value'] * 0.15 +
                normalized['llm_reasoning_quality'] * 0.15
            )
            
            return normalized
            
        except Exception as e:
            print(f"Error in LLM evaluation: {e}")
            return {
                'llm_available': True,
                'error': str(e),
                'llm_overall': 0.5  # Neutral score on error
            }
    
    def detect_hallucination(self, answer: str, context: str) -> Dict:
        """
        Detect if answer contains hallucinated information
        
        Args:
            answer: Generated answer
            context: Available context
            
        Returns:
            Dictionary with hallucination detection results
        """
        if not self.is_available():
            return {
                'llm_available': False,
                'hallucination_detected': False
            }
        
        try:
            prompt = f"""You are an expert at detecting hallucinations in AI-generated text.

Context (Available Information):
{context[:1500]}...

Generated Answer:
{answer}

Task: Determine if the answer contains any information that is NOT supported by the context.

Hallucination means the AI made up facts, numbers, or claims that aren't in the context.

Respond ONLY with a JSON object:
{{
    "hallucination_detected": <true or false>,
    "confidence": <0-10>,
    "hallucinated_parts": "<list specific parts that are hallucinated, or 'none'>",
    "explanation": "<brief explanation>"
}}"""

            response = self.llm.invoke(prompt)
            result_text = response.content.strip()
            
            # Extract JSON
            start_idx = result_text.find('{')
            end_idx = result_text.rfind('}') + 1
            
            if start_idx == -1 or end_idx == 0:
                raise ValueError("No JSON found in response")
            
            json_str = result_text[start_idx:end_idx]
            result = json.loads(json_str)
            
            return {
                'hallucination_detected': result.get('hallucination_detected', False),
                'hallucination_confidence': result.get('confidence', 0) / 10,
                'hallucinated_parts': result.get('hallucinated_parts', 'none'),
                'hallucination_explanation': result.get('explanation', ''),
                'llm_available': True
            }
            
        except Exception as e:
            print(f"Error in hallucination detection: {e}")
            return {
                'llm_available': True,
                'error': str(e),
                'hallucination_detected': False
            }


# Global instance
_llm_judge = None

def get_llm_judge() -> LLMJudge:
    """Get or create global LLM judge instance"""
    global _llm_judge
    if _llm_judge is None:
        _llm_judge = LLMJudge()
    return _llm_judge
