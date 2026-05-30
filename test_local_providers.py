#!/usr/bin/env python3
"""
Test script for local provider integration.

This script tests the local provider discovery and configuration without
requiring a full TUI session.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from mtp.cli.tui_local_providers import (
    discover_ollama_models,
    discover_lmstudio_models,
    check_ollama_health,
    check_lmstudio_health,
    is_local_capable_provider,
    get_default_endpoint,
    get_setup_instructions,
)


def test_provider_classification():
    """Test provider type classification."""
    print("=" * 70)
    print("TEST: Provider Classification")
    print("=" * 70)
    
    print(f"ollama is local-capable: {is_local_capable_provider('ollama')}")
    print(f"lmstudio is local-capable: {is_local_capable_provider('lmstudio')}")
    print(f"openai is local-capable: {is_local_capable_provider('openai')}")
    print(f"groq is local-capable: {is_local_capable_provider('groq')}")
    print()


def test_default_endpoints():
    """Test default endpoint retrieval."""
    print("=" * 70)
    print("TEST: Default Endpoints")
    print("=" * 70)
    
    print(f"Ollama local endpoint: {get_default_endpoint('ollama', 'local')}")
    print(f"LMStudio local endpoint: {get_default_endpoint('lmstudio', 'local')}")
    print()


def test_ollama_discovery():
    """Test Ollama model discovery."""
    print("=" * 70)
    print("TEST: Ollama Model Discovery")
    print("=" * 70)
    
    endpoint = "http://localhost:11434"
    print(f"Discovering models from: {endpoint}")
    print()
    
    result = discover_ollama_models(endpoint, timeout=3)
    
    if result.success:
        print(f"✓ Success! Found {len(result.models)} model(s)")
        print()
        for model in result.models:
            print(f"  • {model.name}")
            if model.size:
                print(f"    Size: {model.size}")
            if model.family:
                print(f"    Family: {model.family}")
            if model.parameter_size:
                print(f"    Parameters: {model.parameter_size}")
            print()
    else:
        print(f"✗ Failed: {result.error_message}")
        print()
        print("Setup instructions:")
        for instruction in get_setup_instructions("ollama"):
            print(f"  {instruction}")
        print()


def test_lmstudio_discovery():
    """Test LM Studio model discovery."""
    print("=" * 70)
    print("TEST: LM Studio Model Discovery")
    print("=" * 70)
    
    endpoint = "http://127.0.0.1:1234/v1"
    print(f"Discovering models from: {endpoint}")
    print()
    
    result = discover_lmstudio_models(endpoint, timeout=3)
    
    if result.success:
        print(f"✓ Success! Found {len(result.models)} model(s)")
        print()
        for model in result.models:
            print(f"  • {model.name}")
            print()
    else:
        print(f"✗ Failed: {result.error_message}")
        print()
        print("Setup instructions:")
        for instruction in get_setup_instructions("lmstudio"):
            print(f"  {instruction}")
        print()


def test_health_checks():
    """Test provider health checks."""
    print("=" * 70)
    print("TEST: Health Checks")
    print("=" * 70)
    
    # Ollama
    print("Checking Ollama health...")
    ollama_health = check_ollama_health("http://localhost:11434", timeout=3)
    print(f"  Healthy: {ollama_health.is_healthy}")
    print(f"  Message: {ollama_health.message}")
    print(f"  Model count: {ollama_health.model_count}")
    print()
    
    # LM Studio
    print("Checking LM Studio health...")
    lmstudio_health = check_lmstudio_health("http://127.0.0.1:1234/v1", timeout=3)
    print(f"  Healthy: {lmstudio_health.is_healthy}")
    print(f"  Message: {lmstudio_health.message}")
    print(f"  Model count: {lmstudio_health.model_count}")
    print()


def main():
    """Run all tests."""
    print()
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 15 + "MTP Local Provider Integration Tests" + " " * 16 + "║")
    print("╚" + "═" * 68 + "╝")
    print()
    
    test_provider_classification()
    test_default_endpoints()
    test_ollama_discovery()
    test_lmstudio_discovery()
    test_health_checks()
    
    print("=" * 70)
    print("All tests completed!")
    print("=" * 70)
    print()


if __name__ == "__main__":
    main()
