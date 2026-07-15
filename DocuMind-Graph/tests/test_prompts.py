from src import prompts


def test_intent_classification_prompt_formats_inputs():
    template = prompts.get_intent_classification_prompt()

    rendered = template.format(
        user_input="Summarize the invoice",
        conversation_history="User asked about invoices.",
    )

    assert "Summarize the invoice" in rendered
    assert "User asked about invoices." in rendered


def test_get_chat_prompt_template_includes_system_and_human_messages():
    template = prompts.get_chat_prompt_template("qa")

    messages = template.format_messages(input="Hello", chat_history=[])

    assert messages[0].type == "system"
    assert messages[-1].type == "human"


def test_memory_summary_prompt_defined():
    assert "conversation history" in prompts.MEMORY_SUMMARY_PROMPT.lower()
