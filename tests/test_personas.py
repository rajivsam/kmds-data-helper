import pytest
import requests
import warnings
from pathlib import Path

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore", category=UserWarning, module="requests")

API_URL = "http://localhost:8000/analyze"
# POINT OF TRUTH: Verified active workspace
VALID_WORKSPACE = "/home/rajiv/programming/kmds_data_helper"

@pytest.mark.parametrize("persona", ["Architect", "Scientist", "Tech Lead", "Modeling Ds"])
def test_persona_audit(persona):
    """
    Validates that the discovery engine finds the persona file in the personas/ 
    folder and returns a valid analysis for each notebook.
    """
    payload = {"config_path": VALID_WORKSPACE}

    try:
        # LLM generation window
        response = requests.post(API_URL, json=payload, timeout=3600)
        response.raise_for_status()
        data = response.json()

        # 1. Structure Verification
        assert isinstance(data, list), f"Expected list of results, got {type(data)}"
        assert len(data) > 0, "Audit returned successfully but found no notebooks to analyze."

        # 2. Filter for the persona (Case-Insensitive)
        persona_results = [
            r for r in data 
            if r.get("persona", "").lower() == persona.lower()
        ]
        
        # Diagnostic check if the list is empty
        if not persona_results:
            found_on_server = {r.get("persona") for r in data}
            pytest.fail(
                f"Discovery Mismatch: Test wanted '{persona}', but server found: {found_on_server}. "
                f"Check if {persona.lower().replace(' ', '_')}.yaml exists in {VALID_WORKSPACE}/personas/"
            )

        # 3. Content Verification (Checking the first notebook result)
        first_nb_result = persona_results[0]
        analysis = first_nb_result.get("analysis", {})
        
        # Ensure the LLM didn't return an error block
        assert "error" not in analysis, f"LLM Error for {persona}: {analysis.get('error')}"
        
        # Ensure we actually got data back
        assert len(analysis.keys()) > 0, f"Analysis for {persona} returned empty JSON content."

        print(f"\n[PASS] {persona} validated successfully for notebook: {first_nb_result.get('notebook')}")

    except requests.exceptions.HTTPError as e:
        error_detail = e.response.json().get("detail", e.response.text)
        pytest.fail(f"Server Error (400/500): {error_detail}")
    except Exception as e:
        pytest.fail(f"Test FAILED for {persona}: {str(e)}")
