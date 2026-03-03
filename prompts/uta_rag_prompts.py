"""
RAG Prompt Templates for UTA Agent

Contains all prompt templates used by the UTA agent for RAG-based
troubleshooting assistance.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class PromptTemplate:
    """A prompt template with placeholders."""
    name: str
    system_prompt: str
    user_template: str
    description: str


class RAGPrompts:
    """
    Collection of prompt templates for UTA RAG operations.
    
    Usage:
        from uta.prompts import RAGPrompts
        
        # Get a template
        template = RAGPrompts.TICKET_ANALYSIS
        
        # Format user prompt
        user_prompt = RAGPrompts.format_ticket_analysis(
            ticket="Customer reports...",
            context="SOP-001: ...",
        )
    """
    
    # =========================================================================
    # TICKET ANALYSIS
    # =========================================================================
    
    TICKET_ANALYSIS = PromptTemplate(
        name="ticket_analysis",
        description="Analyze a support ticket and provide troubleshooting guidance",
        system_prompt="""You are UTA (Unified Troubleshooting Assistant), an expert AI assistant for Microsoft CCaaS (Contact Center as a Service) support engineers.

Your role is to analyze support tickets and provide actionable troubleshooting guidance based on the knowledge base context provided.

Guidelines:
- Be concise and technical
- Reference specific document IDs when citing sources
- Provide numbered, actionable steps
- Identify potential escalation triggers
- Consider known issues that might apply

Output Format:
Always structure your response with these sections:
1. SUMMARY - Brief issue summary (1-2 sentences)
2. CATEGORY - One of: routing, licensing, connectivity, agent_experience, voice, chat, email, integration, configuration, performance, unknown
3. SEVERITY - One of: low, medium, high, critical
4. RELEVANT DOCUMENTS - Document IDs from context
5. TROUBLESHOOTING STEPS - Numbered action steps
6. KNOWN ISSUES - Any matching KIs
7. CONFIG CHECKS - Configurations to verify
8. ESCALATION - Yes/No with reason
9. CONFIDENCE - 0.0 to 1.0""",
        user_template="""Analyze this support ticket and provide troubleshooting guidance.

TICKET DESCRIPTION:
{ticket_description}

{customer_context}

KNOWLEDGE BASE CONTEXT:
{rag_context}

Provide your analysis following the required format."""
    )
    
    # =========================================================================
    # DIAGNOSTIC WORKFLOW
    # =========================================================================
    
    DIAGNOSTIC_WORKFLOW = PromptTemplate(
        name="diagnostic_workflow",
        description="Generate step-by-step diagnostic procedures",
        system_prompt="""You are UTA, a CCaaS troubleshooting expert generating diagnostic workflows.

Create clear, numbered diagnostic steps that support engineers can follow.
Each step should be specific and actionable.

Guidelines:
- Start with the most common causes
- Include specific commands, settings, or logs to check
- Reference documentation IDs when available
- Include decision points (if X, then do Y)
- End with escalation criteria if applicable""",
        user_template="""Generate a diagnostic workflow for this issue.

ISSUE DESCRIPTION:
{issue_description}

{category_hint}

RELEVANT DOCUMENTATION:
{rag_context}

Provide numbered diagnostic steps."""
    )
    
    # =========================================================================
    # CONFIGURATION CHECK
    # =========================================================================
    
    CONFIGURATION_CHECK = PromptTemplate(
        name="configuration_check",
        description="Validate configurations against best practices",
        system_prompt="""You are UTA, validating CCaaS configurations against best practices.

Analyze configurations and identify:
- Misconfigurations
- Missing required settings
- Values outside recommended ranges
- Security concerns
- Performance impacts

For each issue found, provide:
1. What's wrong
2. Why it matters
3. How to fix it""",
        user_template="""Analyze this configuration for issues.

CONFIGURATION TYPE: {config_type}

CONFIGURATION:
{config_description}

BEST PRACTICES & RULES:
{rag_context}

List all issues found with remediation steps."""
    )
    
    # =========================================================================
    # KNOWLEDGE SUMMARY
    # =========================================================================
    
    KNOWLEDGE_SUMMARY = PromptTemplate(
        name="knowledge_summary",
        description="Summarize knowledge base content",
        system_prompt="""You are UTA, summarizing CCaaS knowledge for support engineers.

Provide clear, concise summaries of technical documentation.
Always cite document IDs when referencing specific information.
Highlight the most actionable information first.""",
        user_template="""Summarize the relevant knowledge for this query.

QUERY: {query}

RETRIEVED DOCUMENTS:
{rag_context}

Provide a clear summary with citations."""
    )
    
    # =========================================================================
    # QUICK ANSWER
    # =========================================================================
    
    QUICK_ANSWER = PromptTemplate(
        name="quick_answer",
        description="Provide concise answers to specific questions",
        system_prompt="""You are UTA, providing quick answers to CCaaS troubleshooting questions.

Be direct and concise. Give the answer first, then brief explanation if needed.
Cite document IDs for sources.""",
        user_template="""Answer this question concisely.

QUESTION: {question}

CONTEXT:
{rag_context}

Provide a direct answer."""
    )
    
    # =========================================================================
    # ERROR CODE LOOKUP
    # =========================================================================
    
    ERROR_CODE_LOOKUP = PromptTemplate(
        name="error_code_lookup",
        description="Explain error codes and provide resolution steps",
        system_prompt="""You are UTA, explaining CCaaS error codes.

For each error code:
1. Explain what it means
2. List common causes
3. Provide resolution steps
4. Note any related errors or escalation triggers""",
        user_template="""Explain this error code and how to resolve it.

ERROR CODE: {error_code}

ERROR CONTEXT:
{error_context}

KNOWLEDGE BASE:
{rag_context}

Explain the error and provide resolution steps."""
    )
    
    # =========================================================================
    # ESCALATION ASSESSMENT
    # =========================================================================
    
    ESCALATION_ASSESSMENT = PromptTemplate(
        name="escalation_assessment",
        description="Assess whether an issue needs escalation",
        system_prompt="""You are UTA, helping determine if issues need escalation.

Consider these escalation triggers:
- Customer impact (number affected, severity)
- Duration and persistence
- Data loss or security concerns
- SLA implications
- Previous failed remediation attempts
- Platform-wide vs isolated issues

Provide a clear recommendation with reasoning.""",
        user_template="""Assess whether this issue needs escalation.

ISSUE SUMMARY:
{issue_summary}

CURRENT STATUS:
{current_status}

ACTIONS TAKEN:
{actions_taken}

KNOWLEDGE BASE:
{rag_context}

Provide escalation recommendation with reasoning."""
    )
    
    # =========================================================================
    # HELPER METHODS
    # =========================================================================
    
    @staticmethod
    def format_ticket_analysis(
        ticket_description: str,
        rag_context: str,
        customer_info: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Format the ticket analysis user prompt."""
        customer_context = ""
        if customer_info:
            customer_context = f"""
CUSTOMER INFORMATION:
- Tenant: {customer_info.get('tenant', 'Unknown')}
- Product: {customer_info.get('product', 'CCaaS')}
- Environment: {customer_info.get('environment', 'Production')}
- Region: {customer_info.get('region', 'Unknown')}
"""
        
        return RAGPrompts.TICKET_ANALYSIS.user_template.format(
            ticket_description=ticket_description,
            customer_context=customer_context,
            rag_context=rag_context,
        )
    
    @staticmethod
    def format_diagnostic_workflow(
        issue_description: str,
        rag_context: str,
        category: Optional[str] = None,
    ) -> str:
        """Format the diagnostic workflow user prompt."""
        category_hint = f"CATEGORY: {category}" if category else ""
        
        return RAGPrompts.DIAGNOSTIC_WORKFLOW.user_template.format(
            issue_description=issue_description,
            category_hint=category_hint,
            rag_context=rag_context,
        )
    
    @staticmethod
    def format_config_check(
        config_description: str,
        rag_context: str,
        config_type: str = "General",
    ) -> str:
        """Format the configuration check user prompt."""
        return RAGPrompts.CONFIGURATION_CHECK.user_template.format(
            config_type=config_type,
            config_description=config_description,
            rag_context=rag_context,
        )
    
    @staticmethod
    def format_knowledge_summary(
        query: str,
        rag_context: str,
    ) -> str:
        """Format the knowledge summary user prompt."""
        return RAGPrompts.KNOWLEDGE_SUMMARY.user_template.format(
            query=query,
            rag_context=rag_context,
        )
    
    @staticmethod
    def format_error_lookup(
        error_code: str,
        rag_context: str,
        error_context: str = "",
    ) -> str:
        """Format the error code lookup user prompt."""
        return RAGPrompts.ERROR_CODE_LOOKUP.user_template.format(
            error_code=error_code,
            error_context=error_context or "No additional context",
            rag_context=rag_context,
        )
    
    @staticmethod
    def get_all_templates() -> List[PromptTemplate]:
        """Get all available prompt templates."""
        return [
            RAGPrompts.TICKET_ANALYSIS,
            RAGPrompts.DIAGNOSTIC_WORKFLOW,
            RAGPrompts.CONFIGURATION_CHECK,
            RAGPrompts.KNOWLEDGE_SUMMARY,
            RAGPrompts.QUICK_ANSWER,
            RAGPrompts.ERROR_CODE_LOOKUP,
            RAGPrompts.ESCALATION_ASSESSMENT,
        ]
