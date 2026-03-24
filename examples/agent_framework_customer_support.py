"""
Customer Support Agent - Agent Framework Implementation

Demonstrates how to build a production-ready agent using Microsoft Agent Framework.
"""

import asyncio
from typing import Annotated, Optional
import logging

from core.config_manager import ConfigManager
from core.state_manager import StateManager
from core.agent_framework_client import AgentFrameworkClient
from core.logging_service import LoggingService


# ============================================================================
# Tool Definitions
# ============================================================================

def search_knowledge_base(
    query: Annotated[str, "The search query to find relevant information"]
) -> str:
    """
    Search the knowledge base for relevant information.
    
    This would typically query a vector database or search service.
    """
    # Simulate knowledge base search
    knowledge = {
        "return policy": "You can return items within 30 days of purchase with receipt.",
        "shipping": "Standard shipping takes 5-7 business days. Express shipping is available.",
        "warranty": "All products come with a 1-year manufacturer warranty.",
        "support hours": "Our support team is available Monday-Friday, 9 AM - 6 PM EST."
    }
    
    for key, value in knowledge.items():
        if key in query.lower():
            return f"Found information: {value}"
    
    return f"Searched for '{query}' but no specific information found. Please provide more details."


def create_support_ticket(
    customer_email: Annotated[str, "Customer's email address"],
    issue_category: Annotated[str, "Category of the issue (billing, technical, product, etc.)"],
    description: Annotated[str, "Detailed description of the issue"],
    priority: Annotated[str, "Priority level: low, medium, high"] = "medium"
) -> str:
    """
    Create a support ticket for customer issues that require escalation.
    """
    import random
    ticket_id = f"TKT-{random.randint(10000, 99999)}"
    
    return (
        f"Support ticket created successfully!\n"
        f"Ticket ID: {ticket_id}\n"
        f"Category: {issue_category}\n"
        f"Priority: {priority}\n"
        f"Customer: {customer_email}\n"
        f"Our team will respond within 24 hours."
    )


def send_email_notification(
    recipient: Annotated[str, "Recipient email address"],
    subject: Annotated[str, "Email subject line"],
    message: Annotated[str, "Email message body"]
) -> str:
    """
    Send an email notification to a customer.
    """
    # Simulate email sending
    return f"Email sent to {recipient} with subject: '{subject}'"


def check_order_status(
    order_id: Annotated[str, "The order ID to check"]
) -> str:
    """
    Check the status of a customer's order.
    """
    # Simulate order lookup
    import random
    statuses = [
        f"Order {order_id} is currently being processed and will ship within 2 business days.",
        f"Order {order_id} has been shipped! Tracking number: 1Z999AA1012345678",
        f"Order {order_id} was delivered on January 3rd, 2026.",
        f"Order {order_id} is scheduled for delivery today."
    ]
    
    return random.choice(statuses)


# ============================================================================
# Customer Support Agent
# ============================================================================

class CustomerSupportAgentFramework:
    """
    Customer Support Agent built with Microsoft Agent Framework.
    
    This agent handles:
    - Product inquiries
    - Order tracking
    - Support ticket creation
    - Knowledge base searches
    """
    
    def __init__(
        self,
        config_manager: ConfigManager,
        state_manager: StateManager,
        logger: Optional[logging.Logger] = None
    ):
        """Initialize the agent"""
        self.config = config_manager
        self.state = state_manager
        self.logger = logger or LoggingService.get_logger(self.__class__.__name__)
        
        # Initialize Agent Framework client
        self.af_client = AgentFrameworkClient(config_manager, logger)
        
        # Agent configuration
        self.agent_name = "Customer Support Agent"
        self.instructions = """You are a helpful and professional customer support agent for Agentic CoE.

Your responsibilities:
- Answer customer questions about products, policies, and services
- Help customers track their orders
- Create support tickets for complex issues that need escalation
- Search the knowledge base for accurate information
- Provide friendly, clear, and concise responses

Guidelines:
- Always be polite and professional
- Use the available tools to get accurate information
- Create tickets for issues you cannot resolve directly
- Ask clarifying questions when needed
- Acknowledge customer concerns empathetically

When you need to escalate an issue, create a support ticket with all relevant details."""
        
        # Define tools
        self.tools = [
            search_knowledge_base,
            create_support_ticket,
            send_email_notification,
            check_order_status
        ]
        
        self.logger.info("CustomerSupportAgentFramework initialized")
    
    async def chat(self, user_input: str, thread_id: Optional[str] = None):
        """
        Have a conversation with the agent (streaming).
        
        Args:
            user_input: User's message
            thread_id: Optional conversation thread ID for continuity
        """
        try:
            # Create or retrieve agent
            async with await self.af_client.create_chat_agent(
                agent_name=self.agent_name,
                instructions=self.instructions,
                tools=self.tools,
                temperature=0.7
            ) as agent:
                # Get or create thread
                thread = None
                if thread_id:
                    # In production, retrieve thread from state manager
                    thread = agent.get_new_thread()
                else:
                    thread = agent.get_new_thread()
                
                # Stream response
                print("\n🤖 Agent: ", end="", flush=True)
                
                full_response = ""
                tool_calls_made = []
                
                async for chunk in agent.run_stream(user_input, thread=thread):
                    if chunk.text:
                        print(chunk.text, end="", flush=True)
                        full_response += chunk.text
                    
                    # Track tool calls
                    if (chunk.raw_representation and 
                        hasattr(chunk.raw_representation, 'raw_representation')):
                        raw = chunk.raw_representation.raw_representation
                        if (hasattr(raw, 'status') and 
                            hasattr(raw, 'step_details') and 
                            raw.status == "completed"):
                            if hasattr(raw.step_details, 'tool_calls'):
                                for tool_call in raw.step_details.tool_calls:
                                    if hasattr(tool_call, 'function'):
                                        tool_calls_made.append(tool_call.function.name)
                
                print("\n")
                
                # Show tool usage
                if tool_calls_made:
                    print(f"🔧 Tools used: {', '.join(set(tool_calls_made))}\n")
                
                return {
                    "response": full_response,
                    "tools_used": tool_calls_made,
                    "thread_id": str(thread.id) if hasattr(thread, 'id') else None
                }
                
        except Exception as e:
            self.logger.error(f"Error in chat: {str(e)}", exc_info=True)
            raise
    
    async def chat_non_streaming(self, user_input: str, thread_id: Optional[str] = None):
        """
        Have a conversation with the agent (non-streaming).
        
        Args:
            user_input: User's message
            thread_id: Optional conversation thread ID for continuity
        """
        try:
            async with await self.af_client.create_chat_agent(
                agent_name=self.agent_name,
                instructions=self.instructions,
                tools=self.tools,
                temperature=0.7
            ) as agent:
                thread = agent.get_new_thread()
                
                result = await agent.run(user_input, thread=thread)
                
                return {
                    "response": result.text,
                    "thread_id": str(thread.id) if hasattr(thread, 'id') else None
                }
                
        except Exception as e:
            self.logger.error(f"Error in chat: {str(e)}", exc_info=True)
            raise


# ============================================================================
# Example Usage
# ============================================================================

async def main():
    """Run example conversations with the customer support agent"""
    
    print("=" * 80)
    print("🎯 Customer Support Agent - Microsoft Agent Framework Demo")
    print("=" * 80)
    
    # Initialize components
    config_manager = ConfigManager(config_dir="configs", environment="dev")
    state_manager = StateManager(use_redis=False)
    
    # Create agent
    agent = CustomerSupportAgentFramework(
        config_manager=config_manager,
        state_manager=state_manager
    )
    
    # Example conversations
    conversations = [
        "Hi! Can you tell me about your return policy?",
        "I need to check the status of my order TKT-12345",
        "I'm having trouble with my account login. Can you help?",
        "What are your support hours?",
    ]
    
    thread_id = None
    
    for i, user_message in enumerate(conversations, 1):
        print(f"\n{'─' * 80}")
        print(f"💬 Conversation {i}")
        print(f"{'─' * 80}")
        print(f"👤 User: {user_message}")
        
        result = await agent.chat(user_message, thread_id=thread_id)
        thread_id = result.get("thread_id")
        
        # Small delay between conversations
        await asyncio.sleep(1)
    
    print("\n" + "=" * 80)
    print("✅ Demo completed!")
    print("=" * 80)
    
    # Cleanup
    await state_manager.close()


if __name__ == "__main__":
    # Run the demo
    asyncio.run(main())
