"""
Comprehensive In-Depth Analysis of Benchmark Results
Uses the JSON results file for accurate analysis
"""

import json
import statistics
from collections import defaultdict, Counter
from typing import List, Dict


class BenchmarkAnalyzer:
    def __init__(self, results_file: str):
        """Load benchmark results"""
        print(f"="*70)
        print(f"LOADING BENCHMARK RESULTS")
        print(f"="*70)
        print(f"File: {results_file}\n")
        
        with open(results_file, 'r') as f:
            data = json.load(f)
        
        self.metadata = data.get('metadata', {})
        self.results = data.get('results', [])
        
        print(f"Test Cases: {len(self.results)}")
        print(f"Completed: {self.metadata.get('completed_at', 'N/A')}")
        print(f"Duration: {self.metadata.get('total_time_minutes', 0):.1f} minutes\n")
    
    def analyze_recommendations(self):
        """Detailed recommendation analysis"""
        print("="*70)
        print("RECOMMENDATION SYSTEM ANALYSIS")
        print("="*70)
        
        rec_data = {
            'overall_quality': [],
            'relevance_score': [],
            'diversity_score': [],
            'llm_overall': [],
            'response_time': [],
            'num_recommendations': [],
            # Advanced metrics
            'advanced_ndcg': [],
            'advanced_ild': [],
            'advanced_novelty': [],
            'advanced_serendipity': [],
            'success': 0,
            'failed': 0
        }
        
        all_cars = []
        
        for test in self.results:
            rec = test.get('recommendation_results', {})
            
            if rec.get('success'):
                rec_data['success'] += 1
                metrics = rec.get('quality_metrics', {})
                
                for key in ['overall_quality', 'relevance_score', 'diversity_score', 'llm_overall',
                           'advanced_ndcg', 'advanced_ild', 'advanced_novelty', 'advanced_serendipity']:
                    if key in metrics:
                        rec_data[key].append(metrics[key])
                
                rec_data['response_time'].append(rec.get('response_time', 0))
                rec_data['num_recommendations'].append(rec.get('num_recommendations', 0))
                
                # Collect cars
                recs = rec.get('recommendations', [])
                for r in recs:
                    car = r.get('car', {})
                    if car:
                        all_cars.append({
                            'name': car.get('variant', 'Unknown'),
                            'price': car.get('price', 'N/A'),
                            'fuel': car.get('Fuel Type', 'N/A'),
                            'body': car.get('Body Type', 'N/A'),
                            'score': r.get('score', 0)
                        })
            else:
                rec_data['failed'] += 1
        
        # Print statistics
        print(f"\nSuccess Rate: {rec_data['success']}/{len(self.results)} ({rec_data['success']/len(self.results)*100:.1f}%)")
        print(f"Total Cars Recommended: {len(all_cars)}\n")
        
        # Metrics statistics
        metrics_to_analyze = ['overall_quality', 'relevance_score', 'diversity_score', 'llm_overall', 
                             'response_time', 'advanced_ndcg', 'advanced_ild', 'advanced_novelty', 'advanced_serendipity']
        
        for metric in metrics_to_analyze:
            if rec_data[metric]:
                vals = rec_data[metric]
                print(f"{metric.replace('_', ' ').title()}:")
                print(f"  Mean:   {statistics.mean(vals):.4f}")
                print(f"  Median: {statistics.median(vals):.4f}")
                print(f"  Std:    {statistics.stdev(vals) if len(vals) > 1 else 0:.4f}")
                print(f"  Range:  [{min(vals):.4f}, {max(vals):.4f}]")
                
                # Quality bins
                if 'quality' in metric or 'score' in metric:
                    excellent = sum(1 for v in vals if v > 0.8)
                    good = sum(1 for v in vals if 0.6 < v <= 0.8)
                    moderate = sum(1 for v in vals if 0.4 < v <= 0.6)
                    poor = sum(1 for v in vals if v <= 0.4)
                    print(f"  Distribution:")
                    print(f"    Excellent (>0.8): {excellent} ({excellent/len(vals)*100:.1f}%)")
                    print(f"    Good (0.6-0.8): {good} ({good/len(vals)*100:.1f}%)")
                    print(f"    Moderate (0.4-0.6): {moderate} ({moderate/len(vals)*100:.1f}%)")
                    print(f"    Poor (<=0.4): {poor} ({poor/len(vals)*100:.1f}%)")
                
                print()
        
        # Car analysis
        if all_cars:
            print("Car Recommendation Analysis:")
            
            # Most recommended
            car_names = [c['name'] for c in all_cars]
            car_counts = Counter(car_names)
            print(f"\n  Top 10 Most Recommended:")
            for name, count in car_counts.most_common(10):
                print(f"    {count}x {name}")
            
            # Fuel type distribution
            fuel_types = Counter([c['fuel'] for c in all_cars if c['fuel'] != 'N/A'])
            print(f"\n  Fuel Type Distribution:")
            for fuel, count in fuel_types.most_common():
                print(f"    {fuel}: {count} ({count/len(all_cars)*100:.1f}%)")
            
            # Body type distribution
            body_types = Counter([c['body'] for c in all_cars if c['body'] != 'N/A'])
            print(f"\n  Body Type Distribution:")
            for body, count in body_types.most_common():
                print(f"    {body}: {count} ({count/len(all_cars)*100:.1f}%)")
            
            print()
    
    def analyze_qa(self):
        """Detailed Q&A analysis"""
        print("="*70)
        print("Q&A SYSTEM ANALYSIS")
        print("="*70)
        
        qa_data = {
            'overall_quality': [],
            'llm_overall': [],
            'relevance_score': [],
            'groundedness_score': [],
            'response_time': [],
            'answer_length': [],
            'hallucinations': 0,
            'success': 0,
            'failed': 0
        }
        
        questions = []
        
        for test in self.results:
            for qa in test.get('qa_results', []):
                if qa.get('success'):
                    qa_data['success'] += 1
                    metrics = qa.get('quality_metrics', {})
                    
                    for key in ['overall_quality', 'llm_overall', 'relevance_score', 'groundedness_score', 'answer_length']:
                        if key in metrics:
                            qa_data[key].append(metrics[key])
                    
                    if metrics.get('hallucination_detected'):
                        qa_data['hallucinations'] += 1
                    
                    qa_data['response_time'].append(qa.get('response_time', 0))
                    questions.append(qa.get('question', ''))
                else:
                    qa_data['failed'] += 1
        
        total_qa = qa_data['success'] + qa_data['failed']
        
        print(f"\nTotal Questions: {total_qa}")
        print(f"Success Rate: {qa_data['success']}/{total_qa} ({qa_data['success']/total_qa*100:.1f}%)")
        print(f"Hallucination Rate: {qa_data['hallucinations']}/{qa_data['success']} ({qa_data['hallucinations']/qa_data['success']*100 if qa_data['success'] > 0 else 0:.1f}%)\n")
        
        # Metrics statistics
        for metric in ['overall_quality', 'llm_overall', 'relevance_score', 'groundedness_score', 'response_time', 'answer_length']:
            if qa_data[metric]:
                vals = qa_data[metric]
                print(f"{metric.replace('_', ' ').title()}:")
                print(f"  Mean:   {statistics.mean(vals):.4f}")
                print(f"  Median: {statistics.median(vals):.4f}")
                print(f"  Std:    {statistics.stdev(vals) if len(vals) > 1 else 0:.4f}")
                print(f"  Range:  [{min(vals):.4f}, {max(vals):.4f}]")
                
                # Quality bins for quality metrics
                if 'quality' in metric or metric in ['llm_overall', 'relevance_score', 'groundedness_score']:
                    excellent = sum(1 for v in vals if v > 0.8)
                    good = sum(1 for v in vals if 0.6 < v <= 0.8)
                    moderate = sum(1 for v in vals if 0.4 < v <= 0.6)
                    poor = sum(1 for v in vals if v <= 0.4)
                    print(f"  Distribution:")
                    print(f"    Excellent (>0.8): {excellent} ({excellent/len(vals)*100:.1f}%)")
                    print(f"    Good (0.6-0.8): {good} ({good/len(vals)*100:.1f}%)")
                    print(f"    Moderate (0.4-0.6): {moderate} ({moderate/len(vals)*100:.1f}%)")
                    print(f"    Poor (<=0.4): {poor} ({poor/len(vals)*100:.1f}%)")
                
                # Speed categories for response time
                if metric == 'response_time':
                    very_fast = sum(1 for v in vals if v < 3)
                    fast = sum(1 for v in vals if 3 <= v < 5)
                    moderate = sum(1 for v in vals if 5 <= v < 10)
                    slow = sum(1 for v in vals if v >= 10)
                    print(f"  Speed Distribution:")
                    print(f"    Very Fast (<3s): {very_fast} ({very_fast/len(vals)*100:.1f}%)")
                    print(f"    Fast (3-5s): {fast} ({fast/len(vals)*100:.1f}%)")
                    print(f"    Moderate (5-10s): {moderate} ({moderate/len(vals)*100:.1f}%)")
                    print(f"    Slow (>10s): {slow} ({slow/len(vals)*100:.1f}%)")
                
                print()
        
        # Question pattern analysis
        if questions:
            print("Question Pattern Analysis:")
            patterns = {
                'What': sum(1 for q in questions if q.lower().startswith('what')),
                'Which': sum(1 for q in questions if q.lower().startswith('which')),
                'How': sum(1 for q in questions if q.lower().startswith('how')),
                'Are/Do/Does': sum(1 for q in questions if any(q.lower().startswith(w) for w in ['are', 'do', 'does'])),
                'Tell': sum(1 for q in questions if q.lower().startswith('tell')),
            }
            patterns['Other'] = len(questions) - sum(patterns.values())
            
            for pattern, count in sorted(patterns.items(), key=lambda x: x[1], reverse=True):
                if count > 0:
                    print(f"  {pattern}: {count} ({count/len(questions)*100:.1f}%)")
            print()
    
    def analyze_personas(self):
        """Analyze by persona"""
        print("="*70)
        print("PERSONA-WISE ANALYSIS")
        print("="*70)
        
        persona_stats = defaultdict(lambda: {
            'count': 0,
            'rec_quality': [],
            'rec_diversity': [],
            'qa_quality': [],
            'sample_prefs': None  # Store one sample
        })
        
        for test in self.results:
            persona = test.get('persona', 'Unknown')
            persona_stats[persona]['count'] += 1
            
            # Store sample preferences (first one for this persona)
            if not persona_stats[persona]['sample_prefs']:
                prefs = test.get('preferences', {})
                persona_stats[persona]['sample_prefs'] = {
                    'budget': f"₹{prefs.get('min_budget', 0):,}-₹{prefs.get('max_budget', 0):,}",
                    'fuel': prefs.get('fuel_type', 'Any'),
                    'body': prefs.get('body_type', 'Any'),
                    'seating': prefs.get('seating', 'Any')
                }
            
            # Recommendation quality
            rec = test.get('recommendation_results', {})
            if rec.get('success'):
                metrics = rec.get('quality_metrics', {})
                if 'overall_quality' in metrics:
                    persona_stats[persona]['rec_quality'].append(metrics['overall_quality'])
                if 'diversity_score' in metrics:
                    persona_stats[persona]['rec_diversity'].append(metrics['diversity_score'])
            
            # Q&A quality
            for qa in test.get('qa_results', []):
                if qa.get('success'):
                    metrics = qa.get('quality_metrics', {})
                    if 'overall_quality' in metrics:
                        persona_stats[persona]['qa_quality'].append(metrics['overall_quality'])
        
        # Create sorted list
        persona_list = []
        for persona, stats in persona_stats.items():
            avg_rec = statistics.mean(stats['rec_quality']) if stats['rec_quality'] else 0
            avg_div = statistics.mean(stats['rec_diversity']) if stats['rec_diversity'] else 0
            avg_qa = statistics.mean(stats['qa_quality']) if stats['qa_quality'] else 0
            persona_list.append((persona, stats['count'], avg_rec, avg_div, avg_qa))
        
        persona_list.sort(key=lambda x: x[2], reverse=True)
        
        print(f"\nTotal Personas: {len(persona_list)}\n")
        print(f"{'Persona':<45} {'Tests':<7} {'Rec Qual':<10} {'Diversity':<10} {'Q&A Qual':<10}")
        print("-"*90)
        
        for persona, count, rec_q, div, qa_q in persona_list:
            print(f"{persona:<45} {count:<7} {rec_q:<10.3f} {div:<10.3f} {qa_q:<10.3f}")
        
        # Show sample preferences for top 5 and bottom 5 personas
        print(f"\n{'='*70}")
        print("SAMPLE USER PREFERENCES BY PERSONA")
        print("="*70)
        print("\nTop 5 Performing Personas:")
        for persona, count, rec_q, div, qa_q in persona_list[:5]:
            prefs = persona_stats[persona]['sample_prefs']
            if prefs:
                print(f"\n{persona} (Quality: {rec_q:.3f}):")
                print(f"  Budget: {prefs['budget']}, Fuel: {prefs['fuel']}, Body: {prefs['body']}, Seats: {prefs['seating']}")
        
        print("\n\nBottom 5 Performing Personas:")
        for persona, count, rec_q, div, qa_q in persona_list[-5:]:
            prefs = persona_stats[persona]['sample_prefs']
            if prefs:
                print(f"\n{persona} (Quality: {rec_q:.3f}):")
                print(f"  Budget: {prefs['budget']}, Fuel: {prefs['fuel']}, Body: {prefs['body']}, Seats: {prefs['seating']}")
        
        print()
    
    def generate_insights(self):
        """Generate insights"""
        print("="*70)
        print("KEY INSIGHTS & RECOMMENDATIONS")
        print("="*70)
        print()
        
        # Collect data
        rec_quality = []
        rec_diversity = []
        rec_ndcg = []
        rec_ild = []
        rec_novelty = []
        qa_quality = []
        rec_times = []
        qa_times = []
        
        for test in self.results:
            rec = test.get('recommendation_results', {})
            if rec.get('success'):
                metrics = rec.get('quality_metrics', {})
                if 'overall_quality' in metrics:
                    rec_quality.append(metrics['overall_quality'])
                if 'diversity_score' in metrics:
                    rec_diversity.append(metrics['diversity_score'])
                if 'advanced_ndcg' in metrics:
                    rec_ndcg.append(metrics['advanced_ndcg'])
                if 'advanced_ild' in metrics:
                    rec_ild.append(metrics['advanced_ild'])
                if 'advanced_novelty' in metrics:
                    rec_novelty.append(metrics['advanced_novelty'])
                rec_times.append(rec.get('response_time', 0))
            
            for qa in test.get('qa_results', []):
                if qa.get('success'):
                    metrics = qa.get('quality_metrics', {})
                    if 'overall_quality' in metrics:
                        qa_quality.append(metrics['overall_quality'])
                    qa_times.append(qa.get('response_time', 0))
        
        # Generate insights
        insights = []
        
        if rec_quality:
            avg = statistics.mean(rec_quality)
            if avg < 0.5:
                insights.append(f"⚠️  CRITICAL: Recommendation quality is LOW ({avg:.3f}). Immediate action needed.")
            elif avg < 0.7:
                insights.append(f"⚠️  Recommendation quality is MODERATE ({avg:.3f}). Room for improvement.")
            else:
                insights.append(f"✓ Recommendation quality is GOOD ({avg:.3f}).")
        
        if rec_diversity:
            avg = statistics.mean(rec_diversity)
            if avg < 0.3:
                insights.append(f"⚠️  Diversity is LOW ({avg:.3f}). Users see too similar cars.")
            else:
                insights.append(f"✓ Diversity is acceptable ({avg:.3f}).")
        
        # Advanced metrics insights
        if rec_ndcg:
            avg = statistics.mean(rec_ndcg)
            if avg < 0.5:
                insights.append(f"⚠️  NDCG@K is LOW ({avg:.3f}). Ranking quality needs improvement.")
            else:
                insights.append(f"✓ NDCG@K is good ({avg:.3f}). Ranking quality is solid.")
        
        if rec_ild:
            avg = statistics.mean(rec_ild)
            if avg < 0.3:
                insights.append(f"⚠️  ILD (diversity) is LOW ({avg:.3f}). Recommendations too similar.")
            else:
                insights.append(f"✓ ILD shows good diversity ({avg:.3f}).")
        
        if rec_novelty:
            avg = statistics.mean(rec_novelty)
            if avg < 0.3:
                insights.append(f"⚠️  Novelty is LOW ({avg:.3f}). Consider unexpected but relevant options.")
            else:
                insights.append(f"✓ Novelty is acceptable ({avg:.3f}).")
        
        if qa_quality:
            avg = statistics.mean(qa_quality)
            if avg < 0.7:
                insights.append(f"⚠️  Q&A quality needs improvement ({avg:.3f}).")
            else:
                insights.append(f"✓ Q&A quality is EXCELLENT ({avg:.3f}).")
        
        if rec_times:
            avg = statistics.mean(rec_times)
            slow = sum(1 for t in rec_times if t > 3)
            if avg > 3:
                insights.append(f"⚠️  Recommendation response time is SLOW ({avg:.2f}s avg).")
            if slow > len(rec_times) * 0.1:
                insights.append(f"⚠️  {slow} recommendations took >3s. Consider optimization.")
        
        if qa_times:
            avg = statistics.mean(qa_times)
            slow = sum(1 for t in qa_times if t > 10)
            if avg > 8:
                insights.append(f"⚠️  Q&A response time is SLOW ({avg:.2f}s avg).")
            if slow > 0:
                insights.append(f"⚠️  {slow} Q&A responses took >10s. Consider caching.")
        
        for i, insight in enumerate(insights, 1):
            print(f"{i}. {insight}")
        
        print()
        print("="*70)
    
    def run_full_analysis(self):
        """Run complete analysis"""
        self.analyze_recommendations()
        self.analyze_qa()
        self.analyze_personas()
        self.generate_insights()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        results_file = "results/benchmark_results_20260122_190502.json"
        print(f"Using default: {results_file}\n")
    else:
        results_file = sys.argv[1]
    
    analyzer = BenchmarkAnalyzer(results_file)
    analyzer.run_full_analysis()
    
    print("\n✓ Analysis Complete!")
