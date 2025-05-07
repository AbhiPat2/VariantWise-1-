"use client"

import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { useEffect , useState } from "react"
import { useRouter } from "next/navigation"
import axios from "axios"
import { Star, Award, Battery, ThumbsUp, Shield } from "lucide-react";

export default function DashboardPage() {

  const [activeTab, setActiveTab] = useState("overview");
  
  // Reviews data
  const reviews = [
    { author: "Car Expert", rating: 4.5, text: "Exceptional value and performance for its segment." },
    { author: "Auto World", rating: 4.8, text: "Best-in-class features with impressive driving dynamics." },
    { author: "SUV Magazine", rating: 4.7, text: "Redefines comfort and luxury in the compact SUV space." }
  ];
  
  // Features data
  const features = [
    { name: "Panoramic Sunroof", description: "Enjoy open-air driving with a large dual-pane sunroof" },
    { name: "Advanced Driver Assistance", description: "Lane keep assist, blind spot monitoring, and adaptive cruise control" },
    { name: "10.25\" Touchscreen", description: "Intuitive infotainment with wireless Apple CarPlay & Android Auto" },
    { name: "Bose Premium Sound", description: "8-speaker system with rich bass and crisp highs" },
    { name: "Ventilated Seats", description: "Stay cool with front ventilated seats for hot weather comfort" },
    { name: "Smart Power Tailgate", description: "Hands-free opening for convenient loading and unloading" }
  ];
  
  // Performance metrics
  const performanceMetrics = [
    { label: "Performance", value: 85, icon: <ThumbsUp size={20} /> },
    { label: "Comfort", value: 90, icon: <Award size={20} /> },
    { label: "Fuel Economy", value: 75, icon: <Battery size={20} /> },
    { label: "Features", value: 95, icon: <Star size={20} /> },
    { label: "Safety", value: 88, icon: <Shield size={20} /> }
  ];

  return (
    <div className="bg-black text-white min-h-screen">
      {/* Hero section with gradient backdrop */}
      <div className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-black to-gray-900 opacity-90"></div>
        <div className="container mx-auto px-4 py-20 relative z-10 text-center">
          <h1 className="text-5xl font-bold mb-4 text-white">Hyundai Creta</h1>
          <p className="text-2xl text-gray-300 mb-2 font-bold">SX (O) Knight Premium</p>
            <p className="text-2xl font-light text-gray-300 mb-8">(Top Variant)</p>
          <div className="bg-black bg-opacity-80 p-4 inline-block rounded-lg border border-gray-800">
            <p className="text-3xl font-bold text-green-400">₹18.68 Lakh</p>
            <p className="text-sm text-gray-400">Ex-showroom price</p>
          </div>
        </div>
      </div>
      
      {/* Navigation tabs */}
      <div className="bg-black sticky top-0 z-20 border-b border-gray-900">
        <div className="container mx-auto px-4">
          <div className="flex overflow-x-auto py-2 space-x-4">
            {["overview", "specs", "features", "reviews"].map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-4 py-2 font-medium transition-colors whitespace-nowrap ${
                  activeTab === tab 
                    ? "text-blue-400 border-b-2 border-blue-400" 
                    : "text-gray-500 hover:text-gray-300"
                }`}
              >
                {tab.charAt(0).toUpperCase() + tab.slice(1)}
              </button>
            ))}
          </div>
        </div>
      </div>
      
      {/* Main content area */}
      <div className="container mx-auto px-4 py-8">
        {/* Overview Tab */}
        {activeTab === "overview" && (
          <div className="space-y-8">
          {/* Car Image with shine effect only on background */}
          <div className="relative rounded-xl overflow-hidden bg-gradient-to-r from-black via-gray-900 to-black p-6 border border-gray-800">
            
            {/* Shine effect background layer */}
            
        
            {/* Image container above the shine */}
            <div className="relative z-10 flex justify-center">
              <div className=" rounded-xl w-full max-w-2xl h-64 flex items-center justify-center">
                <img 
                  src="https://ackodrive-assets.ackodrive.com/media/test_MQm3rUW.png" 
                  alt="Car" 
                  className="h-full object-contain"
                />
              </div>
            </div>
        </div>
        
            
            {/* Summary Cards */}
            <div className="grid md:grid-cols-3 gap-6">
              <div className="bg-black rounded-xl p-6 transform transition hover:scale-105 border border-gray-800">
                <div className="text-blue-400 mb-3">
                  <ThumbsUp size={28} />
                </div>
                <h3 className="text-xl font-bold mb-2">Top Performance</h3>
                <p className="text-gray-400">1.5L Turbo engine delivering 158 BHP with smooth 7-speed DCT transmission</p>
              </div>
              
              <div className="bg-black rounded-xl p-6 transform transition hover:scale-105 border border-gray-800">
                <div className="text-green-400 mb-3">
                  <Award size={28} />
                </div>
                <h3 className="text-xl font-bold mb-2">Luxury Features</h3>
                <p className="text-gray-400">Premium interiors with ventilated seats, panoramic sunroof, and Bose sound system</p>
              </div>
              
              <div className="bg-black rounded-xl p-6 transform transition hover:scale-105 border border-gray-800">
                <div className="text-yellow-400 mb-3">
                  <Shield size={28} />
                </div>
                <h3 className="text-xl font-bold mb-2">5-Star Safety</h3>
                <p className="text-gray-400">6 airbags, electronic stability control, and advanced driver assistance systems</p>
              </div>
            </div>
            
            {/* Scoring Section */}
            <div className="bg-black rounded-xl p-6 border border-gray-800">
              <h2 className="text-2xl font-bold mb-6 text-center">Performance Rating</h2>
              <div className="space-y-6">
                {performanceMetrics.map((metric, idx) => (
                  <div key={idx} className="mb-4">
                    <div className="flex justify-between items-center text-sm mb-2">
                      <div className="flex items-center">
                        <span className="text-blue-400 mr-2">{metric.icon}</span>
                        <span className="text-gray-300">{metric.label}</span>
                      </div>
                      <span className="text-blue-400 font-bold">{metric.value}%</span>
                    </div>
                    <div className="w-full bg-gray-900 rounded-full h-2">
                      <div
                        className="bg-gradient-to-r from-blue-600 to-blue-400 h-2 rounded-full transition-all duration-500"
                        style={{ width: `${metric.value}%` }}
                      ></div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
            
            {/* Expert Review */}
            <div className="bg-black rounded-xl p-6 border border-gray-800">
              <h2 className="text-2xl font-bold mb-4">Expert Review</h2>
              <div className="flex items-center mb-4">
                <div className="flex mr-2">
                  {[1, 2, 3, 4].map((_, i) => (
                    <Star key={i} size={20} className="text-yellow-400 fill-current" />
                  ))}
                  <Star size={20} className="text-yellow-400" strokeWidth={1} />
                </div>
                <span className="text-gray-400">4.5/5</span>
              </div>
              <p className="text-gray-400 leading-relaxed">
                The Creta Top Variant stands out as a premium compact SUV that excels in nearly every category.
                The turbo petrol engine offers punchy performance with excellent refinement, while the
                7-speed DCT provides seamless shifts for a luxury driving experience.
              </p>
              <p className="text-gray-400 leading-relaxed mt-4">
                Exceptional comfort features like ventilated seats, panoramic sunroof, and the Bose sound system
                elevate the interior experience. The build quality and safety features are excellent, making it
                one of the most compelling options in the segment for those seeking a feature-rich, refined SUV.
              </p>
            </div>
          </div>
        )}
        
        {/* Specs Tab */}
        {activeTab === "specs" && (
          <div className="bg-black rounded-xl p-6 border border-gray-800">
            <h2 className="text-2xl font-bold mb-6 text-center">Technical Specifications</h2>
            
            <div className="grid md:grid-cols-2 gap-8">
              <div>
                <h3 className="text-xl font-semibold text-blue-400 mb-4">Engine & Performance</h3>
                <table className="w-full">
                  <tbody>
                    {[
                      ["Engine Type", "1.5L Turbo Petrol"],
                      ["Displacement", "1482 cc"],
                      ["Max Power", "158 bhp @ 5500 rpm"],
                      ["Max Torque", "253 Nm @ 1500-3500 rpm"],
                      ["Transmission", "7-Speed DCT"],
                      ["Drive Type", "Front Wheel Drive"]
                    ].map(([key, value], idx) => (
                      <tr key={idx} className="border-b border-gray-800">
                        <td className="py-3 text-gray-500">{key}</td>
                        <td className="py-3 text-right font-medium text-gray-300">{value}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              
              <div>
                <h3 className="text-xl font-semibold text-green-400 mb-4">Dimensions & Capacity</h3>
                <table className="w-full">
                  <tbody>
                    {[
                      ["Length", "4300 mm"],
                      ["Width", "1790 mm"],
                      ["Height", "1635 mm"],
                      ["Wheelbase", "2610 mm"],
                      ["Ground Clearance", "190 mm"],
                      ["Boot Space", "433 liters"]
                    ].map(([key, value], idx) => (
                      <tr key={idx} className="border-b border-gray-800">
                        <td className="py-3 text-gray-500">{key}</td>
                        <td className="py-3 text-right font-medium text-gray-300">{value}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
            
            <div className="mt-8">
              <h3 className="text-xl font-semibold text-yellow-400 mb-4">Fuel & Performance</h3>
              <div className="grid md:grid-cols-3 gap-4">
                <div className="bg-gray-900 rounded-lg p-4 text-center border border-gray-800">
                  <p className="text-gray-500 text-sm">Mileage</p>
                  <p className="text-2xl font-bold">17.4 km/l</p>
                </div>
                <div className="bg-gray-900 rounded-lg p-4 text-center border border-gray-800">
                  <p className="text-gray-500 text-sm">Fuel Tank</p>
                  <p className="text-2xl font-bold">50 L</p>
                </div>
                <div className="bg-gray-900 rounded-lg p-4 text-center border border-gray-800">
                  <p className="text-gray-500 text-sm">0-100 km/h</p>
                  <p className="text-2xl font-bold">9.5 sec</p>
                </div>
              </div>
            </div>
          </div>
        )}
        
        {/* Features Tab */}
        {activeTab === "features" && (
          <div className="space-y-6">
            <div className="bg-black rounded-xl p-6 border border-gray-800">
              <h2 className="text-2xl font-bold mb-6 text-center">Premium Features</h2>
              
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                {features.map((feature, idx) => (
                  <div key={idx} className="bg-gray-900 rounded-lg p-4 hover:bg-gray-800 transition-colors border border-gray-800">
                    <h3 className="text-lg font-semibold text-blue-300 mb-2">{feature.name}</h3>
                    <p className="text-gray-400 text-sm">{feature.description}</p>
                  </div>
                ))}
              </div>
            </div>
            
            <div className="bg-black rounded-xl p-6 border border-gray-800">
              <h2 className="text-2xl font-bold mb-6 text-center">Safety & Technology</h2>
              
              <div className="grid grid-cols-2 gap-4">
                {[
                  "6 Airbags", 
                  "Electronic Stability Control",
                  "Hill Start Assist",
                  "Tire Pressure Monitoring",
                  "360° Camera",
                  "Blind Spot Monitor",
                  "Rear Cross Traffic Alert", 
                  "ISOFIX Child Seat Anchors"
                ].map((item, idx) => (
                  <div key={idx} className="flex items-center">
                    <div className="mr-3 text-green-400">
                      <Shield size={16} />
                    </div>
                    <span className="text-gray-400">{item}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
        
        {/* Reviews Tab */}
        {activeTab === "reviews" && (
          <div className="space-y-6">
            <div className="bg-black rounded-xl p-6 border border-gray-800">
              <h2 className="text-2xl font-bold mb-6 text-center">Critics' Reviews</h2>
              
              <div className="space-y-6">
                {reviews.map((review, idx) => (
                  <div key={idx} className="border-b border-gray-800 pb-6 last:border-0">
                    <div className="flex justify-between items-center mb-3">
                      <h3 className="text-lg font-semibold">{review.author}</h3>
                      <div className="flex items-center">
                        <div className="flex mr-1">
                          {[...Array(Math.floor(review.rating))].map((_, i) => (
                            <Star key={i} size={16} className="text-yellow-400 fill-current" />
                          ))}
                          {review.rating % 1 !== 0 && (
                            <Star size={16} className="text-yellow-400" strokeWidth={1} />
                          )}
                        </div>
                        <span className="text-sm text-gray-400">{review.rating}/5</span>
                      </div>
                    </div>
                    <p className="text-gray-400 italic">"{review.text}"</p>
                  </div>
                ))}
              </div>
            </div>
            
            <div className="bg-gradient-to-r from-black via-blue-900 to-black rounded-xl p-6 text-center border border-gray-800">
              <h2 className="text-2xl font-bold mb-3">Ready for a Test Drive?</h2>
              <p className="text-gray-300 mb-6">Experience the premium Creta top variant for yourself</p>
              <button className="bg-blue-500 text-white px-8 py-3 rounded-lg font-bold hover:bg-blue-600 transition-colors">
                Book Now
              </button>
            </div>
          </div>
        )}
      </div>
      
      {/* Footer */}
      <div className="bg-black mt-12 py-8 border-t border-gray-900">
        <div className="container mx-auto px-4 text-center text-gray-600 text-sm">
          <p>© 2025 Hyundai Motor Company. All specifications and features are subject to change without notice.</p>
          <p className="mt-2">All images shown are for illustration purposes only.</p>
        </div>
      </div>
    </div>
  );
}