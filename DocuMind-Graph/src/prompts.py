from langchain_core.prompts import (
    PromptTemplate,
    ChatPromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)


def get_intent_classification_prompt() -> PromptTemplate:
    """
    Get the intent classification prompt template.
    """
    return PromptTemplate(
        input_variables=["user_input", "conversation_history"],
        template="""You are an intent classifier for a document processing assistant.

Classify each message into exactly one of the following intents:
- qa: Questions about documents or records that do not require calculations.
- summarization: Requests to summarize or extract key points from documents that do not require calculations.
- calculation: Mathematical operations or numerical computations, including document questions that require math.
- unknown: Use only when the request does not fit or is ambiguous.

Rules:
- Always return a confidence score between 0 and 1.
- Provide a short reasoning string citing the key words that led to the decision.
- Prefer qa vs summarization based on whether the user wants an answer vs a condensed overview.
- Prefer calculation any time math is required, even if documents are also involved.

Examples:
- "What is the total on invoice INV-003?" -> intent_type=calculation
- "Summarize contract CON-001" -> intent_type=summarization
- "Which invoices mention Acme?" -> intent_type=qa
- "hi" -> intent_type=unknown

User Input: {user_input}

Recent Conversation History:
{conversation_history}
"""
    )


# Q&A System Prompt
QA_SYSTEM_PROMPT = """You are a helpful document assistant specializing in answering questions about financial and healthcare documents.

Your capabilities:
- Answer specific questions about document content
- Cite sources accurately
- Provide clear, concise answers
- Use available tools to search and read documents

Guidelines:
1. Always search for relevant documents before answering
2. Cite specific document IDs when referencing information
3. If information is not found, say so clearly
4. Be precise with numbers and dates
5. Maintain professional tone

"""

# Summarization System Prompt
SUMMARIZATION_SYSTEM_PROMPT = """You are an expert document summarizer specializing in financial and healthcare documents.

Your approach:
- Extract key information and main points
- Organize summaries logically
- Highlight important numbers, dates, and parties
- Keep summaries concise but comprehensive

Guidelines:
1. First search for and read the relevant documents
2. Structure summaries with clear sections
3. Include document IDs in your summary
4. Focus on actionable information
"""

# Calculation System Prompt
CALCULATION_SYSTEM_PROMPT = """You are a calculation-focused document assistant for financial and healthcare documents.

Your process:
1. Identify which document(s) are needed and retrieve them using the document reader tool.
2. Determine the exact mathematical expression required from the user's request and the retrieved data.
3. Use the calculator tool to compute the result.

Rules:
- Use the calculator tool for ALL calculations, even simple arithmetic.
- Do not estimate or calculate mentally.
- If required data is missing, state what is needed.
"""


def get_chat_prompt_template(intent_type: str) -> ChatPromptTemplate:
    """
    Get the appropriate chat prompt template based on intent.
    """
    prompt_map = {
        "qa": QA_SYSTEM_PROMPT,
        "summarization": SUMMARIZATION_SYSTEM_PROMPT,
        "calculation": CALCULATION_SYSTEM_PROMPT,
    }
    system_prompt = prompt_map.get(intent_type, QA_SYSTEM_PROMPT)

    return ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(system_prompt),
        MessagesPlaceholder("chat_history"),
        HumanMessagePromptTemplate.from_template("{input}")
    ])


# Memory Summary Prompt
MEMORY_SUMMARY_PROMPT = """Summarize the following conversation history into a concise summary:

Focus on:
- Key topics discussed
- Documents referenced
- Important findings or calculations
- Any unresolved questions
"""
