import requests
import pytest

# Configuration
API_URL = "http://localhost:8000/analyze"
VALID_WORKSPACE = "../kmds_2_data_helper"

def test_architect_persona_audit():
    """
    Verification: Prove the Ollama pipeline works for a single persona.
    This avoids the 'marathon' and gives us a quick provable win.
    """
    # We send the full payload but we will only validate the Architect keys
    payload = {
        "config_path": VALID_WORKSPACE, 
        "output_dir": "./output"
    }

    try:
        # LLMs take time, but one persona should be faster than 30 calls
        response = requests.post(API_URL, json=payload, timeout=300)
        response.raise_for_status()
        data = response.json()

        # 1. Check if we got data back
        assert isinstance(data, list)
        assert len(data) > 0, "No notebooks were processed."

        # 2. Verify the Architect Persona specifically
        # We check the first notebook result for the expected architecture keys
        first_nb = data[0]
        
        # Check for the Architect persona key (adjusting to your service's key name)
        # Yesterday we saw 'architect_insight' or 'technical_architect_insight'
        architect_data = first_nb.get("architect_insight")
        
        assert architect_data is not None, "Architect insight was missing from the response."
        assert "quality_score" in architect_data or "score" in architect_data, "Architect score missing."
        
        print(f"\n[PASS] Architect scored {first_nb.get('notebook_name')}: {architect_data.get('quality_score')}")

    except requests.exceptions.ConnectionError:
        pytest.fail("Ollama/API Server is not running on localhost:8000")
    except Exception as e:
        pytest.fail(f"Persona Audit Failed: {str(e)}")
