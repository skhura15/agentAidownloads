"""
Example: Customer Support Agent Usage

This script demonstrates how to create and use the CustomerSupportAgent.
"""

import asyncio
import logging
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.config_manager import ConfigManager
from core.logging_service import LoggingService
from core.state_manager import StateManager
from examples.customer_support_agent import CustomerSupportAgent


async def main():
    """Main example function"""
    
    # Configure logging
    LoggingService.configure(log_level=logging.INFO)
    logger = LoggingService.get_logger("example")
    
    logger.info("Starting Customer Support Agent example...")
    
    # Initialize components
    config_manager = ConfigManager(config_dir="configs")
    state_manager = StateManager(use_redis=False)
    
    # Create agent
    agent = CustomerSupportAgent(
        config_manager=config_manager,
        state_manager=state_manager
    )
    
    # Initialize agent
    await agent.initialize()
    
    logger.info(f"Agent initialized: {agent.agent_name}")
    logger.info(f"Capabilities: {', '.join(agent.capabilities)}")
    
    # Example conversations
    test_messages = [
        "Hi, I need help with my order #12345",
        "My application keeps crashing when I upload files",
        "What are the features of your premium plan?",
        "I want to cancel my subscription"
    ]
    
    for message in test_messages:
        logger.info(f"\n{'='*50}")
        logger.info(f"User: {message}")
        logger.info(f"{'='*50}")
        
        # Send message to agent
        response = await agent.execute(user_input=message, context={})
        
        logger.info(f"Agent: {response.content}")
        logger.info(f"Status: {response.status.value}")
        
        if response.tools_used:
            logger.info(f"Tools used: {', '.join(response.tools_used)}")
        
        if response.handoff_to:
            logger.info(f"Handoff to: {response.handoff_to}")
        
        # Small delay between messages
        await asyncio.sleep(1)
    
    # Get agent info
    agent_info = agent.get_info()
    logger.info(f"\nAgent metadata: {agent_info['metadata']}")
    
    # Cleanup
    await agent.cleanup()
    await state_manager.close()
    
    logger.info("\nExample completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())
