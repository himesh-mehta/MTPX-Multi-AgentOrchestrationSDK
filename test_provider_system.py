#!/usr/bin/env python3
"""
Quick test script for the multi-provider TUI system.
"""

from pathlib import Path
from mtp.cli.tui_provider_factory import SUPPORTED_TUI_PROVIDERS, ProviderSelection, build_tui_provider
from mtp.cli.tui_settings import (
    DEFAULT_PROVIDER_MODELS,
    load_provider_settings,
    ensure_provider_entry,
    is_provider_configured,
)

def test_provider_list():
    """Test that all providers are listed."""
    print("✓ Supported Providers:")
    for i, provider in enumerate(SUPPORTED_TUI_PROVIDERS, 1):
        default_model = DEFAULT_PROVIDER_MODELS.get(provider, "unknown")
        print(f"  {i:2}. {provider:<15} → {default_model}")
    print(f"\n  Total: {len(SUPPORTED_TUI_PROVIDERS)} providers")


def test_settings_system():
    """Test settings loading and provider configuration check."""
    print("\n✓ Settings System:")
    
    # Create test settings path
    test_path = Path("tmp/test_settings.json")
    
    # Load settings (should create empty if not exists)
    settings = load_provider_settings(test_path)
    print(f"  Settings loaded: {type(settings)}")
    
    # Check if a provider is configured
    is_configured = is_provider_configured(settings, "openai")
    print(f"  OpenAI configured: {is_configured}")
    
    # Ensure provider entry exists
    entry = ensure_provider_entry(settings, "groq")
    print(f"  Groq entry created: {entry}")


def test_lazy_loading():
    """Test that providers can be loaded on-demand."""
    print("\n✓ Lazy Loading Test:")
    
    # Test with OpenAI (should work if openai package is installed)
    try:
        selection = ProviderSelection(
            provider_name="openai",
            model_name="gpt-4o",
            api_key="test-key",
        )
        provider = build_tui_provider(selection)
        print(f"  OpenAI provider built: {type(provider).__name__}")
    except ImportError as e:
        print(f"  OpenAI SDK not installed: {e}")
    
    # Test with Groq (should work if groq package is installed)
    try:
        selection = ProviderSelection(
            provider_name="groq",
            model_name="llama-3.3-70b-versatile",
            api_key="test-key",
        )
        provider = build_tui_provider(selection)
        print(f"  Groq provider built: {type(provider).__name__}")
    except ImportError as e:
        print(f"  Groq SDK not installed: {e}")
    
    # Test with Mistral (likely not installed)
    try:
        selection = ProviderSelection(
            provider_name="mistral",
            model_name="mistral-large-latest",
            api_key="test-key",
        )
        provider = build_tui_provider(selection)
        print(f"  Mistral provider built: {type(provider).__name__}")
    except ImportError as e:
        print(f"  Mistral SDK not installed (expected): {str(e)[:80]}...")


def main():
    print("=" * 70)
    print("MTP Multi-Provider System Test")
    print("=" * 70)
    
    test_provider_list()
    test_settings_system()
    test_lazy_loading()
    
    print("\n" + "=" * 70)
    print("✓ All tests completed!")
    print("=" * 70)


if __name__ == "__main__":
    main()
