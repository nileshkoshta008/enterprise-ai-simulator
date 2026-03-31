from models import Action, Email, Reward

def calculate_reward(action: Action, email: Email) -> Reward:
    """
    Deterministically grade the agent's action and return a Reward between 0.0 and 1.0.
    """
    score = 0.0
    details = {
        "priority_match": 0.0,
        "category_match": 0.0,
        "decision_match": 0.0
    }
    penalty = 0.0

    # 1. Evaluate Priority (0.3 max)
    if action.priority == email.true_priority:
        details["priority_match"] = 0.3
        score += 0.3
    
    # 2. Evaluate Category (0.3 max)
    if action.category == email.true_category:
        details["category_match"] = 0.3
        score += 0.3

    # 3. Evaluate Decision (0.3 max)
    if action.decision == email.true_action:
        details["decision_match"] = 0.3
        score += 0.3

    # 4. Check Penalties
    # Ignoring urgent emails
    if email.true_priority in ["high", "critical"] and action.decision == "ignore":
        penalty += 0.5
    
    # Wrong priority for critical cases
    if email.true_priority == "critical" and action.priority in ["low", "medium"]:
        penalty += 0.5

    # Progressive SLA violation penalty based on hours elapsed versus hours allowed
    if email.time_elapsed_hours >= email.sla_hours:
        violation_ratio = email.time_elapsed_hours / max(1, email.sla_hours)
        
        # Base penalty for breaching SLA
        base_sla_penalty = 0.2
        
        # Add escalating penalty if severely overdue
        if violation_ratio > 2.0:
            base_sla_penalty += 0.3  # Tripled penalty for massive breaches
        elif violation_ratio > 1.2:
            base_sla_penalty += 0.15
            
        # Forgive slightly if they escalated or correctly determined high priority
        if action.decision == "escalate" or action.priority in ["high", "critical"]:
            base_sla_penalty *= 0.5 # Halve the penalty
            
        penalty += base_sla_penalty

    # Provide a tiny base bump to bring max to 1.0
    base_bonus = 0.1
    score += base_bonus

    # Apply penalty and clip to [0.0, 1.0]
    final_score = score - penalty
    if final_score < 0.0:
        final_score = 0.0
    elif final_score > 1.0:
        final_score = 1.0

    return Reward(
        score=round(final_score, 2),
        details=details,
        penalty=round(penalty, 2)
    )
