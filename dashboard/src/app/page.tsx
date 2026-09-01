"use client";
import { useEffect, useState } from "react";

export default function Dashboard() {
  const [reviews, setReviews] = useState<any[]>([]);

  useEffect(() => {
    const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
    const fetchReviews = () => {
      fetch(`${API_URL}/api/reviews`)
        .then((res) => res.json())
        .then((data) => setReviews(data))
        .catch((err) => console.error(err));
    };

    fetchReviews(); // Initial load
    const interval = setInterval(fetchReviews, 3000); // Auto-refresh every 3s
    return () => clearInterval(interval);
  }, []);

  return (
    <main className="min-h-screen bg-gray-50 p-4 md:p-10">
      <div className="max-w-5xl mx-auto">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
          <div>
            <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-2">RAG Review Dashboard</h1>
            <p className="text-gray-600">Audit log and retrieval traces for LLM code reviews.</p>
          </div>
          <div className="flex items-center gap-2 text-sm text-green-600 bg-green-50 px-3 py-1.5 rounded-full border border-green-200">
            <span className="relative flex h-3 w-3">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-3 w-3 bg-green-500"></span>
            </span>
            Live Updates
          </div>
        </div>

        <div className="space-y-6">
          {reviews.length === 0 ? (
            <p className="text-gray-500">No reviews yet. Trigger a webhook!</p>
          ) : (
            reviews.map((review) => (
              <div key={review.id} className="bg-white rounded-xl shadow-sm border border-gray-200 p-4 md:p-6 transition-all hover:shadow-md">
                <div className="flex flex-col sm:flex-row justify-between items-start gap-4 mb-4">
                  <div>
                    <h3 className="text-lg font-bold text-gray-800 break-all">
                      {review.repo} <span className="text-gray-400 font-normal">#PR-{review.pr_number}</span>
                    </h3>
                    <p className="text-sm text-gray-500 font-mono mt-1 break-all">
                      📄 {review.file_path} : Line {review.line_number}
                    </p>
                  </div>
                  <span className={`shrink-0 px-3 py-1 rounded-full text-xs font-bold uppercase ${
                    review.severity === 'high' ? 'bg-red-100 text-red-700' : 
                    review.severity === 'medium' ? 'bg-yellow-100 text-yellow-700' : 
                    'bg-green-100 text-green-700'
                  }`}>
                    {review.severity} • {review.category}
                  </span>
                </div>

                <div className="bg-gray-50 p-4 rounded-lg mb-4 text-gray-700 text-sm border border-gray-100">
                  <span className="font-semibold text-indigo-600 block mb-1">AI Comment:</span> 
                  {review.comment}
                </div>

                <div className="border-t border-gray-100 pt-4">
                  <h4 className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2">Retrieval Trace (Grounded Context)</h4>
                  <div className="flex flex-wrap gap-2">
                    {review.cited_chunks && review.cited_chunks.map((chunk: string, idx: number) => (
                      <span key={idx} className="bg-indigo-50 border border-indigo-100 text-indigo-700 px-2 py-1 rounded text-xs font-mono break-all">
                        🔗 {chunk}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </main>
  );
}
