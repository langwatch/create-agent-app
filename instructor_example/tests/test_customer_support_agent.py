"""
Tests for the Instructor Customer Support Agent

This module tests the customer support agent using Instructor with Langfuse integration.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import List, Dict, Any

# Import the agent classes
from customer_support_agent import (
    CustomerSupportAgent,
    CustomerIntent,
    ToolCall,
    CustomerSupportResponse,
    get_customer_order_history,
    get_order_status,
    get_company_policy,
    get_troubleshooting_guide,
    escalate_to_human,
)


class TestCustomerIntent:
    """Test the CustomerIntent structured output model"""

    def test_valid_intent(self):
        """Test creating a valid CustomerIntent"""
        intent = CustomerIntent(
            intent="technical_support", confidence=0.95, requires_tool=True
        )
        assert intent.intent == "technical_support"
        assert intent.confidence == 0.95
        assert intent.requires_tool is True

    def test_invalid_intent(self):
        """Test that invalid intent raises validation error"""
        with pytest.raises(ValueError):
            CustomerIntent(intent="invalid_intent", confidence=0.5, requires_tool=False)

    def test_confidence_bounds(self):
        """Test confidence score bounds validation"""
        # Test valid confidence
        intent = CustomerIntent(
            intent="order_inquiry", confidence=0.5, requires_tool=True
        )
        assert intent.confidence == 0.5

        # Test invalid confidence (too high)
        with pytest.raises(ValueError):
            CustomerIntent(intent="order_inquiry", confidence=1.5, requires_tool=True)

        # Test invalid confidence (too low)
        with pytest.raises(ValueError):
            CustomerIntent(intent="order_inquiry", confidence=-0.1, requires_tool=True)


class TestToolCall:
    """Test the ToolCall structured output model"""

    def test_valid_tool_call(self):
        """Test creating a valid ToolCall"""
        tool_call = ToolCall(tool_name="get_customer_order_history", parameters={})
        assert tool_call.tool_name == "get_customer_order_history"
        assert tool_call.parameters == {}

    def test_tool_call_with_parameters(self):
        """Test ToolCall with parameters"""
        tool_call = ToolCall(
            tool_name="get_order_status", parameters={"order_id": "12345"}
        )
        assert tool_call.tool_name == "get_order_status"
        assert tool_call.parameters == {"order_id": "12345"}

    def test_invalid_tool_name(self):
        """Test that invalid tool name raises validation error"""
        with pytest.raises(ValueError):
            ToolCall(tool_name="invalid_tool", parameters={})


class TestCustomerSupportResponse:
    """Test the CustomerSupportResponse structured output model"""

    def test_valid_response(self):
        """Test creating a valid CustomerSupportResponse"""
        intent = CustomerIntent(
            intent="technical_support", confidence=0.9, requires_tool=True
        )

        response = CustomerSupportResponse(
            message="I can help you with your technical issue.",
            intent=intent,
            tool_calls=[],
            should_escalate=False,
        )

        assert response.message == "I can help you with your technical issue."
        assert response.intent == intent
        assert response.tool_calls == []
        assert response.should_escalate is False

    def test_response_with_tool_calls(self):
        """Test CustomerSupportResponse with tool calls"""
        intent = CustomerIntent(
            intent="technical_support", confidence=0.8, requires_tool=True
        )

        tool_call = ToolCall(
            tool_name="get_troubleshooting_guide", parameters={"guide": "internet"}
        )

        response = CustomerSupportResponse(
            message="Let me check the troubleshooting guide for you.",
            intent=intent,
            tool_calls=[tool_call],
            should_escalate=False,
        )

        assert len(response.tool_calls) == 1
        assert response.tool_calls[0].tool_name == "get_troubleshooting_guide"


class TestToolFunctions:
    """Test the individual tool functions"""

    def test_get_customer_order_history(self):
        """Test getting customer order history"""
        result = get_customer_order_history()
        assert isinstance(result, list)
        assert len(result) > 0

        # Check structure of first order
        first_order = result[0]
        assert "order_id" in first_order
        assert "items" in first_order
        assert "total_amount" in first_order
        assert "order_date" in first_order

    def test_get_order_status(self):
        """Test getting order status"""
        result = get_order_status("9127412")
        assert isinstance(result, dict)
        assert "order_id" in result
        assert "status" in result
        assert result["order_id"] == "9127412"

    def test_get_order_status_invalid_id(self):
        """Test getting order status with invalid ID"""
        with pytest.raises(ValueError):
            get_order_status("invalid_id")

    def test_get_company_policy(self):
        """Test getting company policy"""
        result = get_company_policy()
        assert isinstance(result, dict)
        assert "document_id" in result
        assert "document_name" in result
        assert "document_content" in result
        assert result["document_id"] == "company_policy"

    def test_get_troubleshooting_guide(self):
        """Test getting troubleshooting guide"""
        result = get_troubleshooting_guide("internet")
        assert isinstance(result, dict)
        assert "document_id" in result
        assert "document_name" in result
        assert "document_content" in result
        assert result["document_id"] == "troubleshooting_internet"

    def test_get_troubleshooting_guide_invalid_guide(self):
        """Test getting troubleshooting guide with invalid guide type"""
        with pytest.raises(ValueError):
            get_troubleshooting_guide("invalid_guide")

    def test_escalate_to_human(self):
        """Test escalating to human agent"""
        result = escalate_to_human(
            reason="Complex technical issue",
            urgency="high",
            summary="Customer needs advanced support",
        )
        assert isinstance(result, dict)
        assert result["status"] == "escalated"
        assert result["reason"] == "Complex technical issue"
        assert result["urgency"] == "high"


class TestCustomerSupportAgent:
    """Test the CustomerSupportAgent class"""

    @pytest.fixture
    def mock_client(self):
        """Mock the OpenAI client"""
        with patch("customer_support_agent.client") as mock_client:
            yield mock_client

    @pytest.fixture
    def mock_langfuse(self):
        """Mock the Langfuse client"""
        with patch("customer_support_agent.langfuse") as mock_langfuse:
            yield mock_langfuse

    @pytest.fixture
    def agent(self, mock_client, mock_langfuse):
        """Create an agent instance with mocked dependencies"""
        return CustomerSupportAgent()

    def test_agent_initialization(self, agent):
        """Test agent initialization"""
        assert agent.client is not None
        assert agent.langfuse is not None

    @patch("customer_support_agent.observe")
    def test_classify_intent(self, mock_observe, agent, mock_client):
        """Test intent classification"""
        # Mock the response
        mock_response = CustomerIntent(
            intent="technical_support", confidence=0.9, requires_tool=True
        )
        mock_client.chat.completions.create.return_value = mock_response

        result = agent.classify_intent("I need help with my internet")

        assert result.intent == "technical_support"
        assert result.confidence == 0.9
        assert result.requires_tool is True

        # Verify the client was called
        mock_client.chat.completions.create.assert_called_once()

    @patch("customer_support_agent.observe")
    def test_generate_response(self, mock_observe, agent, mock_client):
        """Test response generation"""
        intent = CustomerIntent(
            intent="technical_support", confidence=0.8, requires_tool=True
        )

        # Mock the response
        mock_response = CustomerSupportResponse(
            message="I can help you with that.",
            intent=intent,
            tool_calls=[],
            should_escalate=False,
        )
        mock_client.chat.completions.create.return_value = mock_response

        result = agent.generate_response("I need help", intent)

        assert result.message == "I can help you with that."
        assert result.intent == intent

        # Verify the client was called
        mock_client.chat.completions.create.assert_called_once()

    def test_execute_tools(self, agent):
        """Test tool execution"""
        tool_calls = [
            ToolCall(tool_name="get_customer_order_history", parameters={}),
            ToolCall(tool_name="get_company_policy", parameters={}),
        ]

        results = agent.execute_tools(tool_calls)

        assert len(results) == 2
        assert results[0]["tool"] == "get_customer_order_history"
        assert results[1]["tool"] == "get_company_policy"
        assert "result" in results[0]
        assert "result" in results[1]

    def test_execute_tools_with_error(self, agent):
        """Test tool execution with error handling"""
        tool_calls = [
            ToolCall(
                tool_name="get_order_status", parameters={"order_id": "invalid_id"}
            )
        ]

        results = agent.execute_tools(tool_calls)

        assert len(results) == 1
        assert results[0]["tool"] == "get_order_status"
        assert "error" in results[0]

    @patch("customer_support_agent.observe")
    def test_run_method(self, mock_observe, agent, mock_client):
        """Test the main run method"""
        # Mock intent classification
        intent = CustomerIntent(
            intent="technical_support", confidence=0.9, requires_tool=True
        )

        # Mock response generation
        response = CustomerSupportResponse(
            message="I can help you with your technical issue.",
            intent=intent,
            tool_calls=[],
            should_escalate=False,
        )

        mock_client.chat.completions.create.side_effect = [intent, response]

        result = agent.run("I need help with my internet")

        assert result == "I can help you with your technical issue."
        assert mock_client.chat.completions.create.call_count == 2

    def test_score_interaction(self, agent, mock_langfuse):
        """Test interaction scoring"""
        # Mock current observation and trace IDs
        mock_langfuse.get_current_observation_id.return_value = "obs_123"
        mock_langfuse.get_current_trace_id.return_value = "trace_456"

        intent = CustomerIntent(
            intent="technical_support", confidence=0.9, requires_tool=True
        )

        response = CustomerSupportResponse(
            message="I can help you.",
            intent=intent,
            tool_calls=[],
            should_escalate=False,
        )

        # This should not raise an exception
        agent.score_interaction("test message", response, intent)

        # Verify scores were created
        assert mock_langfuse.create_score.call_count == 2


def test_main_function():
    """Test the main function"""
    with patch("customer_support_agent.CustomerSupportAgent") as mock_agent_class:
        mock_agent = Mock()
        mock_agent.run.return_value = "Test response"
        mock_agent_class.return_value = mock_agent

        # Import and run main
        from customer_support_agent import main

        main()

        # Verify agent was created and run was called
        mock_agent_class.assert_called_once()
        assert mock_agent.run.call_count == 4  # 4 test messages


if __name__ == "__main__":
    pytest.main([__file__])
