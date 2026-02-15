import time
import hashlib
import os
from flask import Flask, request, jsonify

app = Flask(__name__)

# -----------------------------
# Caches
# -----------------------------
cache = {}              # Exact match cache
semantic_cache = []     # Semantic cache (simple similarity)

# -----------------------------
# Analytics
# -----------------------------
analytics = {
    "totalRequests": 0,
    "cacheHits": 0,
    "cacheMisses": 0
}

# -----------------------------
# Helper functions
# -----------------------------
def normalize(text):
    return text.lower().strip()

def get_cache_key(query):
    return hashlib.md5(query.encode()).hexdigest()

def simple_similarity(a, b):
    a_set = set(a.split())
    b_set = set(b.split())
    return len(a_set & b_set) / max(1, len(a_set | b_set))

def call_llm(query):
    time.sleep(1)  # simulate slow AI call
    return f"Summary of document for query: {query}"

# -----------------------------
# Main API
# -----------------------------
@app.route("/", methods=["POST"])
def query_api():
    start = time.time()
    analytics["totalRequests"] += 1

    data = request.json
    raw_query = data["query"]
    query = normalize(raw_query)

    # 1️⃣ Exact match cache
    key = get_cache_key(query)
    if key in cache:
        analytics["cacheHits"] += 1
        return jsonify({
            "answer": cache[key],
            "cached": True,
            "latency": int((time.time() - start) * 1000),
            "cacheKey": key
        })

    # 2️⃣ Semantic cache (simple similarity)
    for entry in semantic_cache:
        if simple_similarity(query, entry["query"]) > 0.5:
            analytics["cacheHits"] += 1
            return jsonify({
                "answer": entry["answer"],
                "cached": True,
                "latency": int((time.time() - start) * 1000),
                "cacheKey": "semantic"
            })

    # 3️⃣ Cache miss → call AI
    analytics["cacheMisses"] += 1
    answer = call_llm(query)

    # Store in caches
    cache[key] = answer
    semantic_cache.append({
        "query": query,
        "answer": answer
    })

    return jsonify({
        "answer": answer,
        "cached": False,
        "latency": int((time.time() - start) * 1000),
        "cacheKey": key
    })


@app.route("/", methods=["GET"])
def home():
    return {
        "message": "Caching API is running. Use POST / for queries and GET /analytics for metrics."
    }

# -----------------------------
# Analytics API
# -----------------------------
@app.route("/analytics", methods=["GET"])
def analytics_endpoint():
    hit_rate = analytics["cacheHits"] / max(1, analytics["totalRequests"])

    return jsonify({
        "hitRate": round(hit_rate, 2),
        "totalRequests": analytics["totalRequests"],
        "cacheHits": analytics["cacheHits"],
        "cacheMisses": analytics["cacheMisses"],
        "cacheSize": len(cache),
        "costSavings": 1.00,
        "savingsPercent": int(hit_rate * 100),
        "strategies": [
            "exact match",
            "semantic similarity",
            "LRU eviction (conceptual)",
            "TTL expiration (conceptual)"
        ]
    })

# -----------------------------
# Run app
# -----------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
