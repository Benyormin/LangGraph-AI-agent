from main import build_graph


def test_agent():
    sample_input = {
        "yesterday": {
            "sales": 100.0,
            "cost": 100.0,
            "customers": 10
        },
        "today": {
            "sales": 300.0,
            "cost": 200.0,
            "customers": 10
        }
    }

    g = build_graph()
    result = g.invoke(sample_input)

    assert result["profit_today"] == 100.0, "Incorrect profit"
    assert result["profit_status"] == "positive", "Profit status should be positive"
    assert result["revenue_change_pct"] == 200.0, "Revenue change should be 200%"
    assert result["cost_change_pct"] == 100.0, "Cost change should be 100%"
    assert result["cac_change_pct"] == 100.0, "CAC change should be 100%"
    assert "Consider increasing advertising budget" in result["recommendations"], "Missing ad budget recommendation"

    print("✅ All tests passed.")
