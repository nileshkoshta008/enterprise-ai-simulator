from models import Email

EASY_TASKS = [
    Email(
        id="easy-1",
        subject="Win a free iPhone!!!",
        body="Click this link now. Immediate response required.",
        sender_tier="bronze",
        sla_hours=48,
        time_elapsed_hours=1.0,
        true_priority="low",
        true_category="spam",
        true_action="ignore",
    ),
    Email(
        id="easy-2",
        subject="Where is my invoice?",
        body="I need the receipt from last month's subscription payment.",
        sender_tier="silver",
        sla_hours=12,
        time_elapsed_hours=2.0,
        true_priority="medium",
        true_category="billing",
        true_action="reply",
    ),
    Email(
        id="easy-3",
        subject="Hello",
        body="Just saying hi and wanted to know your operating hours.",
        sender_tier="bronze",
        sla_hours=48,
        time_elapsed_hours=5.0,
        true_priority="low",
        true_category="general",
        true_action="reply",
    )
]

MEDIUM_TASKS = [
    Email(
        id="med-1",
        subject="App crashing when I tap the checkout button",
        body="I've been trying to pay you but the app crashes. Btw I see a weird charge from 2 days ago.",
        sender_tier="gold",
        sla_hours=2,
        time_elapsed_hours=0.5,
        true_priority="high",
        true_category="technical",
        true_action="escalate",
    ),
    Email(
        id="med-2",
        subject="Cancel my account",
        body="I cannot figure out how to do it. Will I get a refund?",
        sender_tier="silver",
        sla_hours=12,
        time_elapsed_hours=6.0,
        true_priority="medium",
        true_category="billing",
        true_action="reply",
    ),
    Email(
        id="med-3",
        subject="URGENT: Database migration failure",
        body="Our engineering team noticed your API is returning 500s during our integration testing.",
        sender_tier="silver",
        sla_hours=12,
        time_elapsed_hours=1.0,
        true_priority="high",
        true_category="technical",
        true_action="escalate",
    )
]

HARD_TASKS = [
    Email(
        id="hard-1",
        subject="MY ACCOUNT WAS HACKED - IMMEDIATE ACTION REQUIRED",
        body="Someone has logged in and changed my password. They are routing my funds. This is unacceptable. I am a VIP client!!!",
        sender_tier="gold",
        sla_hours=2,
        time_elapsed_hours=1.5, # Almost breaching SLA
        true_priority="critical",
        true_category="technical",
        true_action="escalate",
    ),
    Email(
        id="hard-2",
        subject="Legal action regarding billing dispute #99942",
        body="Per our council's advice, we demand an immediate refund for the downtime last week, otherwise we will litigate.",
        sender_tier="gold",
        sla_hours=2,
        time_elapsed_hours=2.5, # Breached SLA
        true_priority="critical",
        true_category="billing",
        true_action="escalate",
    ),
    Email(
        id="hard-3",
        subject="Enterprise RFP submission query",
        body="We are evaluating your system for a 10,000 seat license. Can your SLA guarantee 99.999% uptime?",
        sender_tier="bronze", # Wait, big deal but bronze tier
        sla_hours=48,
        time_elapsed_hours=24.0,
        true_priority="high",
        true_category="general",
        true_action="reply",
    )
]

ALL_TASKS = {
    "easy": EASY_TASKS,
    "medium": MEDIUM_TASKS,
    "hard": HARD_TASKS
}
