"use client";

import { useState, useEffect } from "react";
import axios from "axios";
import { ChevronDown, ChevronUp, Search, MessageSquare, RefreshCw, Check } from "lucide-react";

const API_BASE_URL = process.env.NEXT_PUBLIC_MODEL_URL; // Update with your actual API URL

const computeComfort = (car) => {
  const scores = [
    car.front_seat_comfort_score,
    car.rear_seat_comfort_score,
    car.bump_absorption_score,
    car.material_quality_score,
  ];
  return (scores.reduce((a, b) => a + b, 0) / scores.length).toFixed(1);
};

export default function Home() {
  const [prefs, setPrefs] = useState({
    min_budget: 500000,
    max_budget: 2000000,
    fuel_type: "Any",
    body_type: "Any",
    transmission: "Any",
    seating: 5,
    features: [],
    performance: 5,
  });

  const [results, setResults] = useState([]);
  const [question, setQuestion] = useState("");
  const [chatResponse, setChatResponse] = useState("");
  const [isSearching, setIsSearching] = useState(false);
  const [isAsking, setIsAsking] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);
  const [error, setError] = useState("");
  const [expandedCard, setExpandedCard] = useState(null);
  const [sessionId, setSessionId] = useState("");
  const [reviews, setReviews] = useState({});
  const [qualityMetrics, setQualityMetrics] = useState(null);
  const [answerQuality, setAnswerQuality] = useState(null);

  useEffect(() => {
    if (hasSearched && question.trim() === "") {
      setChatResponse("");
    }
  }, [question, hasSearched]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (prefs.min_budget > prefs.max_budget) {
      setError("Minimum budget cannot be greater than maximum budget");
      return;
    }

    setIsSearching(true);
    setError("");

    try {
      // Map the frontend preferences to match the API's expected format
      const response = await axios.post(`${API_BASE_URL}/api/recommend`, {
        min_budget: prefs.min_budget,
        max_budget: prefs.max_budget,
        fuel_type: prefs.fuel_type,
        body_type: prefs.body_type,
        transmission: prefs.transmission,
        seating: prefs.seating,
        features: prefs.features,
        performance: prefs.performance
      });
      
      // Store the session ID for future requests
      setSessionId(response.data.session_id);
      
      // Process and store the car matches
      setResults(response.data.matches.map(match => ({
        car: match.car,
        details: match.details,
        score: match.combined_score
      })));
      
      // Store reviews if available
      if (response.data.reviews) {
        setReviews(response.data.reviews);
      }
      
      // Store quality metrics
      if (response.data.quality_metrics) {
        setQualityMetrics(response.data.quality_metrics);
      }
      
      setHasSearched(true);
    } catch (err) {
      console.error("Recommendation error:", err);
      setError("Failed to get recommendations. Please try again.");
    } finally {
      setIsSearching(false);
    }
  };

  const handleAsk = async () => {
    if (!question.trim()) return;
    setIsAsking(true);
    setChatResponse("");
    try {
      const response = await axios.post(`${API_BASE_URL}/api/ask`, {
        question,
        session_id: sessionId
      });
      setChatResponse(response.data.answer);
      
      // Store answer quality metrics
      if (response.data.quality_metrics) {
        setAnswerQuality(response.data.quality_metrics);
      }
    } catch (err) {
      console.error("Chat error:", err);
      setChatResponse("Sorry, I couldn't process your question. Please try again.");
    } finally {
      setIsAsking(false);
    }
  };

  const toggleCard = (idx) => {
    setExpandedCard(expandedCard === idx ? null : idx);
  };

  const formatPrice = (price) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(price);
  };

  const renderPriceRange = () => {
    return (
      <div className="relative pt-6">
        <label className="block font-medium mb-1">Budget Range: {formatPrice(prefs.min_budget)} - {formatPrice(prefs.max_budget)}</label>
        <div className="relative h-2 bg-gray-700 rounded-full mb-6">
          <div className="absolute h-2 bg-blue-500 rounded-full" 
               style={{
                 left: '0%',
                 width: '100%'
               }}></div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm mb-1">Min Budget</label>
            <input 
              className="p-2 w-full rounded bg-gray-800 text-white border border-gray-600 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all"
              type="number" 
              required 
              value={prefs.min_budget} 
              onChange={(e) => setPrefs(prev => ({ ...prev, min_budget: parseInt(e.target.value) }))} 
              placeholder="Min Budget (₹)" 
            />
          </div>
          <div>
            <label className="block text-sm mb-1">Max Budget</label>
            <input 
              className="p-2 w-full rounded bg-gray-800 text-white border border-gray-600 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all" 
              type="number" 
              required 
              value={prefs.max_budget} 
              onChange={(e) => setPrefs(prev => ({ ...prev, max_budget: parseInt(e.target.value) }))} 
              placeholder="Max Budget (₹)" 
            />
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-blue-900 via-black to-black text-white min-h-screen pb-16">
      <div className="max-w-5xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
        <header className="text-center mb-10">
          <h1 className="text-4xl font-bold mb-2 bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-500">VariantWise Consultant</h1>
          <p className="text-gray-300 max-w-2xl mx-auto">Find the perfect car that matches your preferences and budget</p>
        </header>

        {!hasSearched ? (
          <form onSubmit={handleSubmit} className="bg-gray-900/70 backdrop-blur-sm p-6 sm:p-8 rounded-xl shadow-lg border border-gray-800">
            {renderPriceRange()}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-8">
              <div>
                <label className="block font-medium mb-1">Fuel Type</label>
                <select 
                  className="w-full p-2 rounded bg-gray-800 text-white border border-gray-600 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all" 
                  value={prefs.fuel_type} 
                  onChange={(e) => setPrefs(prev => ({ ...prev, fuel_type: e.target.value }))}
                >
                  {["Any", "Petrol", "Diesel", "Electric", "CNG", "Hybrid"].map(f => 
                    <option key={f} value={f}>{f}</option>
                  )}
                </select>
              </div>
              
              <div>
                <label className="block font-medium mb-1">Body Type</label>
                <select 
                  className="w-full p-2 rounded bg-gray-800 text-white border border-gray-600 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all" 
                  value={prefs.body_type} 
                  onChange={(e) => setPrefs(prev => ({ ...prev, body_type: e.target.value }))}
                >
                  {["Any", "SUV", "Sedan", "Hatchback", "MUV", "Crossover"].map(b => 
                    <option key={b} value={b}>{b}</option>
                  )}
                </select>
              </div>
              
              <div>
                <label className="block font-medium mb-1">Transmission</label>
                <select 
                  className="w-full p-2 rounded bg-gray-800 text-white border border-gray-600 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all" 
                  value={prefs.transmission} 
                  onChange={(e) => setPrefs(prev => ({ ...prev, transmission: e.target.value }))}
                >
                  {["Any", "Manual", "Automatic", "CVT", "DCT", "AMT"].map(t => 
                    <option key={t} value={t}>{t}</option>
                  )}
                </select>
              </div>
              
              <div>
                <label className="block font-medium mb-1">Seating Capacity</label>
                <input 
                  className="w-full p-2 rounded bg-gray-800 text-white border border-gray-600 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all" 
                  type="number" 
                  min="2" 
                  max="9" 
                  value={prefs.seating} 
                  onChange={(e) => setPrefs(prev => ({ ...prev, seating: parseInt(e.target.value) }))} 
                  placeholder="Min Seats" 
                />
              </div>
            </div>

            <div className="mt-6">
              <label className="block font-medium mb-2">Must-Have Features</label>
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                {["Sunroof", "Apple CarPlay/Android Auto", "Automatic Climate Control", "360 Camera", "Lane Assist", "Ventilated Seats", "Wireless Charging"].map((feature) => (
                  <div 
                    key={feature}
                    className={`p-2 rounded-md border cursor-pointer transition-all ${
                      prefs.features.includes(feature) 
                        ? "bg-blue-600/30 border-blue-400 text-white" 
                        : "bg-gray-800 border-gray-700 text-gray-300"
                    }`}
                    onClick={() => {
                      setPrefs((prev) => {
                        const newFeatures = prev.features.includes(feature)
                          ? prev.features.filter(f => f !== feature)
                          : [...prev.features, feature];
                        return { ...prev, features: newFeatures };
                      });
                    }}
                  >
                    <div className="flex items-center">
                      {prefs.features.includes(feature) && <Check size={16} className="mr-1 flex-shrink-0" />}
                      <span className="text-sm">{feature}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="mt-6">
              <label className="block font-medium mb-1">Performance Priority: {prefs.performance}/10</label>
              <input 
                type="range" 
                min="1" 
                max="10" 
                value={prefs.performance} 
                className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-blue-500" 
                onChange={(e) => setPrefs(prev => ({ ...prev, performance: parseInt(e.target.value) }))} 
              />
              <div className="flex justify-between text-xs text-gray-400 mt-1">
                <span>Comfort</span>
                <span>Balanced</span>
                <span>Performance</span>
              </div>
            </div>

            <div className="mt-8">
              <button 
                type="submit" 
                disabled={isSearching}
                className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white py-3 rounded-lg text-lg font-medium flex items-center justify-center transition-all shadow-lg hover:shadow-blue-500/30"
              >
                {isSearching ? (
                  <>
                    <RefreshCw size={20} className="mr-2 animate-spin" />
                    Finding Your Perfect Cars...
                  </>
                ) : (
                  <>
                    <Search size={20} className="mr-2" />
                    Find My Car
                  </>
                )}
              </button>
            </div>

            {error && (
              <div className="mt-4 p-3 bg-red-900/60 border border-red-700 rounded-lg text-sm text-red-200">
                ⚠️ {error}
              </div>
            )}
          </form>
        ) : (
          <div className="animate-fade-in">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-semibold">Your Top Recommendations</h2>
              <button 
                className="text-gray-300 hover:text-white flex items-center text-sm bg-gray-800/70 px-3 py-1.5 rounded-full transition-all hover:bg-gray-700"
                onClick={() => { 
                  setHasSearched(false); 
                  setResults([]); 
                  setChatResponse(""); 
                  setError(""); 
                  setSessionId("");
                  setReviews({});
                  setQualityMetrics(null);
                  setAnswerQuality(null);
                }}
              >
                <RefreshCw size={14} className="mr-1" /> New Search
              </button>
            </div>

            {/* Quality Metrics Display */}
            {qualityMetrics && (
              <div className="mb-6 bg-gradient-to-r from-blue-900/30 to-purple-900/30 backdrop-blur-sm border border-blue-800/50 rounded-xl p-5 shadow-lg">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold flex items-center text-blue-300">
                    <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                    </svg>
                    Recommendation Quality Metrics
                  </h3>
                  {qualityMetrics.evaluation_method && (
                    <span className={`text-xs px-2 py-1 rounded ${
                      qualityMetrics.evaluation_method === 'advanced_hybrid' 
                        ? 'bg-gradient-to-r from-purple-500/20 to-pink-500/20 text-purple-200 border border-purple-400/30' 
                        : qualityMetrics.evaluation_method.includes('hybrid')
                        ? 'bg-purple-500/20 text-purple-300' 
                        : 'bg-gray-600/20 text-gray-400'
                    }`}>
                      {qualityMetrics.evaluation_method === 'advanced_hybrid' 
                        ? '🚀 Advanced Multi-Framework' 
                        : qualityMetrics.evaluation_method.includes('hybrid')
                        ? '🤖 AI-Enhanced' 
                        : '📊 Rule-Based'}
                    </span>
                  )}
                </div>
                
                <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-4">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-white">{(qualityMetrics.overall_quality * 100).toFixed(0)}%</div>
                    <div className="text-xs text-gray-400 mt-1">Overall Quality</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-green-400">{(qualityMetrics.relevance_score * 100).toFixed(0)}%</div>
                    <div className="text-xs text-gray-400 mt-1">Relevance</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-purple-400">{(qualityMetrics.diversity_score * 100).toFixed(0)}%</div>
                    <div className="text-xs text-gray-400 mt-1">Diversity</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-blue-400">{(qualityMetrics.performance_score * 100).toFixed(0)}%</div>
                    <div className="text-xs text-gray-400 mt-1">Performance</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-yellow-400">{qualityMetrics.response_time}s</div>
                    <div className="text-xs text-gray-400 mt-1">Response Time</div>
                  </div>
                </div>

                {/* Advanced Framework Scores */}
                {qualityMetrics.advanced_available && (
                  <div className="mt-4 pt-4 border-t border-purple-700/30">
                    <div className="text-xs font-semibold text-purple-300 mb-3 flex items-center">
                      <span className="mr-2">🚀 Advanced Metrics (NDCG, ILD, Novelty):</span>
                    </div>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
                      {qualityMetrics.advanced_ndcg !== undefined && (
                        <div className="text-center">
                          <div className="font-semibold text-cyan-300">{(qualityMetrics.advanced_ndcg * 100).toFixed(0)}%</div>
                          <div className="text-gray-500">NDCG@K</div>
                        </div>
                      )}
                      {qualityMetrics.advanced_ild !== undefined && (
                        <div className="text-center">
                          <div className="font-semibold text-purple-300">{(qualityMetrics.advanced_ild * 100).toFixed(0)}%</div>
                          <div className="text-gray-500">ILD (Diversity)</div>
                        </div>
                      )}
                      {qualityMetrics.advanced_novelty !== undefined && (
                        <div className="text-center">
                          <div className="font-semibold text-pink-300">{(qualityMetrics.advanced_novelty * 100).toFixed(0)}%</div>
                          <div className="text-gray-500">Novelty</div>
                        </div>
                      )}
                      {qualityMetrics.advanced_serendipity !== undefined && (
                        <div className="text-center">
                          <div className="font-semibold text-yellow-300">{(qualityMetrics.advanced_serendipity * 100).toFixed(0)}%</div>
                          <div className="text-gray-500">Serendipity</div>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* LLM Judge Scores (if available) */}
                {qualityMetrics.llm_available && qualityMetrics.llm_overall && (
                  <div className="mt-4 pt-4 border-t border-blue-700/30">
                    <div className="text-xs text-gray-400 mb-2 flex items-center">
                      <span className="mr-2">🤖 AI Judge Analysis:</span>
                      {qualityMetrics.llm_explanation && (
                        <span className="text-gray-300 italic">"{qualityMetrics.llm_explanation}"</span>
                      )}
                    </div>
                    <div className="grid grid-cols-2 md:grid-cols-5 gap-3 text-xs">
                      {qualityMetrics.llm_relevance !== undefined && (
                        <div className="text-center">
                          <div className="font-semibold text-green-300">{(qualityMetrics.llm_relevance * 100).toFixed(0)}%</div>
                          <div className="text-gray-500">AI Relevance</div>
                        </div>
                      )}
                      {qualityMetrics.llm_diversity !== undefined && (
                        <div className="text-center">
                          <div className="font-semibold text-purple-300">{(qualityMetrics.llm_diversity * 100).toFixed(0)}%</div>
                          <div className="text-gray-500">AI Diversity</div>
                        </div>
                      )}
                      {qualityMetrics.llm_practicality !== undefined && (
                        <div className="text-center">
                          <div className="font-semibold text-blue-300">{(qualityMetrics.llm_practicality * 100).toFixed(0)}%</div>
                          <div className="text-gray-500">Practicality</div>
                        </div>
                      )}
                      {qualityMetrics.llm_value !== undefined && (
                        <div className="text-center">
                          <div className="font-semibold text-yellow-300">{(qualityMetrics.llm_value * 100).toFixed(0)}%</div>
                          <div className="text-gray-500">Value</div>
                        </div>
                      )}
                      {qualityMetrics.llm_reasoning_quality !== undefined && (
                        <div className="text-center">
                          <div className="font-semibold text-pink-300">{(qualityMetrics.llm_reasoning_quality * 100).toFixed(0)}%</div>
                          <div className="text-gray-500">Reasoning</div>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* Enhanced Evaluation Metrics */}
                {qualityMetrics.enhanced && (
                  <div className="mt-4 pt-4 border-t border-green-700/30">
                    <div className="text-xs font-semibold text-green-300 mb-3 flex items-center">
                      <span className="mr-2">✨ Enhanced Evaluation:</span>
                    </div>
                    
                    {/* Predicted Satisfaction */}
                    {qualityMetrics.enhanced.predicted_satisfaction && (
                      <div className="mb-4">
                        <div className="flex justify-between items-center mb-2">
                          <span className="text-xs text-gray-400">Predicted User Satisfaction</span>
                          <span className="text-sm font-semibold text-green-300">
                            {(qualityMetrics.enhanced.predicted_satisfaction.predicted_satisfaction * 100).toFixed(0)}%
                          </span>
                        </div>
                        <div className="grid grid-cols-4 gap-2 text-xs">
                          <div className="text-center">
                            <div className="font-semibold text-blue-300">
                              {(qualityMetrics.enhanced.predicted_satisfaction.best_match_score * 100).toFixed(0)}%
                            </div>
                            <div className="text-gray-500">Best Match</div>
                          </div>
                          <div className="text-center">
                            <div className="font-semibold text-purple-300">
                              {(qualityMetrics.enhanced.predicted_satisfaction.top3_avg * 100).toFixed(0)}%
                            </div>
                            <div className="text-gray-500">Top 3 Avg</div>
                          </div>
                          <div className="text-center">
                            <div className="font-semibold text-yellow-300">
                              {(qualityMetrics.enhanced.predicted_satisfaction.diversity_factor * 100).toFixed(0)}%
                            </div>
                            <div className="text-gray-500">Diversity</div>
                          </div>
                          <div className="text-center">
                            <div className="font-semibold text-green-300">
                              {(qualityMetrics.enhanced.predicted_satisfaction.confidence * 100).toFixed(0)}%
                            </div>
                            <div className="text-gray-500">Confidence</div>
                          </div>
                        </div>
                      </div>
                    )}

                    {/* Preference Alignment */}
                    {qualityMetrics.enhanced.preference_alignment && (
                      <div className="mb-4">
                        <div className="flex justify-between items-center mb-2">
                          <span className="text-xs text-gray-400">Preference Alignment</span>
                          <span className="text-sm font-semibold text-green-300">
                            {(qualityMetrics.enhanced.preference_alignment.overall_alignment * 100).toFixed(0)}%
                          </span>
                        </div>
                        <div className="grid grid-cols-4 gap-2 text-xs">
                          <div className="text-center">
                            <div className="font-semibold text-blue-300">
                              {(qualityMetrics.enhanced.preference_alignment.budget_alignment * 100).toFixed(0)}%
                            </div>
                            <div className="text-gray-500">Budget</div>
                          </div>
                          <div className="text-center">
                            <div className="font-semibold text-purple-300">
                              {(qualityMetrics.enhanced.preference_alignment.fuel_alignment * 100).toFixed(0)}%
                            </div>
                            <div className="text-gray-500">Fuel</div>
                          </div>
                          <div className="text-center">
                            <div className="font-semibold text-yellow-300">
                              {(qualityMetrics.enhanced.preference_alignment.body_alignment * 100).toFixed(0)}%
                            </div>
                            <div className="text-gray-500">Body Type</div>
                          </div>
                          <div className="text-center">
                            <div className="font-semibold text-green-300">
                              {(qualityMetrics.enhanced.preference_alignment.transmission_alignment * 100).toFixed(0)}%
                            </div>
                            <div className="text-gray-500">Transmission</div>
                          </div>
                        </div>
                      </div>
                    )}

                    {/* Actionable Insights */}
                    {qualityMetrics.enhanced.actionable_insights && qualityMetrics.enhanced.actionable_insights.length > 0 && (
                      <div className="mt-3 pt-3 border-t border-green-700/20">
                        <div className="text-xs font-semibold text-green-300 mb-2">💡 Insights:</div>
                        <ul className="space-y-1">
                          {qualityMetrics.enhanced.actionable_insights.map((insight, idx) => (
                            <li key={idx} className="text-xs text-gray-300 flex items-start">
                              <span className="text-green-400 mr-1.5">•</span>
                              {insight}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}

            <div className="space-y-4">
              {results.map((match, idx) => (
                <div 
                  key={idx} 
                  className={`bg-gray-900/70 backdrop-blur-sm border border-gray-800 rounded-xl shadow-lg overflow-hidden transition-all duration-300 ${
                    expandedCard === idx ? "ring-2 ring-blue-500" : "hover:border-gray-700"
                  }`}
                >
                  <div 
                    className="p-5 cursor-pointer flex justify-between items-center"
                    onClick={() => toggleCard(idx)}
                  >
                    <div className="flex-1">
                      <div className="flex items-center gap-2 flex-wrap">
                        <h3 className="text-xl font-bold">{match.car.variant}</h3>
                        {match.match_quality && (
                          <span className={`text-xs px-2 py-1 rounded-full ${
                            match.match_quality === 'Excellent Match' 
                              ? 'bg-green-500/20 text-green-300 border border-green-400/30' 
                              : match.match_quality === 'Great Match'
                              ? 'bg-blue-500/20 text-blue-300 border border-blue-400/30'
                              : match.match_quality === 'Good Match'
                              ? 'bg-yellow-500/20 text-yellow-300 border border-yellow-400/30'
                              : 'bg-gray-500/20 text-gray-300 border border-gray-400/30'
                          }`}>
                            {match.match_quality}
                          </span>
                        )}
                      </div>
                      <p className="text-lg font-semibold text-blue-400 mt-1">{match.car.price}</p>
                      {match.explanation && (
                        <p className="text-sm text-gray-400 mt-2 flex items-start">
                          <svg className="w-4 h-4 mr-1.5 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                          {match.explanation}
                        </p>
                      )}
                    </div>
                    <div className="flex items-center space-x-4">
                      <div className="text-right hidden sm:block">
                        <div className="text-sm text-gray-300">
                          <span className="inline-flex items-center bg-gray-800 px-2 py-0.5 rounded mr-2 text-xs">
                            {match.car["Fuel Type"]}
                          </span>
                          <span className="inline-flex items-center bg-gray-800 px-2 py-0.5 rounded mr-2 text-xs">
                            {match.car["Transmission Type"]}
                          </span>
                          <span className="inline-flex items-center bg-gray-800 px-2 py-0.5 rounded text-xs">
                            {match.car["Seating Capacity"]} seats
                          </span>
                        </div>
                        <div className="mt-1 text-sm">
                          <span className="text-yellow-400">Comfort: {computeComfort(match.car)}/5</span>
                        </div>
                      </div>
                      {expandedCard === idx ? (
                        <ChevronUp size={20} className="text-gray-400" />
                      ) : (
                        <ChevronDown size={20} className="text-gray-400" />
                      )}
                    </div>
                  </div>
                  
                  {expandedCard === idx && (
                    <div className="px-5 pb-5 border-t border-gray-800 animate-slide-down">
                      <div className="sm:hidden py-2 mb-2">
                        <div className="flex flex-wrap gap-2">
                          <span className="inline-flex items-center bg-gray-800 px-2 py-0.5 rounded text-xs">
                            {match.car["Fuel Type"]}
                          </span>
                          <span className="inline-flex items-center bg-gray-800 px-2 py-0.5 rounded text-xs">
                            {match.car["Transmission Type"]}
                          </span>
                          <span className="inline-flex items-center bg-gray-800 px-2 py-0.5 rounded text-xs">
                            {match.car["Seating Capacity"]} seats
                          </span>
                          <span className="inline-flex items-center bg-gray-800 px-2 py-0.5 rounded text-xs text-yellow-400">
                            Comfort: {computeComfort(match.car)}/5
                          </span>
                        </div>
                      </div>
                      
                      <p className="text-gray-300 py-2">{match.car.description || "No description available."}</p>
                      
                      {/* Display review if available */}
                      {reviews[match.car.variant] && (
                        <div className="mt-3 pt-3 border-t border-gray-800">
                          <h4 className="font-semibold text-sm text-blue-400 mb-2">Expert Review</h4>
                          <p className="text-sm text-gray-300">{reviews[match.car.variant].substring(0, 200)}...</p>
                        </div>
                      )}
                      
                      <div className="mt-3 pt-3 border-t border-gray-800">
                        <h4 className="font-semibold text-sm text-blue-400 mb-2">Highlights</h4>
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-1">
                          {Object.entries(match.details).map(([k, v], i) => (
                            <p key={i} className="text-sm text-gray-300 flex items-start">
                              <span className="text-green-400 mr-1.5 mt-1">•</span> {v}
                            </p>
                          ))}
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>

            <div className="mt-10 bg-gray-900/70 backdrop-blur-sm p-6 rounded-xl shadow-lg border border-gray-800">
              <h3 className="text-lg font-semibold mb-4 flex items-center">
                <MessageSquare size={18} className="mr-2 text-blue-400" />
                Ask About These Cars
              </h3>
              
              <div className="flex gap-2">
                <input 
                  type="text" 
                  placeholder="e.g., Which car has the best mileage?" 
                  className="flex-1 border border-gray-700 p-3 rounded-lg bg-gray-800 text-white focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all" 
                  value={question} 
                  onChange={(e) => setQuestion(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleAsk()}
                />
                <button 
                  onClick={handleAsk} 
                  disabled={isAsking || !question.trim() || !sessionId} 
                  className={`bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg flex items-center transition-all ${
                    isAsking || !question.trim() || !sessionId ? 'opacity-50 cursor-not-allowed' : ''
                  }`}
                >
                  {isAsking ? (
                    <RefreshCw size={18} className="animate-spin" />
                  ) : (
                    <span>Ask</span>
                  )}
                </button>
              </div>
              
              {chatResponse && (
                <div className="mt-4 space-y-3">
                  <div className="p-5 bg-gray-800 border border-gray-700 rounded-lg text-gray-200 animate-fade-in whitespace-pre-wrap">
                    {chatResponse}
                  </div>
                  
                  {/* Answer Quality Metrics */}
                  {answerQuality && (
                    <div className="p-4 bg-gradient-to-r from-green-900/20 to-blue-900/20 border border-green-800/30 rounded-lg">
                      {/* Hallucination Warning */}
                      {answerQuality.hallucination_detected && (
                        <div className="mb-3 p-2 bg-red-900/30 border border-red-700/50 rounded text-xs text-red-300 flex items-center">
                          <svg className="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                          </svg>
                          <div>
                            <div className="font-semibold">⚠️ Possible Hallucination Detected</div>
                            {answerQuality.hallucination_explanation && (
                              <div className="mt-1">{answerQuality.hallucination_explanation}</div>
                            )}
                          </div>
                        </div>
                      )}
                      
                      <div className="flex items-center justify-between text-sm mb-2">
                        <div className="flex items-center space-x-4 flex-wrap">
                          <div>
                            <span className="text-gray-400">Quality:</span>
                            <span className="ml-2 font-semibold text-green-400">{(answerQuality.overall_quality * 100).toFixed(0)}%</span>
                          </div>
                          <div>
                            <span className="text-gray-400">Relevance:</span>
                            <span className="ml-2 font-semibold text-blue-400">{(answerQuality.relevance_score * 100).toFixed(0)}%</span>
                          </div>
                          <div>
                            <span className="text-gray-400">Grounded:</span>
                            <span className="ml-2 font-semibold text-purple-400">{(answerQuality.groundedness_score * 100).toFixed(0)}%</span>
                          </div>
                          <div>
                            <span className="text-gray-400">Time:</span>
                            <span className="ml-2 font-semibold text-yellow-400">{answerQuality.response_time}s</span>
                          </div>
                        </div>
                        {answerQuality.evaluation_method && (
                          <span className={`text-xs px-2 py-1 rounded ${
                            answerQuality.evaluation_method === 'advanced_hybrid' 
                              ? 'bg-gradient-to-r from-purple-500/20 to-pink-500/20 text-purple-200 border border-purple-400/30' 
                              : answerQuality.evaluation_method.includes('hybrid')
                              ? 'bg-purple-500/20 text-purple-300' 
                              : 'bg-gray-600/20 text-gray-400'
                          }`}>
                            {answerQuality.evaluation_method === 'advanced_hybrid' 
                              ? '🚀 DeepEval+RAGAS' 
                              : answerQuality.evaluation_method.includes('hybrid')
                              ? '🤖 AI-Enhanced' 
                              : '📊 Rule-Based'}
                          </span>
                        )}
                      </div>

                      {/* DeepEval Scores */}
                      {answerQuality.deepeval_available && answerQuality.deepeval_overall && (
                        <div className="mt-3 pt-3 border-t border-purple-700/30">
                          <div className="text-xs font-semibold text-purple-300 mb-2">🔬 DeepEval Framework:</div>
                          <div className="grid grid-cols-2 md:grid-cols-3 gap-3 text-xs">
                            {answerQuality.deepeval_answerrelevancy !== undefined && (
                              <div className="text-center">
                                <div className="font-semibold text-cyan-300">{(answerQuality.deepeval_answerrelevancy * 100).toFixed(0)}%</div>
                                <div className="text-gray-500">Answer Relevancy</div>
                              </div>
                            )}
                            {answerQuality.deepeval_faithfulness !== undefined && (
                              <div className="text-center">
                                <div className="font-semibold text-green-300">{(answerQuality.deepeval_faithfulness * 100).toFixed(0)}%</div>
                                <div className="text-gray-500">Faithfulness</div>
                              </div>
                            )}
                            {answerQuality.deepeval_hallucination !== undefined && (
                              <div className="text-center">
                                <div className="font-semibold text-red-300">{(answerQuality.deepeval_hallucination * 100).toFixed(0)}%</div>
                                <div className="text-gray-500">Hallucination</div>
                              </div>
                            )}
                          </div>
                        </div>
                      )}

                      {/* RAGAS Scores */}
                      {answerQuality.ragas_available && answerQuality.ragas_overall && (
                        <div className="mt-3 pt-3 border-t border-pink-700/30">
                          <div className="text-xs font-semibold text-pink-300 mb-2">📊 RAGAS Framework:</div>
                          <div className="grid grid-cols-2 md:grid-cols-3 gap-3 text-xs">
                            {answerQuality.ragas_faithfulness !== undefined && (
                              <div className="text-center">
                                <div className="font-semibold text-green-300">{(answerQuality.ragas_faithfulness * 100).toFixed(0)}%</div>
                                <div className="text-gray-500">Faithfulness</div>
                              </div>
                            )}
                            {answerQuality.ragas_answer_relevancy !== undefined && (
                              <div className="text-center">
                                <div className="font-semibold text-blue-300">{(answerQuality.ragas_answer_relevancy * 100).toFixed(0)}%</div>
                                <div className="text-gray-500">Relevancy</div>
                              </div>
                            )}
                            {answerQuality.ragas_context_precision !== undefined && (
                              <div className="text-center">
                                <div className="font-semibold text-purple-300">{(answerQuality.ragas_context_precision * 100).toFixed(0)}%</div>
                                <div className="text-gray-500">Context Precision</div>
                              </div>
                            )}
                          </div>
                        </div>
                      )}

                      {/* LLM Judge Scores (if available) */}
                      {answerQuality.llm_available && answerQuality.llm_overall && (
                        <div className="mt-3 pt-3 border-t border-green-700/30">
                          <div className="text-xs text-gray-400 mb-2 flex items-center">
                            <span className="mr-2">🤖 AI Judge Analysis:</span>
                            {answerQuality.llm_reasoning && (
                              <span className="text-gray-300 italic">"{answerQuality.llm_reasoning}"</span>
                            )}
                          </div>
                          <div className="grid grid-cols-2 md:grid-cols-5 gap-3 text-xs">
                            {answerQuality.llm_relevance !== undefined && (
                              <div className="text-center">
                                <div className="font-semibold text-green-300">{(answerQuality.llm_relevance * 100).toFixed(0)}%</div>
                                <div className="text-gray-500">AI Relevance</div>
                              </div>
                            )}
                            {answerQuality.llm_accuracy !== undefined && (
                              <div className="text-center">
                                <div className="font-semibold text-blue-300">{(answerQuality.llm_accuracy * 100).toFixed(0)}%</div>
                                <div className="text-gray-500">Accuracy</div>
                              </div>
                            )}
                            {answerQuality.llm_completeness !== undefined && (
                              <div className="text-center">
                                <div className="font-semibold text-purple-300">{(answerQuality.llm_completeness * 100).toFixed(0)}%</div>
                                <div className="text-gray-500">Completeness</div>
                              </div>
                            )}
                            {answerQuality.llm_helpfulness !== undefined && (
                              <div className="text-center">
                                <div className="font-semibold text-yellow-300">{(answerQuality.llm_helpfulness * 100).toFixed(0)}%</div>
                                <div className="text-gray-500">Helpfulness</div>
                              </div>
                            )}
                            {answerQuality.llm_groundedness !== undefined && (
                              <div className="text-center">
                                <div className="font-semibold text-pink-300">{(answerQuality.llm_groundedness * 100).toFixed(0)}%</div>
                                <div className="text-gray-500">AI Grounded</div>
                              </div>
                            )}
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        )}
      </div>
      
      <style jsx>{`
        @keyframes fade-in {
          from { opacity: 0; }
          to { opacity: 1; }
        }
        @keyframes slide-down {
          from { opacity: 0; max-height: 0; }
          to { opacity: 1; max-height: 500px; }
        }
        .animate-fade-in {
          animation: fade-in 0.3s ease-out;
        }
        .animate-slide-down {
          animation: slide-down 0.3s ease-out;
          overflow: hidden;
        }
      `}</style>
    </div>
  );
}