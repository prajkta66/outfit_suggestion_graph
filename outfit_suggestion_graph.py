# =============================================================================
# Outfit Suggestion Graph -- A LangGraph Learning Project
# =============================================================================
#
# This project teaches you how LangGraph works by building a fashion assistant
# that suggests outfits based on an occasion and wardrobe items.
#
# WHAT THIS DOES:
# A user enters an occasion and a list of wardrobe pieces. The system runs 3
# specialist nodes in PARALLEL (occasion matching, color pairing, accessories),
# then a decision node picks whether the look should be CASUAL or FORMAL and
# routes to the corresponding outfit plan.
#
# LANGGRAPH CONCEPTS COVERED:
# 1. State Management (Pydantic) -- user occasion and wardrobe flow through the graph
# 2. Nodes -- each function does one job (outfit match, color pairing, accessories)
# 3. Parallel Execution -- 3 specialist nodes run at the same time
# 4. Fan-in -- waiting for all 3 specialist suggestions before deciding the style
# 5. Conditional Edges -- routing to casual vs formal outfit plan
# 6. Graph Compilation -- turning the graph definition into a runnable app
#
# GRAPH STRUCTURE:
#
#   START
#     |
#   understand_request
#     |
#     +---> match_outfit_to_occasion ---+
#     |                                |
#     +---> suggest_color_pairings ----+---> decide_style
#     |                                |         |
#     +---> suggest_accessories -------+    (conditional)
#                                               /      \
#                                         casual?      formal?
#                                           |             |
#                                 casual_outfit_plan  formal_outfit_plan
#                                           |             |
#                                          END           END
#
# HOW TO RUN:
#   python outfit_suggestion_graph.py
#
# DEPENDENCIES (same as requirements.txt):
#   langgraph, langchain-openai, python-dotenv, pydantic
#
# =============================================================================

import sys
import operator
import json
from typing import Annotated

from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END

sys.stdout.reconfigure(encoding="utf-8")
load_dotenv()


class OutfitState(BaseModel):
    occasion: str = ""
    wardrobe_items: str = ""
    matched_outfit: str = ""
    color_pairings: str = ""
    accessories_suggestion: str = ""
    needs_formal_look: bool = False
    style_reason: str = ""
    final_plan: str = ""
    messages: Annotated[list, operator.add] = []


llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)


def understand_request(state: OutfitState) -> dict:
    response = llm.invoke(
        f"You are a stylish fashion assistant. "
        f"A user wants an outfit for the occasion: '{state.occasion}'. "
        f"They have wardrobe items: '{state.wardrobe_items}'. "
        f"Acknowledge the occasion and confirm the wardrobe items in 1-2 sentences."
    )
    return {
        "messages": [f"[understand_request] {response.content}"]
    }


def match_outfit_to_occasion(state: OutfitState) -> dict:
    response = llm.invoke(
        f"You are a wardrobe matching specialist. "
        f"The occasion is: '{state.occasion}'. "
        f"The available wardrobe items are: '{state.wardrobe_items}'. "
        f"Suggest ONE complete outfit that fits the occasion, using the provided items. "
        f"Describe the outfit clearly and mention why it is suitable."
    )
    return {
        "matched_outfit": response.content,
        "messages": [f"[match_outfit_to_occasion] Done"]
    }


def suggest_color_pairings(state: OutfitState) -> dict:
    response = llm.invoke(
        f"You are a color and pattern expert. "
        f"The proposed outfit is: '{state.matched_outfit}'. "
        f"Recommend color pairings and pattern combinations that enhance the look. "
        f"Keep the suggestions practical and easy to follow."
    )
    return {
        "color_pairings": response.content,
        "messages": [f"[suggest_color_pairings] Done"]
    }


def suggest_accessories(state: OutfitState) -> dict:
    response = llm.invoke(
        f"You are an accessories and footwear stylist. "
        f"The proposed outfit is: '{state.matched_outfit}'. "
        f"Recommend accessories and footwear that complete the look. "
        f"Include one or two items for a polished finish."
    )
    return {
        "accessories_suggestion": response.content,
        "messages": [f"[suggest_accessories] Done"]
    }


def decide_style(state: OutfitState) -> dict:
    response = llm.invoke(
        f"You are a fashion decision system. "
        f"Based on the occasion and wardrobe items, decide whether the outer look should be CASUAL or FORMAL. "
        f"Reply ONLY in this JSON format: {{\"needs_formal_look\": true/false, \"reason\": \"one sentence\"}}"
    )
    try:
        result = json.loads(response.content)
        needs_formal = result["needs_formal_look"]
        reason = result["reason"]
    except (json.JSONDecodeError, KeyError):
        needs_formal = False
        reason = "Could not parse decision, defaulting to casual look."

    return {
        "needs_formal_look": needs_formal,
        "style_reason": reason,
        "messages": [f"[decide_style] formal={needs_formal}"]
    }


def casual_outfit_plan(state: OutfitState) -> dict:
    response = llm.invoke(
        f"You are a casual style planner. "
        f"The matched outfit is: '{state.matched_outfit}'. "
        f"Color pairings: '{state.color_pairings}'. "
        f"Accessories: '{state.accessories_suggestion}'. "
        f"Create a casual outfit plan with styling notes and a relaxed tone."
    )
    return {
        "final_plan": f"CASUAL OUTFIT PLAN\n{'='*35}\n{response.content}",
        "messages": [f"[casual_outfit_plan] Generated casual plan"]
    }


def formal_outfit_plan(state: OutfitState) -> dict:
    response = llm.invoke(
        f"You are a formal style planner. "
        f"The matched outfit is: '{state.matched_outfit}'. "
        f"Color pairings: '{state.color_pairings}'. "
        f"Accessories: '{state.accessories_suggestion}'. "
        f"Create a formal outfit plan with polished styling notes and an elevated tone."
    )
    return {
        "final_plan": f"FORMAL OUTFIT PLAN\n{'='*35}\n{response.content}",
        "messages": [f"[formal_outfit_plan] Generated formal plan"]
    }


def route_after_decision(state: OutfitState) -> str:
    if state.needs_formal_look:
        return "formal"
    else:
        return "casual"


graph = StateGraph(OutfitState)

graph.add_node("understand_request", understand_request)
graph.add_node("match_outfit_to_occasion", match_outfit_to_occasion)
graph.add_node("suggest_color_pairings", suggest_color_pairings)
graph.add_node("suggest_accessories", suggest_accessories)
graph.add_node("decide_style", decide_style)
graph.add_node("casual_outfit_plan", casual_outfit_plan)
graph.add_node("formal_outfit_plan", formal_outfit_plan)

graph.add_edge(START, "understand_request")

graph.add_edge("understand_request", "match_outfit_to_occasion")
graph.add_edge("understand_request", "suggest_color_pairings")
graph.add_edge("understand_request", "suggest_accessories")

graph.add_edge("match_outfit_to_occasion", "decide_style")
graph.add_edge("suggest_color_pairings", "decide_style")
graph.add_edge("suggest_accessories", "decide_style")

graph.add_conditional_edges(
    "decide_style",
    route_after_decision,
    {
        "casual": "casual_outfit_plan",
        "formal": "formal_outfit_plan",
    }
)

graph.add_edge("casual_outfit_plan", END)
graph.add_edge("formal_outfit_plan", END)

app = graph.compile()


def run_outfit_suggestion(occasion: str, wardrobe_items: str):
    print("=" * 55)
    print("  OUTFIT SUGGESTION GRAPH")
    print(f"  Occasion: \"{occasion}\"")
    print(f"  Wardrobe items: \"{wardrobe_items}\"")
    print("=" * 55)

    result = app.invoke({
        "occasion": occasion,
        "wardrobe_items": wardrobe_items,
        "messages": [],
    })

    print("\n" + "=" * 55)
    print("  YOUR OUTFIT PLAN")
    print("=" * 55)
    print(f"\n{result['final_plan']}")

    print("\n" + "-" * 55)
    print("  MESSAGE LOG")
    print("-" * 55)
    for msg in result["messages"]:
        print(f"  {msg}")

    return result


if __name__ == "__main__":
    occasion_input = input("Enter the occasion: ")
    wardrobe_input = input("Enter the wardrobe items: ")
    run_outfit_suggestion(occasion_input, wardrobe_input)
