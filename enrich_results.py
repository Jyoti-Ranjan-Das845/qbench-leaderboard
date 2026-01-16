"""Enrich results.json with participant name from scenario.toml"""

import argparse
import json
import sys
from pathlib import Path

try:
    import tomli
except ImportError:
    try:
        import tomllib as tomli
    except ImportError:
        print("Error: tomli required. Install with: pip install tomli")
        sys.exit(1)


def parse_scenario(scenario_path: Path) -> dict:
    """Parse scenario.toml and extract participant information."""
    toml_data = scenario_path.read_text()
    data = tomli.loads(toml_data)

    participants = data.get("participants", [])
    if not participants:
        print("Warning: No participants found in scenario.toml")
        return {}

    # Get the first participant's name (QBench only supports one purple agent)
    if len(participants) > 1:
        print(f"Warning: Multiple participants found ({len(participants)}). Using first one.")

    participant_name = participants[0].get("name", "unknown")
    return {"name": participant_name}


def enrich_results(results_path: Path, participant_info: dict) -> None:
    """Add participant name to results.json."""
    if not results_path.exists():
        print(f"Error: {results_path} not found")
        sys.exit(1)

    # Read results.json
    with open(results_path, 'r') as f:
        results = json.load(f)

    # Add participant name to participants object
    if "participants" not in results:
        print("Warning: No participants section in results.json")
        results["participants"] = {}

    # Add name field
    results["participants"]["name"] = participant_info.get("name", "unknown")

    # Write back
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"Enriched {results_path} with participant name: {participant_info.get('name')}")


def main():
    parser = argparse.ArgumentParser(description="Enrich results.json with participant name")
    parser.add_argument("--scenario", type=Path, required=True, help="Path to scenario.toml")
    parser.add_argument("--results", type=Path, required=True, help="Path to results.json")
    args = parser.parse_args()

    if not args.scenario.exists():
        print(f"Error: {args.scenario} not found")
        sys.exit(1)

    participant_info = parse_scenario(args.scenario)
    enrich_results(args.results, participant_info)


if __name__ == "__main__":
    main()
