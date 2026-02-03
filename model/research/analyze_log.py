"""
In-depth Analysis of benchmark_full_100.log
Extracts metrics, patterns, and insights directly from the log file
"""

import re
from collections import defaultdict, Counter
import statistics
from typing import List, Dict, Tuple


class LogAnalyzer:
    def __init__(self, log_file: str):
        """Initialize analyzer with log file"""
        print(f"Loading log file: {log_file}")
        
        with open(log_file, 'r', encoding='utf-8') as f:
            self.log_content = f.read()
        
        self.lines = self.log_content.split('\n')
        print(f"Loaded {len(self.lines)} lines\n")
        
        # Storage for parsed data
        self.test_cases = []
        self.recommendations = []
        self.qa_interactions = []
        self.metrics = {
            'recommendation': defaultdict(list),
            'qa': defaultdict(list)
        }
    
    def parse_log(self):
        """Parse the entire log file"""
        print("="*70)
        print("PARSING LOG FILE")
        print("="*70)
        
        current_test = None
        current_rec = None
        in_qa = False
        current_question = None
        
        i = 0
        while i < len(self.lines):
            line = self.lines[i].strip()
            
            # Test case detection
            if "Test Case #" in line:
                # Extract test number and persona
                match = re.search(r'Test Case #(\d+):\s*(.+)', line)
                if match:
                    test_num = int(match.group(1))
                    persona = match.group(2)
                    current_test = {
                        'test_id': test_num,
                        'persona': persona,
                        'recommendations': [],
                        'qa': []
                    }
                    self.test_cases.append(current_test)
            
            # Recommendation metrics
            elif "Getting recommendations..." in line:
                current_rec = {'cars': []}
            
            elif "Got" in line and "recommendations" in line:
                match = re.search(r'Got (\d+) recommendations', line)
                if match and current_rec:
                    current_rec['count'] = int(match.group(1))
            
            elif "Response time:" in line and current_rec:
                match = re.search(r'Response time:\s*([\d.]+)s', line)
                if match:
                    current_rec['response_time'] = float(match.group(1))
                    self.metrics['recommendation']['response_time'].append(float(match.group(1)))
            
            elif "Overall Quality:" in line:
                match = re.search(r'Overall Quality:\s*([\d.]+)', line)
                if match:
                    value = float(match.group(1))
                    if current_rec and 'response_time' in current_rec:
                        current_rec['overall_quality'] = value
                        self.metrics['recommendation']['overall_quality'].append(value)
                    elif in_qa:
                        self.metrics['qa']['overall_quality'].append(value)
            
            elif "Relevance:" in line:
                match = re.search(r'Relevance:\s*([\d.]+)', line)
                if match and current_rec:
                    current_rec['relevance'] = float(match.group(1))
                    self.metrics['recommendation']['relevance'].append(float(match.group(1)))
            
            elif "Diversity:" in line:
                match = re.search(r'Diversity:\s*([\d.]+)', line)
                if match and current_rec:
                    current_rec['diversity'] = float(match.group(1))
                    self.metrics['recommendation']['diversity'].append(float(match.group(1)))
                    
                    # End of recommendation block
                    if current_test:
                        current_test['recommendations'].append(current_rec)
                        self.recommendations.append(current_rec)
                    current_rec = None
            
            # Car details
            elif re.match(r'\s+\d+\.\s+[A-Z]', line):
                # Car name
                match = re.search(r'\d+\.\s+(.+)', line)
                if match and current_rec:
                    car_name = match.group(1).strip()
                    current_car = {'name': car_name}
                    
                    # Next line has price, fuel, transmission
                    if i + 1 < len(self.lines):
                        next_line = self.lines[i + 1].strip()
                        price_match = re.search(r'Price:\s*([^\|]+)', next_line)
                        fuel_match = re.search(r'Fuel:\s*([^\|]+)', next_line)
                        trans_match = re.search(r'Trans:\s*(.+)', next_line)
                        
                        if price_match:
                            current_car['price'] = price_match.group(1).strip()
                        if fuel_match:
                            current_car['fuel'] = fuel_match.group(1).strip()
                        if trans_match:
                            current_car['transmission'] = trans_match.group(1).strip()
                    
                    # Line after that has match score
                    if i + 2 < len(self.lines):
                        score_line = self.lines[i + 2].strip()
                        score_match = re.search(r'Match Score:\s*([\d.]+)', score_line)
                        if score_match:
                            current_car['score'] = float(score_match.group(1))
                    
                    if 'cars' in current_rec:
                        current_rec['cars'].append(current_car)
            
            # Q&A section
            elif "Asking" in line and "questions" in line:
                in_qa = True
            
            elif "Q1:" in line or "Q2:" in line or "Q3:" in line:
                # Question
                match = re.search(r'Q\d+:\s*(.+)', line)
                if match:
                    current_question = {
                        'question': match.group(1),
                        'metrics': {}
                    }
            
            elif "Answer generated" in line:
                match = re.search(r'Answer generated \(([\d.]+)s\)', line)
                if match and current_question:
                    current_question['response_time'] = float(match.group(1))
                    self.metrics['qa']['response_time'].append(float(match.group(1)))
            
            elif "Answer:" in line:
                # Extract answer preview (must be after Answer generated)
                if current_question and 'response_time' in current_question:
                    answer_match = re.search(r'Answer:\s*(.+)', line)
                    if answer_match:
                        current_question['answer'] = answer_match.group(1)
            
            elif "Overall Quality:" in line:
                # Check if this is Q&A (more indentation) or recommendation (less indentation)
                if current_question and 'answer' in current_question and line.startswith('      '):
                    # This is Q&A quality (7+ spaces)
                    match = re.search(r'Overall Quality:\s*([\d.]+)', line)
                    if match:
                        current_question['metrics']['overall_quality'] = float(match.group(1))
                        self.metrics['qa']['overall_quality'].append(float(match.group(1)))
                        
                        # End of Q&A block
                        if current_test:
                            current_test['qa'].append(current_question)
                            self.qa_interactions.append(current_question)
                        current_question = None
            
            i += 1
        
        print(f"Parsed {len(self.test_cases)} test cases")
        print(f"Parsed {len(self.recommendations)} recommendation sets")
        print(f"Parsed {len(self.qa_interactions)} Q&A interactions")
        print()
    
    def analyze_recommendations(self):
        """Analyze recommendation performance"""
        print("="*70)
        print("RECOMMENDATION ANALYSIS")
        print("="*70)
        
        rec_metrics = self.metrics['recommendation']
        
        if not rec_metrics['overall_quality']:
            print("No recommendation metrics found")
            return
        
        print(f"\nTotal Recommendation Sets: {len(self.recommendations)}")
        print(f"Total Cars Recommended: {sum(len(r.get('cars', [])) for r in self.recommendations)}")
        print()
        
        # Statistical analysis
        metrics_to_analyze = ['overall_quality', 'relevance', 'diversity', 'response_time']
        
        for metric in metrics_to_analyze:
            if metric in rec_metrics and rec_metrics[metric]:
                values = rec_metrics[metric]
                print(f"{metric.replace('_', ' ').title()}:")
                print(f"  Mean:   {statistics.mean(values):.4f}")
                print(f"  Median: {statistics.median(values):.4f}")
                print(f"  Std:    {statistics.stdev(values) if len(values) > 1 else 0:.4f}")
                print(f"  Min:    {min(values):.4f}")
                print(f"  Max:    {max(values):.4f}")
                print()
        
        # Quality distribution
        print("Quality Distribution:")
        quality_ranges = {
            'Excellent (>0.8)': 0,
            'Good (0.6-0.8)': 0,
            'Moderate (0.4-0.6)': 0,
            'Poor (<0.4)': 0
        }
        
        for q in rec_metrics['overall_quality']:
            if q > 0.8:
                quality_ranges['Excellent (>0.8)'] += 1
            elif q > 0.6:
                quality_ranges['Good (0.6-0.8)'] += 1
            elif q > 0.4:
                quality_ranges['Moderate (0.4-0.6)'] += 1
            else:
                quality_ranges['Poor (<0.4)'] += 1
        
        for range_name, count in quality_ranges.items():
            pct = (count / len(rec_metrics['overall_quality'])) * 100
            print(f"  {range_name}: {count} ({pct:.1f}%)")
        print()
        
        # Car analysis
        all_cars = []
        for rec in self.recommendations:
            all_cars.extend(rec.get('cars', []))
        
        if all_cars:
            print(f"Car Details:")
            print(f"  Total unique recommendations: {len(all_cars)}")
            
            # Most recommended cars
            car_names = [c['name'] for c in all_cars if 'name' in c]
            if car_names:
                car_counts = Counter(car_names)
                print(f"\n  Top 10 Most Recommended Cars:")
                for car, count in car_counts.most_common(10):
                    print(f"    {count}x: {car}")
            
            # Fuel type distribution
            fuel_types = [c['fuel'] for c in all_cars if 'fuel' in c]
            if fuel_types:
                fuel_counts = Counter(fuel_types)
                print(f"\n  Fuel Type Distribution:")
                for fuel, count in fuel_counts.most_common():
                    pct = (count / len(fuel_types)) * 100
                    print(f"    {fuel}: {count} ({pct:.1f}%)")
        
        print()
    
    def analyze_qa(self):
        """Analyze Q&A performance"""
        print("="*70)
        print("Q&A ANALYSIS")
        print("="*70)
        
        qa_metrics = self.metrics['qa']
        
        if not self.qa_interactions:
            print("No Q&A interactions found")
            return
        
        print(f"\nTotal Q&A Interactions: {len(self.qa_interactions)}")
        print()
        
        # Response time analysis
        if 'response_time' in qa_metrics and qa_metrics['response_time']:
            values = qa_metrics['response_time']
            print(f"Response Time:")
            print(f"  Mean:   {statistics.mean(values):.2f}s")
            print(f"  Median: {statistics.median(values):.2f}s")
            print(f"  Std:    {statistics.stdev(values) if len(values) > 1 else 0:.2f}s")
            print(f"  Min:    {min(values):.2f}s")
            print(f"  Max:    {max(values):.2f}s")
            print()
            
            # Speed categories
            speed_cats = {
                'Very Fast (<3s)': sum(1 for v in values if v < 3),
                'Fast (3-5s)': sum(1 for v in values if 3 <= v < 5),
                'Moderate (5-10s)': sum(1 for v in values if 5 <= v < 10),
                'Slow (>10s)': sum(1 for v in values if v >= 10)
            }
            
            print("Response Speed Distribution:")
            for cat, count in speed_cats.items():
                pct = (count / len(values)) * 100
                print(f"  {cat}: {count} ({pct:.1f}%)")
            print()
        
        # Quality analysis
        if 'overall_quality' in qa_metrics and qa_metrics['overall_quality']:
            values = qa_metrics['overall_quality']
            print(f"Overall Quality:")
            print(f"  Mean:   {statistics.mean(values):.4f}")
            print(f"  Median: {statistics.median(values):.4f}")
            print(f"  Std:    {statistics.stdev(values) if len(values) > 1 else 0:.4f}")
            print(f"  Min:    {min(values):.4f}")
            print(f"  Max:    {max(values):.4f}")
            print()
            
            # Quality distribution
            quality_ranges = {
                'Excellent (>0.8)': 0,
                'Good (0.6-0.8)': 0,
                'Moderate (0.4-0.6)': 0,
                'Poor (<0.4)': 0
            }
            
            for q in values:
                if q > 0.8:
                    quality_ranges['Excellent (>0.8)'] += 1
                elif q > 0.6:
                    quality_ranges['Good (0.6-0.8)'] += 1
                elif q > 0.4:
                    quality_ranges['Moderate (0.4-0.6)'] += 1
                else:
                    quality_ranges['Poor (<0.4)'] += 1
            
            print("Quality Distribution:")
            for range_name, count in quality_ranges.items():
                pct = (count / len(values)) * 100
                print(f"  {range_name}: {count} ({pct:.1f}%)")
            print()
        
        # Question analysis
        questions = [qa['question'] for qa in self.qa_interactions if 'question' in qa]
        if questions:
            print(f"Question Pattern Analysis:")
            
            # Common question patterns
            patterns = {
                'What': sum(1 for q in questions if q.lower().startswith('what')),
                'Which': sum(1 for q in questions if q.lower().startswith('which')),
                'How': sum(1 for q in questions if q.lower().startswith('how')),
                'Are/Do/Does': sum(1 for q in questions if any(q.lower().startswith(w) for w in ['are', 'do', 'does'])),
                'Tell me': sum(1 for q in questions if 'tell me' in q.lower()),
                'Other': 0
            }
            patterns['Other'] = len(questions) - sum(patterns.values())
            
            print(f"  Question Types:")
            for pattern, count in sorted(patterns.items(), key=lambda x: x[1], reverse=True):
                if count > 0:
                    pct = (count / len(questions)) * 100
                    print(f"    {pattern}: {count} ({pct:.1f}%)")
        
        print()
    
    def analyze_personas(self):
        """Analyze performance by persona"""
        print("="*70)
        print("PERSONA ANALYSIS")
        print("="*70)
        
        if not self.test_cases:
            print("No test case data found")
            return
        
        persona_stats = defaultdict(lambda: {
            'count': 0,
            'rec_quality': [],
            'rec_diversity': [],
            'qa_count': 0
        })
        
        for test in self.test_cases:
            persona = test.get('persona', 'Unknown')
            persona_stats[persona]['count'] += 1
            
            # Recommendation quality
            for rec in test.get('recommendations', []):
                if 'overall_quality' in rec:
                    persona_stats[persona]['rec_quality'].append(rec['overall_quality'])
                if 'diversity' in rec:
                    persona_stats[persona]['rec_diversity'].append(rec['diversity'])
            
            # Q&A count
            persona_stats[persona]['qa_count'] += len(test.get('qa', []))
        
        print(f"\nTotal Personas: {len(persona_stats)}")
        print()
        
        # Sort by average rec quality
        persona_list = []
        for persona, stats in persona_stats.items():
            avg_quality = statistics.mean(stats['rec_quality']) if stats['rec_quality'] else 0
            avg_diversity = statistics.mean(stats['rec_diversity']) if stats['rec_diversity'] else 0
            persona_list.append((persona, stats['count'], avg_quality, avg_diversity, stats['qa_count']))
        
        persona_list.sort(key=lambda x: x[2], reverse=True)
        
        print("Personas (sorted by recommendation quality):")
        print(f"{'Persona':<45} {'Tests':<8} {'Rec Quality':<12} {'Diversity':<12} {'Q&A':<8}")
        print("-" * 90)
        
        for persona, count, avg_qual, avg_div, qa_count in persona_list:
            print(f"{persona:<45} {count:<8} {avg_qual:<12.3f} {avg_div:<12.3f} {qa_count:<8}")
        
        print()
    
    def generate_insights(self):
        """Generate actionable insights"""
        print("="*70)
        print("KEY INSIGHTS & RECOMMENDATIONS")
        print("="*70)
        print()
        
        insights = []
        
        # Recommendation insights
        rec_quality = self.metrics['recommendation'].get('overall_quality', [])
        if rec_quality:
            avg_quality = statistics.mean(rec_quality)
            if avg_quality < 0.5:
                insights.append("LOW ALERT: Recommendation quality is below 50%. Immediate review needed.")
            elif avg_quality < 0.7:
                insights.append("MODERATE: Recommendation quality could be improved. Consider tuning weights.")
            else:
                insights.append("GOOD: Recommendation quality is above 70%.")
        
        # Diversity insights
        diversity = self.metrics['recommendation'].get('diversity', [])
        if diversity:
            avg_div = statistics.mean(diversity)
            if avg_div < 0.3:
                insights.append("LOW: Diversity is low. Users see too many similar cars. Increase variety.")
            elif avg_div > 0.6:
                insights.append("GOOD: Recommendations show good diversity.")
        
        # Q&A insights
        qa_quality = self.metrics['qa'].get('overall_quality', [])
        if qa_quality:
            avg_qa = statistics.mean(qa_quality)
            if avg_qa < 0.7:
                insights.append("MODERATE: Q&A quality needs improvement. Review context retrieval.")
            else:
                insights.append("EXCELLENT: Q&A quality is above 70%.")
        
        # Response time insights
        rec_time = self.metrics['recommendation'].get('response_time', [])
        if rec_time:
            avg_time = statistics.mean(rec_time)
            if avg_time > 3:
                insights.append(f"SLOW: Recommendation response time is {avg_time:.1f}s. Optimize performance.")
        
        qa_time = self.metrics['qa'].get('response_time', [])
        if qa_time:
            avg_time = statistics.mean(qa_time)
            slow_count = sum(1 for t in qa_time if t > 10)
            if avg_time > 10:
                insights.append(f"SLOW: Q&A response time is {avg_time:.1f}s. Consider caching.")
            elif slow_count > len(qa_time) * 0.1:
                insights.append(f"WARNING: {slow_count} Q&A responses took >10s. Investigate slow queries.")
        
        for i, insight in enumerate(insights, 1):
            print(f"{i}. {insight}")
        
        print()
        print("="*70)
    
    def run_full_analysis(self):
        """Run complete analysis"""
        self.parse_log()
        self.analyze_recommendations()
        self.analyze_qa()
        self.analyze_personas()
        self.generate_insights()


if __name__ == "__main__":
    import sys
    
    log_file = "benchmark_full_100.log"
    if len(sys.argv) > 1:
        log_file = sys.argv[1]
    
    analyzer = LogAnalyzer(log_file)
    analyzer.run_full_analysis()
    
    print("\nAnalysis complete!")
