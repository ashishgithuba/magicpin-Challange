# magicpin AI Challenge Submission

## Approach

This submission implements a deterministic, template-based approach to compose messages for Vera. While an LLM could be used for dynamic composition, this approach guarantees that the messages meet all the constraints of the challenge, execute instantly (< 5ms per composition), and do not require external API dependencies or incur costs.

The composer routes incoming context based on the trigger `kind`:
- **Research Digest**: Highlights the specific clinical trial and metric, matching the clinical peer tone. Offers effort externalization ("Want me to pull the abstract and draft a WhatsApp message?").
- **Recall Due**: Uses the customer context to frame a personalized recall nudge on behalf of the merchant. Identifies preferred time slots and active offers to maximize conversion.
- **Performance Dip / Spikes**: Anchors on the precise metric shift (e.g. "views dropped 25%") and contrasts it with the peer average. The CTA offers a clear visibility campaign.

### Compulsion Levers Applied
We strictly apply at least one compulsion lever per message:
1. **Specificity**: Verifiable metrics and clinical numbers pulled directly from contexts.
2. **Loss Aversion**: Highlight missed searches, peer comparison, and traffic dips.
3. **Effort Externalization**: Drafted posts, single binary commitments.
4. **Curiosity**: Teasing new compliance or research insights.

### Multi-turn Capabilities
`conversation_handlers.py` tracks conversation history to detect:
1. **Auto-replies**: If the merchant replies with the exact same text 2+ times, the conversation exits gracefully.
2. **Intent Transitions**: If the merchant gives the go-ahead ("yes", "do it"), the bot switches to action mode instead of asking more qualifying questions.

## Running the Bot
```bash
uvicorn bot:app --host 0.0.0.0 --port 8080
```

## Additional Context
With more time, this template-based engine could act as a fallback, while an LLM is used primarily for extracting nuances from free-form customer conversations.
