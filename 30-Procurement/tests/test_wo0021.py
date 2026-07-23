from pathlib import Path

from procurement_watch.config import load_yaml_config


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_initial_procurement_case_portfolio_has_watching_cases_and_budgets():
    expected = {
        "PC-0002": (120.0, 400.0),
        "PC-0003": (220.0, 220.0),
        "PC-0004": (150.0, 220.0),
        "PC-0005": (170.0, 350.0),
    }
    for case_id, budgets in expected.items():
        path = next((REPO_ROOT / "30-Procurement" / "cases").glob(f"{case_id}-*.yaml"))
        document = load_yaml_config(path)
        assert document["case_id"] == case_id
        assert document["status"] == "WATCHING"
        assert document["budget"]["target_price"] == budgets[0]
        assert document["budget"]["absolute_maximum_total_price"] == budgets[1]
        assert document["requirements"]


def test_rwo0012_activates_only_approved_public_sources():
    sources = load_yaml_config(REPO_ROOT / "30-Procurement" / "config" / "sources.yaml")["sources"]
    by_case = {case_id: [source for source in sources if source.get("case_id") == case_id] for case_id in ("PC-0002", "PC-0003", "PC-0004", "PC-0005")}
    assert len(by_case["PC-0002"]) == 3
    assert by_case["PC-0004"][0]["url"].endswith("tl-sg2218-a2519275.html")
    assert by_case["PC-0005"][0]["url"].endswith("or1000erm1u-a2531829.html")
    assert len(by_case["PC-0003"]) >= 2
    firewall = load_yaml_config(next((REPO_ROOT / "30-Procurement" / "cases").glob("PC-0003-*.yaml")))
    assert "market_observation" not in firewall
    assert firewall["budget"]["absolute_maximum_total_price"] == 220.0
    assert firewall["requirements"]["cpu"]["value"] == "Intel Processor N100"
    assert firewall["requirements"]["network_controller"]["value"] == "Intel i226"
