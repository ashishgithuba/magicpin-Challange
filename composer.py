import json
import random
from typing import Dict, Any, Optional, Tuple

def get_best_offer(merchant: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    offers = merchant.get("offers", [])
    active_offers = [o for o in offers if o.get("status") == "active"]
    if active_offers:
        return active_offers[0]
    return offers[0] if offers else None

def format_offer(offer: Dict[str, Any]) -> str:
    if not offer:
        return ""
    title = offer.get("title", "")
    # Check if price is already in title, e.g., "Dental Cleaning @ ₹299"
    if "₹" in title:
        return title
    
    val = offer.get("value", "")
    if val:
        if val.isdigit():
            return f"{title} @ ₹{val}"
        return f"{title} ({val})"
    return title

def get_language_preference(customer: Optional[Dict[str, Any]], merchant: Dict[str, Any]) -> str:
    if customer:
        identity = customer.get("identity", {})
        return identity.get("language_pref", "en")
    
    identity = merchant.get("identity", {})
    langs = identity.get("languages", ["en"])
    if "hi" in langs or "hi-en mix" in langs:
        return "hi-en mix"
    return langs[0] if langs else "en"

def compose_research_digest(category: Dict, merchant: Dict, trigger: Dict, customer: Optional[Dict]) -> Tuple[str, str, str, str]:
    payload = trigger.get("payload", {})
    top_item_id = payload.get("top_item_id")
    
    digest_items = category.get("digest", [])
    item = next((i for i in digest_items if i.get("id") == top_item_id), None)
    
    if not item and digest_items:
        item = digest_items[0]
        
    if not item:
        return "Hi! Some new research has been published for your category.", "open_ended", "research_digest"
        
    title = item.get("title", "")
    source = item.get("source", "")
    trial_n = item.get("trial_n", "")
    patient_segment = item.get("patient_segment", "")
    
    owner_name = merchant.get("identity", {}).get("owner_first_name") or merchant.get("identity", {}).get("name", "Merchant")
    
    lang = get_language_preference(None, merchant)
    is_hi = "hi" in lang.lower()
    
    body = f"Hi {owner_name}, a quick update from {source}."
    
    if patient_segment:
        if is_hi:
            body += f"\n\nMaine socha aapke '{patient_segment}' patients ke liye yeh relevant hoga: "
        else:
            body += f"\n\nThought this would be relevant for your '{patient_segment}' patients: "
            
    body += f"\"{title}\"."
    
    if trial_n:
        body += f" (Based on a {trial_n}-patient trial)."
        
    if is_hi:
        body += "\n\nKya main iska abstract pull karun aur ek WhatsApp draft banaun jo aap patients ke saath share kar sakein?"
    else:
        body += "\n\nWant me to pull the abstract and draft a WhatsApp message you can share with patients?"
        
    return body, "open_ended", "clinical peer tone, source citation, effort externalization"

def compose_recall_due(category: Dict, merchant: Dict, trigger: Dict, customer: Optional[Dict]) -> Tuple[str, str, str, str]:
    if not customer:
        return "Your customer is due for a visit.", "none", "fallback"
        
    cust_name = customer.get("identity", {}).get("name", "there")
    biz_name = merchant.get("identity", {}).get("name", "Our Clinic")
    
    lang = get_language_preference(customer, merchant)
    is_hi = "hi" in lang.lower()
    
    offer = get_best_offer(merchant)
    offer_text = format_offer(offer) if offer else ""
    
    prefs = customer.get("preferences", {})
    pref_slot = prefs.get("preferred_slots", "whenever")
    
    if is_hi:
        body = f"Hi {cust_name}, {biz_name} se bol rahe hain. Aapke pichle visit ko kaafi time ho gaya hai — aapka recall due hai."
        if offer_text:
            body += f"\n\nAbhi humare paas yeh available hai: {offer_text}."
        body += f"\n\nAapko normally '{pref_slot}' time pasand hai. Kya main aapke liye is week ek slot schedule karun?"
    else:
        body = f"Hi {cust_name}, this is {biz_name}. It's been a while since your last visit — your recall is due."
        if offer_text:
            body += f"\n\nWe currently have: {offer_text}."
        body += f"\n\nSince you prefer '{pref_slot}', would you like me to schedule a slot for you this week?"
        
    return body, "YES/STOP", "customer-facing recall, slot offer based on preference"

def compose_perf_dip(category: Dict, merchant: Dict, trigger: Dict, customer: Optional[Dict]) -> Tuple[str, str, str, str]:
    owner_name = merchant.get("identity", {}).get("owner_first_name") or merchant.get("identity", {}).get("name", "Merchant")
    perf = merchant.get("performance", {})
    delta = perf.get("delta_7d", {})
    
    calls_pct = delta.get("calls_pct", 0)
    views_pct = delta.get("views_pct", 0)
    
    dip_metric = "calls" if calls_pct < 0 and calls_pct < views_pct else "views"
    dip_val = abs(calls_pct) * 100 if dip_metric == "calls" else abs(views_pct) * 100
    
    lang = get_language_preference(None, merchant)
    is_hi = "hi" in lang.lower()
    
    peer_stats = category.get("peer_stats", {})
    peer_scope = peer_stats.get("scope", "your area")
    
    if is_hi:
        body = f"Hi {owner_name}, quick nudge: pichle 7 dino mein aapke {dip_metric} {dip_val:.0f}% drop hue hain."
        body += f"\n\nBaaki {peer_scope} ki businesses abhi normally chal rahi hain."
        body += "\n\nKya main ek quick visibility boost campaign run karun taki hum yeh traffic wapas la sakein?"
    else:
        body = f"Hi {owner_name}, quick nudge: your {dip_metric} dropped by {dip_val:.0f}% in the last 7 days."
        body += f"\n\nOther businesses in {peer_scope} are seeing normal traffic right now."
        body += "\n\nWant me to run a quick visibility boost campaign to win back that traffic?"
        
    return body, "YES/STOP", "loss aversion, peer comparison, effort externalization"

def compose(category: Dict, merchant: Dict, trigger: Dict, customer: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Main entry point for composing messages.
    Returns: body, cta, send_as, suppression_key, rationale
    """
    trigger_id = trigger.get("id", "")
    trigger_kind = trigger.get("kind", "")
    suppression_key = trigger.get("suppression_key", "")
    
    if not category: category = {}
    if not merchant: merchant = {}
    if not trigger: trigger = {}
    
    send_as = "merchant_on_behalf" if trigger.get("scope") == "customer" else "vera"
    
    # Route by trigger kind
    if trigger_kind == "research_digest":
        body, cta, rationale = compose_research_digest(category, merchant, trigger, customer)
    elif trigger_kind in ("recall_due", "customer_lapsed_soft", "chronic_refill_due"):
        body, cta, rationale = compose_recall_due(category, merchant, trigger, customer)
    elif trigger_kind in ("perf_dip", "dormant_with_vera"):
        body, cta, rationale = compose_perf_dip(category, merchant, trigger, customer)
    else:
        # Generic fallback that still tries to be specific
        owner_name = merchant.get("identity", {}).get("owner_first_name") or merchant.get("identity", {}).get("name", "Merchant")
        if trigger.get("scope") == "customer" and customer:
            owner_name = customer.get("identity", {}).get("name", "there")
            
        lang = get_language_preference(customer, merchant)
        is_hi = "hi" in lang.lower()
        
        if is_hi:
            body = f"Hi {owner_name}, maine observe kiya ki '{trigger_kind}' trigger hua hai. Kya aapko iske baare mein details chahiye?"
        else:
            body = f"Hi {owner_name}, I noticed a '{trigger_kind}' event for your account. Would you like me to handle this?"
        cta = "open_ended"
        rationale = "generic fallback handling"
        
    return {
        "body": body,
        "cta": cta,
        "send_as": send_as,
        "suppression_key": suppression_key,
        "rationale": rationale
    }
