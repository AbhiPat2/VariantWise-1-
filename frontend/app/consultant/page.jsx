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
                }}
              >
                <RefreshCw size={14} className="mr-1" /> New Search
              </button>
            </div>

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
                    <div>
                      <h3 className="text-xl font-bold">{match.car.variant}</h3>
                      <p className="text-lg font-semibold text-blue-400">{match.car.price}</p>
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
                <div className="mt-4 p-5 bg-gray-800 border border-gray-700 rounded-lg text-gray-200 animate-fade-in whitespace-pre-wrap">
                  {chatResponse}
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