import pytest
from unittest.mock import MagicMock, patch
from core.code_arena.sandbox_client import SandboxArena
from core.code_arena.tournament import Tournament

# --- Sandbox Client Tests ---

def test_sandbox_health_check_success():
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        client = SandboxArena()
        assert client.check_health() is True

def test_sandbox_health_check_fail():
    with patch('requests.get') as mock_get:
        import requests
        mock_get.side_effect = requests.exceptions.RequestException("Connection Refused")
        client = SandboxArena()
        assert client.check_health() is False

def test_sandbox_execute_code_success():
    with patch('requests.post') as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"stdout": "Hello", "stderr": ""}
        
        client = SandboxArena()
        result = client.execute_code("print('Hello')")
        
        assert result["stdout"] == "Hello"
        mock_post.assert_called_once()


# --- Tournament Tests ---

@pytest.fixture
def mock_arena():
    arena = MagicMock(spec=SandboxArena)
    arena_return_pass = {"stdout": "55", "stderr": ""}
    # Configure mock to always return valid expected output for the test case
    # This is simplified; in real test we might want dynamic side effects
    arena.execute_code.return_value = arena_return_pass
    return arena

def test_tournament_code_extraction():
    t = Tournament("url_a", "url_b")
    
    raw_md_1 = "Here is the code:\n```python\ndef solution(): pass\n```"
    assert t._extract_code_block(raw_md_1) == "def solution(): pass"
    
    raw_md_2 = "```\nprint('generic')\n```"
    assert t._extract_code_block(raw_md_2) == "print('generic')"

@patch("requests.post")
def test_tournament_round_flow(mock_post, mock_arena):
    # Mock LLM generation
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {
        "content": "```python\ndef solution(n): return 55\n```"
    }

    t = Tournament("url_a", "url_b")
    t.arena = mock_arena # Inject mock arena
    
    challenge = "Fibonacci 10"
    test_cases = [{"input": "10", "expected": 55}]
    
    result = t.run_round(challenge, test_cases)
    
    assert result["winner"] == "Draw" # Both succeed
    assert result["fighter_a"]["score"] == 1
    assert result["fighter_b"]["score"] == 1
    assert t.scores["A"] == 0 # Tie
