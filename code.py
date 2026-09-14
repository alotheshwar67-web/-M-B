"""
Sustainable Travel Planner Agent
--------------------------------
A multi-agent AI system simulation for planning eco-friendly trips.
Uses RAG-style retrieval (mock vector store) and agent orchestration.
"""

import json
import random
from typing import List, Dict, Any, Optional, Tuple

# ----------------------------------------------------------------------
# 1. MOCK VECTOR STORE (RAG Simulation)
# ----------------------------------------------------------------------
class VectorStore:
    """
    Simulates a vector database for Retrieval-Augmented Generation (RAG).
    Stores documents and retrieves relevant ones based on keyword matching.
    """
    def __init__(self):
        self.documents = {
            "destinations": [
                {"name": "Kasauli", "region": "Himachal", "distance_from_delhi": 300,
                 "eco_rating": 4.5, "type": "hill station", "best_season": "Summer",
                 "description": "Quiet hill town with pine forests and colonial charm."},
                {"name": "Lansdowne", "region": "Uttarakhand", "distance_from_delhi": 250,
                 "eco_rating": 4.2, "type": "hill station", "best_season": "Spring",
                 "description": "Offbeat hill station with oak forests and trekking trails."},
                {"name": "Binsar", "region": "Uttarakhand", "distance_from_delhi": 350,
                 "eco_rating": 4.8, "type": "hill station", "best_season": "Autumn",
                 "description": "Wildlife sanctuary, panoramic Himalayan views, eco-sensitive zone."},
                {"name": "Tarkarli", "region": "Maharashtra", "distance_from_mumbai": 500,
                 "eco_rating": 4.6, "type": "beach", "best_season": "Winter",
                 "description": "Pristine beach, scuba diving, eco-friendly homestays."},
                {"name": "Gokarna", "region": "Karnataka", "distance_from_bangalore": 480,
                 "eco_rating": 4.4, "type": "beach", "best_season": "Winter",
                 "description": "Less crowded beaches, temple town, sustainable tourism."},
            ],
            "transport": [
                {"mode": "train", "carbon_factor": 0.05, "description": "Indian Railways, low carbon"},
                {"mode": "bus", "carbon_factor": 0.08, "description": "State transport, shared"},
                {"mode": "shared_taxi", "carbon_factor": 0.12, "description": "Shared taxi from station"},
                {"mode": "flight", "carbon_factor": 0.15, "description": "Domestic flight, high carbon"},
                {"mode": "private_car", "carbon_factor": 0.14, "description": "Personal car, moderate carbon"},
            ],
            "stays": [
                {"destination": "Binsar", "type": "eco-homestay", "rating": 4.7, "community_owned": True},
                {"destination": "Kasauli", "type": "eco-resort", "rating": 4.3, "community_owned": False},
                {"destination": "Tarkarli", "type": "homestay", "rating": 4.6, "community_owned": True},
            ]
        }

    def retrieve(self, query: str, category: str) -> List[Dict]:
        """Retrieve documents from a category that match the query keywords."""
        query_lower = query.lower()
        results = []
        for doc in self.documents.get(category, []):
            # Simple keyword matching: check if any word in query appears in doc fields
            for key, value in doc.items():
                if isinstance(value, str) and query_lower in value.lower():
                    results.append(doc)
                    break
                if isinstance(value, str) and any(word in value.lower() for word in query_lower.split()):
                    results.append(doc)
                    break
        return results if results else self.documents.get(category, [])


# ----------------------------------------------------------------------
# 2. AGENTS
# ----------------------------------------------------------------------
class DestinationDiscoveryAgent:
    """Discovers eco-friendly destinations based on user query."""
    def __init__(self, vector_store: VectorStore):
        self.vs = vector_store

    def discover(self, query: str) -> List[Dict]:
        # Retrieve all destinations, then filter by type if mentioned
        all_dest = self.vs.retrieve(query, "destinations")
        query_lower = query.lower()
        if "hill station" in query_lower:
            return [d for d in all_dest if d.get("type") == "hill station"]
        elif "beach" in query_lower:
            return [d for d in all_dest if d.get("type") == "beach"]
        return all_dest


class ItineraryBuilderAgent:
    """Builds a day-wise sustainable itinerary for a chosen destination."""
    def build(self, destination: Dict, days: int = 3) -> List[str]:
        name = destination["name"]
        itinerary = [
            f"Day 1: Arrive in {name}, check into eco-homestay, local walk.",
            f"Day 2: Nature trail, visit local village, organic farm lunch.",
            f"Day 3: Sunrise point, local craft workshop, depart."
        ]
        # Extend if more days
        while len(itinerary) < days:
            itinerary.insert(-1, f"Day {len(itinerary)}: Explore nearby eco-spots, local cuisine.")
        return itinerary[:days]


class TransportStayAgent:
    """Recommends low-carbon transport and eco-certified stays."""
    def __init__(self, vector_store: VectorStore):
        self.vs = vector_store

    def recommend(self, origin: str, destination: Dict) -> Tuple[str, str]:
        dest_name = destination["name"]
        # Transport
        transport_docs = self.vs.retrieve(dest_name, "transport")
        # Prefer train if available, else bus, else shared taxi
        preferred = ["train", "bus", "shared_taxi"]
        chosen_transport = None
        for pref in preferred:
            for doc in transport_docs:
                if doc["mode"] == pref:
                    chosen_transport = doc
                    break
            if chosen_transport:
                break
        if not chosen_transport:
            chosen_transport = transport_docs[0] if transport_docs else {"mode": "train", "carbon_factor": 0.05}
        transport_str = f"{chosen_transport['mode'].title()} from {origin} to nearest station, then shared taxi to {dest_name}."

        # Stay
        stay_docs = [s for s in self.vs.retrieve(dest_name, "stays") if s["destination"] == dest_name]
        if stay_docs:
            stay = stay_docs[0]
            stay_str = f"{stay['type'].title()} in {dest_name} (community-owned: {stay['community_owned']})."
        else:
            stay_str = f"Eco-certified homestay in {dest_name} (community-owned)."
        return transport_str, stay_str


class ImpactTrackerAgent:
    """Estimates carbon footprint for different transport modes."""
    def __init__(self, vector_store: VectorStore):
        self.vs = vector_store

    def estimate(self, origin: str, destination: Dict, transport_mode: str = "train") -> float:
        distance = destination.get("distance_from_delhi") or destination.get("distance_from_mumbai") or destination.get("distance_from_bangalore") or 300
        # Find carbon factor
        factors = {doc["mode"]: doc["carbon_factor"] for doc in self.vs.retrieve("", "transport")}
        factor = factors.get(transport_mode, 0.05)
        return round(distance * factor, 2)

    def compare(self, origin: str, destination: Dict) -> Dict:
        train = self.estimate(origin, destination, "train")
        flight = self.estimate(origin, destination, "flight")
        return {"train": train, "flight": flight, "savings": round(flight - train, 2)}


# ----------------------------------------------------------------------
# 3. ORCHESTRATOR
# ----------------------------------------------------------------------
class TravelPlannerOrchestrator:
    """Coordinates all agents to produce a final sustainable travel plan."""
    def __init__(self):
        self.vs = VectorStore()
        self.dest_agent = DestinationDiscoveryAgent(self.vs)
        self.itin_agent = ItineraryBuilderAgent()
        self.transport_agent = TransportStayAgent(self.vs)
        self.impact_agent = ImpactTrackerAgent(self.vs)

    def plan_trip(self, query: str) -> str:
        # Extract origin (simple heuristic)
        origin = "Delhi"
        if "from" in query.lower():
            parts = query.lower().split("from")
            if len(parts) > 1:
                origin_part = parts[1].split("to")[0].strip()
                origin = origin_part.title()

        # 1. Discover destinations
        destinations = self.dest_agent.discover(query)
        if not destinations:
            return "No eco-friendly destinations found for your query."

        # Choose best by eco_rating
        best_dest = max(destinations, key=lambda x: x.get("eco_rating", 0))

        # 2. Build itinerary
        itinerary = self.itin_agent.build(best_dest, days=3)

        # 3. Transport & Stay
        transport, stay = self.transport_agent.recommend(origin, best_dest)

        # 4. Impact
        impact = self.impact_agent.compare(origin, best_dest)

        # 5. Format final output
        output = f"Sustainable Travel Plan for: {query}\n"
        output += f"Destination: {best_dest['name']} (Eco Rating: {best_dest['eco_rating']}/5)\n"
        output += f"Transport: {transport}\n"
        output += f"Stay: {stay}\n"
        output += "Itinerary:\n"
        for day in itinerary:
            output += f"  - {day}\n"
        output += f"Carbon Footprint Estimate (train): {impact['train']} kg CO2\n"
        output += f"Carbon Footprint Estimate (flight): {impact['flight']} kg CO2\n"
        output += f"Carbon Savings: {impact['savings']} kg CO2\n"
        output += "Local Benefit: Supports community businesses.\n"
        return output


# ----------------------------------------------------------------------
# 4. MAIN
# ----------------------------------------------------------------------
if __name__ == "__main__":
    orchestrator = TravelPlannerOrchestrator()
    print("=" * 60)
    print(" SUSTAINABLE TRAVEL PLANNER AGENT")
    print("=" * 60)
    # Example queries
    queries = [
        "Plan a 3-day trip from Delhi to a nearby hill station with minimal carbon footprint.",
        "Weekend trip from Mumbai to a sustainable beach destination.",
        "Eco-friendly trip from Bangalore to a hill station."
    ]
    for q in queries:
        print("\n" + "-" * 50)
        print(f"User Query: {q}")
        print("-" * 50)
        result = orchestrator.plan_trip(q)
        print(result)
    print("\n" + "=" * 60)
    print(" END OF PLANS")
    print("=" * 60)