"""
LangGraph Studio Task - Business Data Agent
Author: Benyamin Ramezani
Analyzes sales and cost data over two days and generates actionable business recommendations.
"""

from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from data import seven_day_data


import json


class BusinessDay(TypedDict):
    sales: float
    cost: float
    customers: int


# Define the input
class InputData(TypedDict):
    today: BusinessDay
    yesterday: BusinessDay


# Define the state that will flow between nodes
class BusinessState(TypedDict):
    today: BusinessDay
    yesterday: BusinessDay
    profit_today: float
    profit_status: str
    profit_change_pct: float
    revenue_change_pct: float
    cost_change_pct: float
    cac_change_pct: float
    alerts: list[str]
    recommendations: list[str]


# define nodes
def input_node(state: InputData) -> BusinessState:
    return {
        "today": state["today"],
        "yesterday": state["yesterday"],
        "alerts": [],
        "recommendations": []
    }


def processing_node(state: BusinessState) -> BusinessState:
    today = state["today"]
    yesterday = state["yesterday"]

    # Profit
    profit_today = today["sales"] - today["cost"]
    yesterday_profit = yesterday["sales"] - yesterday["cost"]
    if profit_today > 0:
        profit_status = "positive"
    elif profit_today < 0:
        profit_status = "negative"
    else:
        profit_status = "zero"

    # Percentage changes

    if yesterday["sales"] == 0:
        revenue_change = float("inf") if today["sales"] != 0 else 0.0
    else:
        revenue_change = ((today["sales"] - yesterday["sales"]) / yesterday["sales"]) * 100

    if yesterday["cost"] == 0:
        cost_change = float("inf") if today["cost"] != 0 else 0.0
    else:
        cost_change = ((today["cost"] - yesterday["cost"]) / yesterday["cost"]) * 100 if yesterday["cost"] != 0 else 0

    # CACs
    cac_today = today["cost"] / today["customers"] if today["customers"] != 0 else float('inf')
    cac_yesterday = yesterday["cost"] / yesterday["customers"] if yesterday["customers"] != 0 else float('inf')
    cac_change = ((cac_today - cac_yesterday) / cac_yesterday) * 100 if cac_yesterday != 0 else 0

    # profit change
    if yesterday_profit == 0:
        profit_change = float("inf") if yesterday_profit != 0 else 0.0
    else:
        profit_change = ((profit_today - yesterday_profit) / yesterday_profit) * 100 if yesterday_profit != 0 else 0
    return {
        **state,
        "profit_today": profit_today,
        "profit_status": profit_status,
        "profit_change_pct": profit_change,
        "revenue_change_pct": revenue_change,
        "cost_change_pct": cost_change,
        "cac_change_pct": cac_change,
    }


def recommendation_node(state: BusinessState) -> BusinessState:
    if state["profit_today"] < 0:
        state["alerts"].append("Profit is negative")
        state["recommendations"].append("Reduce costs")

    if state["cac_change_pct"] > 0.20:
        state["alerts"].append("CAC increased by more than 20%")
        state["recommendations"].append("Review marketing campaigns")

    if state["revenue_change_pct"] > 0:
        state["recommendations"].append("Consider increasing advertising budget")

    return state


# Create the state graph object
def build_graph():
    builder = StateGraph(BusinessState, input_schema=InputData)
    builder.add_node("input", input_node)
    builder.add_node("process", processing_node)
    builder.add_node("recommend", recommendation_node)

    builder.add_edge(START, "input")
    builder.add_edge("input", "process")
    builder.add_edge("process", "recommend")
    builder.add_edge("recommend", END)

    return builder.compile()



if __name__ == '__main__':
    graph = build_graph()


    ## an example for the last two days

    input_data = {
        "today": seven_day_data[-1],
        "yesterday": seven_day_data[-2]}
    result = graph.invoke(input_data)
    print(json.dumps(result, indent=2))

    from test import test_agent
    test_agent()
