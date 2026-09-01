from typing import Dict, Any, List

def check_auto_reply(history: List[Dict[str, Any]], new_message: str) -> bool:
    """Detect if the new message is likely an auto-reply by checking if it matches exactly with recent messages."""
    if not history:
        return False
        
    merchant_msgs = [msg["msg"] for msg in history if msg.get("from") == "merchant"]
    
    # If the exact same message was sent 2+ times before, it's an auto-reply
    count = merchant_msgs.count(new_message)
    return count >= 2

def check_intent_transition(new_message: str) -> bool:
    """Detect if the user is giving a clear go-ahead"""
    msg_lower = new_message.lower()
    intent_signals = ["yes", "ok", "go ahead", "do it", "sure", "haan", "theek hai"]
    return any(signal in msg_lower for signal in intent_signals)

def respond(history: List[Dict[str, Any]], merchant_message: str) -> Dict[str, Any]:
    """
    Given the conversation so far + the merchant's latest message, produce the reply.
    """
    if check_auto_reply(history, merchant_message):
        return {
            "action": "end",
            "rationale": "Detected auto-reply. Gracefully exiting to avoid spam."
        }
        
    if check_intent_transition(merchant_message):
        return {
            "action": "send",
            "body": "Got it! I'm starting on that right now. I'll ping you once it's complete.",
            "cta": "none",
            "rationale": "Merchant gave go-ahead, transitioning to action mode."
        }
        
    msg_lower = merchant_message.lower()
    if "stop" in msg_lower or "not interested" in msg_lower or "no" in msg_lower:
        return {
            "action": "end",
            "rationale": "Merchant explicitly declined or opted out."
        }
        
    if "later" in msg_lower or "busy" in msg_lower or "time" in msg_lower:
        return {
            "action": "wait",
            "wait_seconds": 3600,
            "rationale": "Merchant asked for time, waiting an hour."
        }
        
    # Default fallback
    return {
        "action": "send",
        "body": "Could you clarify that? I want to make sure I get it right for your business.",
        "cta": "open_ended",
        "rationale": "Clarification request for unhandled response."
    }
