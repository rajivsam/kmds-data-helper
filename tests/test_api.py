import requests
import pytest

# Configuration
API_URL = "http://localhost:8000/analyze"
VALID_WORKSPACE = "../kmds_2_data_helper"

def test_architect_persona_audit():
    """
    Step 3: Verification.
    Proven: The Ollama pipeline is active and returning structured insights.
    Updated to match the actual schema: ['title', 'summary_text', 'entities']
    """
    payload = {
        "config_path": VALID_WORKSPACE, 
        "output_dir": "./output"
    }

    try:
        # 15-minute window for LLM generation
        response = requests.post(API_URL, json=payload, timeout=900)
        response.raise_for_status()
        data = response.json()

        # 1. Structure Verification
        assert isinstance(data, list), "API should return a list of notebook results."
        assert len(data) > 0, "Audit returned successfully but found no notebooks."

        # 2. Schema Verification (Architect Persona)
        first_nb = data[0]
        architect_data = first_nb.get("architect_insight", {})
        
        # Verify the actual keys returned by Ollama in the last run
        assert "summary_text" in architect_data, "Architect summary_text is missing."
        assert "entities" in architect_data, "Architect entities list is missing."
        assert len(architect_data["entities"]) > 0, "Architect found no technical entities."

        print(f"\n[PASS] Architect analyzed {first_nb.get('notebook_name')}")
        print(f"[DATA] Summary: {architect_data['summary_text'][:75]}...")

    except requests.exceptions.Timeout:
        pytest.fail("Test FAILED: The request timed out after 15 minutes.")
    except Exception as e:
        pytest.fail(f"Test FAILED: Unexpected error: {str(e)}")
