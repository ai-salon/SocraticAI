import logging

from SocraticAI.generate.prompts import multi_convo_prompt
from SocraticAI.generate.utils import strip_preamble
from SocraticAI.llm_utils import chat_completion

logger = logging.getLogger(__name__)


def compare_conversation_insights(conversation_insights, model="claude-2"):
    logger.info(f"Comparing insights across conversations: {model}")
    try:
        # concatenate conversaion insight strings into one large string
        concat_text = ""
        for i, convo_insight in enumerate(conversation_insights):
            concat_text += f"```Conversation {i+1}```\n\n"
            concat_text += convo_insight

        p = multi_convo_prompt(text=concat_text)
        comparison = strip_preamble(chat_completion(p, model=model))
        logger.info(f"Generated {len(comparison)} insights")
        return comparison
    except Exception as e:
        logger.error(f"Error comparing conversations: {e}")
        raise
