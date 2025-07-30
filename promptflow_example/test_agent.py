#!/usr/bin/env python3
"""
Simple test script to verify the Promptflow customer support agent works.
"""

import os
import dotenv

# Load environment variables
dotenv.load_dotenv()


def test_agent():
    """Test the agent with a simple query."""
    try:
        from customer_support_agent import agent

        print("Testing Promptflow Customer Support Agent...")
        print("=" * 50)

        # Test query
        query = "Hello, I need help with my order"
        print(f"Query: {query}")
        print("-" * 30)

        # Get response
        response = agent.chat(query)
        print(f"Response: {response}")
        print("=" * 50)

        print("✅ Agent test completed successfully!")

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all dependencies are installed with 'uv sync'")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Check your environment variables and API configuration")


if __name__ == "__main__":
    test_agent()
