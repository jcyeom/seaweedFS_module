import pytest
from app.prompt import PromptClient

@pytest.fixture
def client():
    """
    Fixture to initialize the PromptClient for testing.
    """

    return PromptClient(ip="http://127.0.0.1", port=":8000")

def test_typo_correction(client):
    """
    Test the typo_correction method of PromptClient.
    """
    print("Starting test_typo_correction...")
    input_data = ["helo", "wrld"]
    expected_output = ["helo", "wrld"]  # Replace with actual correction logic if implemented

    result = client.typo_correction(input_data)
    
    assert result == expected_output
    print(f"test_typo_correction PASSED: input={input_data}, result={result}, expected={expected_output}", "\n")

def test_typo_detection(client):
    """
    Test the typo_detection method of PromptClient.
    """
    print("Starting test_typo_detection...")
    input_data = ["helo", "wrld"]
    expected_typos = False  # Assuming no typo detection logic yet
    expected_detected = ["helo", "wrld"]  # Replace with actual detection logic if implemented

    has_typos, detected_typos = client.typo_detection(input_data)

    assert has_typos == expected_typos
    assert detected_typos == expected_detected
    
    print(f"test_typo_detection PASSED: input={input_data}, has_typos={has_typos}, detected_typos={detected_typos}, "
          f"expected_typos={expected_typos}, expected_detected={expected_detected}", "\n")

def test_classify(client):
    """
    Test the classify method of PromptClient.
    """
    print("Starting test_classify...")
    input_data = ["hello", "world"]
    expected_output = ["hello", "world"]  # Replace with actual classification logic if implemented

    result = client.classify(input_data)

    assert result == expected_output
    print(f"test_classify PASSED: input={input_data}, result={result}, expected={expected_output}", "\n")