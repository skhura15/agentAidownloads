"""
Common Tools for Agents

This module contains commonly used tools that agents can leverage.
"""

import asyncio
from typing import Any, Dict, List, Optional
import json
import re


async def search_knowledge_base(
    query: str,
    knowledge_base_id: str,
    top_k: int = 5
) -> List[Dict[str, Any]]:
    """
    Search a knowledge base for relevant information.
    
    Args:
        query: Search query
        knowledge_base_id: Knowledge base identifier
        top_k: Number of results to return
        
    Returns:
        List of search results
    """
    # This is a placeholder implementation
    # In production, this would integrate with Azure AI Search or similar
    await asyncio.sleep(0.5)  # Simulate API call
    
    return [
        {
            "id": "doc1",
            "title": "Sample Document",
            "content": f"Relevant information about {query}",
            "score": 0.95
        }
    ]


async def create_ticket(
    title: str,
    description: str,
    priority: str = "medium",
    category: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a support ticket.
    
    Args:
        title: Ticket title
        description: Ticket description
        priority: Priority level (low, medium, high, critical)
        category: Ticket category
        
    Returns:
        Created ticket information
    """
    # This is a placeholder implementation
    # In production, this would integrate with your ticketing system
    await asyncio.sleep(0.3)
    
    ticket_id = f"TICKET-{hash(title) % 10000:04d}"
    
    return {
        "ticket_id": ticket_id,
        "title": title,
        "description": description,
        "priority": priority,
        "category": category,
        "status": "open",
        "created_at": "2026-01-05T10:00:00Z"
    }


async def send_email(
    to: str,
    subject: str,
    body: str,
    cc: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Send an email.
    
    Args:
        to: Recipient email address
        subject: Email subject
        body: Email body
        cc: CC recipients
        
    Returns:
        Email sending result
    """
    # This is a placeholder implementation
    await asyncio.sleep(0.2)
    
    return {
        "status": "sent",
        "message_id": f"msg-{hash(subject) % 10000:04d}",
        "to": to,
        "subject": subject
    }


def extract_entities(text: str) -> Dict[str, List[str]]:
    """
    Extract entities from text.
    
    Args:
        text: Input text
        
    Returns:
        Dictionary of entity types and their values
    """
    # Simple pattern-based extraction (replace with Azure AI Language in production)
    entities = {
        "emails": re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text),
        "phone_numbers": re.findall(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', text),
        "urls": re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
    }
    
    return entities


def format_response(
    content: str,
    response_type: str = "text"
) -> Dict[str, Any]:
    """
    Format response for UI display.
    
    Args:
        content: Response content
        response_type: Type of response (text, markdown, json)
        
    Returns:
        Formatted response
    """
    formatted = {
        "content": content,
        "type": response_type,
        "metadata": {}
    }
    
    if response_type == "json":
        try:
            formatted["parsed"] = json.loads(content)
        except:
            formatted["type"] = "text"
    
    return formatted


async def get_weather(location: str) -> Dict[str, Any]:
    """
    Get weather information for a location.
    
    Args:
        location: Location name
        
    Returns:
        Weather information
    """
    # Placeholder implementation
    await asyncio.sleep(0.3)
    
    return {
        "location": location,
        "temperature": 72,
        "conditions": "Partly Cloudy",
        "humidity": 65,
        "wind_speed": 8
    }


def calculate(expression: str) -> float:
    """
    Safely evaluate a mathematical expression.
    
    Args:
        expression: Mathematical expression
        
    Returns:
        Result of the calculation
    """
    # Simple safe evaluation (use more sophisticated parsing in production)
    try:
        # Remove any non-math characters
        safe_expr = re.sub(r'[^0-9+\-*/().\s]', '', expression)
        result = eval(safe_expr, {"__builtins__": {}}, {})
        return float(result)
    except Exception as e:
        raise ValueError(f"Invalid expression: {str(e)}")
