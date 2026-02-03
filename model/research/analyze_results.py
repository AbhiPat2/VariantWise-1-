"""
Comprehensive Analysis of Benchmark Results
Generates statistics, insights, and prepares data for PDF/Excel export
"""

import json
import numpy as np
from datetime import datetime
from collections import defaultdict, Counter
from typing import Dict, List, Any


class BenchmarkAnalyzer:
    def __init__(self, results_file: str):
        """Load and prepare benchmark results for analysis"""
        print(f"Loading results from: {results_file}")
        
        with open(results_file, 'r') as f:
            data = json.load(f)
        
        self.metadata = data.get('metadata', {})
        self.results = data.get('results', [])
        
        print(f"Loaded {len(self.results)} test cases")
        print(f"Completed at: {self.metadata.get('completed_at', 'N/A')}")
        print(f"Total time: {self.metadata.get('total_time_minutes', 0):.1f} minutes")
        print()
    
    def analyze_recommendations(self) -> Dict:
        """Analyze recommendation performance"""
        print("=" * 70)
        print("RECOMMENDATION ANALYSIS")
        print("=" * 70)
        
        rec_metrics = {
            'overall_quality': [],
            'relevance_score': [],
            'diversity_score': [],
            'llm_overall': [],
            'response_time': [],
            'num_recommendations': [],
            'success_count': 0,
            'failure_count': 0
        }
        
        for test in self.results:
            rec_result = test.get('recommendation_results', {})
            
            if rec_result.get('success'):
                rec_metrics['success_count'] += 1
                metrics = rec_result.get('quality_metrics', {})
                
                for key in ['overall_quality', 'relevance_score', 'diversity_score', 'llm_overall']:
                    if key in metrics:
                        rec_metrics[key].append(metrics[key])
                
                rec_metrics['response_time'].append(rec_result.get('response_time', 0))
                rec_metrics['num_recommendations'].append(rec_result.get('num_recommendations', 0))
            else:
                rec_metrics['failure_count'] += 1
        
        # Calculate statistics
        analysis = {
            'total_tests': len(self.results),
            'success_rate': rec_metrics['success_count'] / len(self.results) * 100,
            'failure_rate': rec_metrics['failure_count'] / len(self.results) * 100,
            'metrics': {}
        }
        
        for key in ['overall_quality', 'relevance_score', 'diversity_score', 'llm_overall', 'response_time']:
            if rec_metrics[key]:
                values = rec_metrics[key]
                analysis['metrics'][key] = {
                    'mean': np.mean(values),
                    'std': np.std(values),
                    'min': np.min(values),
                    'max': np.max(values),
                    'median': np.median(values),
                    'p25': np.percentile(values, 25),
                    'p75': np.percentile(values, 75)
                }
        
        # Print summary
        print(f"\nSuccess Rate: {analysis['success_rate']:.1f}%")
        print(f"Total Recommendations Generated: {rec_metrics['success_count'] * 5}")
        print()
        
        print("Metric Statistics:")
        print("-" * 70)
        for metric_name, stats in analysis['metrics'].items():
            print(f"\n{metric_name.replace('_', ' ').title()}:")
            print(f"  Mean:   {stats['mean']:.3f}")
            print(f"  Std:    {stats['std']:.3f}")
            print(f"  Range:  [{stats['min']:.3f}, {stats['max']:.3f}]")
            print(f"  Median: {stats['median']:.3f}")
        
        return analysis
    
    def analyze_qa(self) -> Dict:
        """Analyze Q&A performance"""
        print("\n" + "=" * 70)
        print("Q&A ANALYSIS")
        print("=" * 70)
        
        qa_metrics = {
            'overall_quality': [],
            'llm_overall': [],
            'relevance_score': [],
            'groundedness_score': [],
            'hallucination_detected': [],
            'response_time': [],
            'answer_length': [],
            'success_count': 0,
            'failure_count': 0
        }
        
        for test in self.results:
            for qa in test.get('qa_results', []):
                if qa.get('success'):
                    qa_metrics['success_count'] += 1
                    metrics = qa.get('quality_metrics', {})
                    
                    for key in ['overall_quality', 'llm_overall', 'relevance_score', 
                               'groundedness_score', 'answer_length']:
                        if key in metrics:
                            qa_metrics[key].append(metrics[key])
                    
                    if 'hallucination_detected' in metrics:
                        qa_metrics['hallucination_detected'].append(
                            1 if metrics['hallucination_detected'] else 0
                        )
                    
                    qa_metrics['response_time'].append(qa.get('response_time', 0))
                else:
                    qa_metrics['failure_count'] += 1
        
        # Calculate statistics
        total_qa = qa_metrics['success_count'] + qa_metrics['failure_count']
        analysis = {
            'total_questions': total_qa,
            'success_rate': qa_metrics['success_count'] / total_qa * 100 if total_qa > 0 else 0,
            'failure_rate': qa_metrics['failure_count'] / total_qa * 100 if total_qa > 0 else 0,
            'hallucination_rate': (sum(qa_metrics['hallucination_detected']) / 
                                  len(qa_metrics['hallucination_detected']) * 100) 
                                  if qa_metrics['hallucination_detected'] else 0,
            'metrics': {}
        }
        
        for key in ['overall_quality', 'llm_overall', 'relevance_score', 
                   'groundedness_score', 'response_time', 'answer_length']:
            if qa_metrics[key]:
                values = qa_metrics[key]
                analysis['metrics'][key] = {
                    'mean': np.mean(values),
                    'std': np.std(values),
                    'min': np.min(values),
                    'max': np.max(values),
                    'median': np.median(values),
                    'p25': np.percentile(values, 25),
                    'p75': np.percentile(values, 75)
                }
        
        # Print summary
        print(f"\nTotal Questions: {total_qa}")
        print(f"Success Rate: {analysis['success_rate']:.1f}%")
        print(f"Hallucination Rate: {analysis['hallucination_rate']:.1f}%")
        print()
        
        print("Metric Statistics:")
        print("-" * 70)
        for metric_name, stats in analysis['metrics'].items():
            print(f"\n{metric_name.replace('_', ' ').title()}:")
            print(f"  Mean:   {stats['mean']:.3f}")
            print(f"  Std:    {stats['std']:.3f}")
            print(f"  Range:  [{stats['min']:.3f}, {stats['max']:.3f}]")
            print(f"  Median: {stats['median']:.3f}")
        
        return analysis
    
    def analyze_personas(self) -> Dict:
        """Analyze performance by user persona"""
        print("\n" + "=" * 70)
        print("PERSONA ANALYSIS")
        print("=" * 70)
        
        persona_data = defaultdict(lambda: {
            'count': 0,
            'rec_quality': [],
            'qa_quality': [],
            'preferences': []
        })
        
        for test in self.results:
            persona = test.get('persona', 'Unknown')
            persona_data[persona]['count'] += 1
            
            # Recommendation quality
            rec_result = test.get('recommendation_results', {})
            if rec_result.get('success'):
                rec_quality = rec_result.get('quality_metrics', {}).get('overall_quality')
                if rec_quality is not None:
                    persona_data[persona]['rec_quality'].append(rec_quality)
            
            # Q&A quality
            for qa in test.get('qa_results', []):
                if qa.get('success'):
                    qa_quality = qa.get('quality_metrics', {}).get('overall_quality')
                    if qa_quality is not None:
                        persona_data[persona]['qa_quality'].append(qa_quality)
            
            # Store preferences
            persona_data[persona]['preferences'].append(test.get('preferences', {}))
        
        # Calculate averages
        persona_analysis = {}
        for persona, data in persona_data.items():
            persona_analysis[persona] = {
                'count': data['count'],
                'avg_rec_quality': np.mean(data['rec_quality']) if data['rec_quality'] else 0,
                'avg_qa_quality': np.mean(data['qa_quality']) if data['qa_quality'] else 0
            }
        
        # Print summary
        print(f"\nTotal Personas: {len(persona_analysis)}")
        print()
        for persona, stats in sorted(persona_analysis.items(), 
                                     key=lambda x: x[1]['avg_rec_quality'], 
                                     reverse=True):
            print(f"{persona}:")
            print(f"  Tests: {stats['count']}")
            print(f"  Avg Rec Quality: {stats['avg_rec_quality']:.3f}")
            print(f"  Avg Q&A Quality: {stats['avg_qa_quality']:.3f}")
            print()
        
        return persona_analysis
    
    def analyze_preferences(self) -> Dict:
        """Analyze performance by preference patterns"""
        print("=" * 70)
        print("PREFERENCE PATTERN ANALYSIS")
        print("=" * 70)
        
        # Collect preference patterns
        fuel_types = Counter()
        body_types = Counter()
        transmissions = Counter()
        budget_ranges = []
        
        for test in self.results:
            prefs = test.get('preferences', {})
            
            if 'fuel_type' in prefs:
                fuel_types[prefs['fuel_type']] += 1
            if 'body_type' in prefs:
                body_types[prefs['body_type']] += 1
            if 'transmission' in prefs:
                transmissions[prefs['transmission']] += 1
            
            min_budget = prefs.get('min_budget', 0)
            max_budget = prefs.get('max_budget', 0)
            if min_budget and max_budget:
                budget_ranges.append((min_budget + max_budget) / 2)
        
        analysis = {
            'fuel_type_distribution': dict(fuel_types),
            'body_type_distribution': dict(body_types),
            'transmission_distribution': dict(transmissions),
            'avg_budget': np.mean(budget_ranges) if budget_ranges else 0,
            'budget_std': np.std(budget_ranges) if budget_ranges else 0
        }
        
        print(f"\nFuel Type Distribution:")
        for fuel, count in fuel_types.most_common():
            print(f"  {fuel}: {count} ({count/len(self.results)*100:.1f}%)")
        
        print(f"\nBody Type Distribution:")
        for body, count in body_types.most_common():
            print(f"  {body}: {count} ({count/len(self.results)*100:.1f}%)")
        
        print(f"\nTransmission Distribution:")
        for trans, count in transmissions.most_common():
            print(f"  {trans}: {count} ({count/len(self.results)*100:.1f}%)")
        
        print(f"\nBudget Analysis:")
        print(f"  Average: Rs.{analysis['avg_budget']:,.0f}")
        print(f"  Std Dev: Rs.{analysis['budget_std']:,.0f}")
        
        return analysis
    
    def generate_insights(self, rec_analysis, qa_analysis, persona_analysis) -> List[str]:
        """Generate actionable insights from the analysis"""
        print("\n" + "=" * 70)
        print("KEY INSIGHTS & RECOMMENDATIONS")
        print("=" * 70)
        
        insights = []
        
        # Recommendation insights
        rec_quality = rec_analysis['metrics'].get('overall_quality', {}).get('mean', 0)
        if rec_quality < 0.5:
            insights.append("⚠ LOW: Recommendation quality is below 50%. Review matching algorithm.")
        elif rec_quality < 0.7:
            insights.append("⚠ MODERATE: Recommendation quality could be improved. Consider tuning weights.")
        else:
            insights.append("✓ GOOD: Recommendation quality is above 70%.")
        
        # Diversity insights
        diversity = rec_analysis['metrics'].get('diversity_score', {}).get('mean', 0)
        if diversity < 0.3:
            insights.append("⚠ LOW: Diversity is low. Users may see too many similar cars.")
        elif diversity > 0.6:
            insights.append("✓ GOOD: Recommendations show good diversity.")
        
        # Q&A insights
        qa_quality = qa_analysis['metrics'].get('overall_quality', {}).get('mean', 0)
        if qa_quality < 0.7:
            insights.append("⚠ MODERATE: Q&A quality needs improvement. Review context retrieval.")
        else:
            insights.append("✓ EXCELLENT: Q&A quality is above 70%.")
        
        # Hallucination insights
        hallucination_rate = qa_analysis.get('hallucination_rate', 0)
        if hallucination_rate > 10:
            insights.append(f"⚠ HIGH: Hallucination rate is {hallucination_rate:.1f}%. Improve grounding.")
        elif hallucination_rate > 5:
            insights.append(f"⚠ MODERATE: Hallucination rate is {hallucination_rate:.1f}%. Monitor closely.")
        else:
            insights.append(f"✓ LOW: Hallucination rate is {hallucination_rate:.1f}%.")
        
        # Response time insights
        avg_rec_time = rec_analysis['metrics'].get('response_time', {}).get('mean', 0)
        avg_qa_time = qa_analysis['metrics'].get('response_time', {}).get('mean', 0)
        
        if avg_rec_time > 3:
            insights.append(f"⚠ SLOW: Recommendation response time is {avg_rec_time:.1f}s. Optimize.")
        if avg_qa_time > 10:
            insights.append(f"⚠ SLOW: Q&A response time is {avg_qa_time:.1f}s. Consider caching.")
        
        # Print insights
        for i, insight in enumerate(insights, 1):
            print(f"{i}. {insight}")
        
        print()
        return insights
    
    def get_summary_data(self) -> Dict:
        """Get all analysis data for export"""
        rec_analysis = self.analyze_recommendations()
        qa_analysis = self.analyze_qa()
        persona_analysis = self.analyze_personas()
        pref_analysis = self.analyze_preferences()
        insights = self.generate_insights(rec_analysis, qa_analysis, persona_analysis)
        
        return {
            'metadata': self.metadata,
            'recommendation_analysis': rec_analysis,
            'qa_analysis': qa_analysis,
            'persona_analysis': persona_analysis,
            'preference_analysis': pref_analysis,
            'insights': insights,
            'raw_results': self.results
        }


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python analyze_results.py <results_file.json>")
        sys.exit(1)
    
    results_file = sys.argv[1]
    
    analyzer = BenchmarkAnalyzer(results_file)
    summary = analyzer.get_summary_data()
    
    # Save analysis summary
    output_file = results_file.replace('.json', '_analysis.json')
    with open(output_file, 'w') as f:
        json.dump(summary, f, indent=2, default=str)
    
    print("=" * 70)
    print(f"Analysis saved to: {output_file}")
    print("=" * 70)
