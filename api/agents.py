import json
import os
from typing import Optional, Literal, cast
from openai import AsyncOpenAI
from dotenv import load_dotenv
from .models import Observation, Action

# Load .env file automatically
load_dotenv()

api_key = os.environ.get("OPENAI_API_KEY", "")
use_openai = True
if not api_key or api_key.startswith("AIza"):
    # Invalid Google-style key or missing key
    use_openai = False
    print("WARNING: OPENAI_API_KEY not provided or invalid; falling back to local stub agents for offline testing.")

client: Optional[AsyncOpenAI] = None
if use_openai:
    try:
        client = AsyncOpenAI(api_key=api_key)
    except Exception as e:
        use_openai = False
        client = None
        print(f"WARNING: could not initialize OpenAI client ({e}); using stub agents.")


def _local_priority(obs: Observation) -> tuple[Literal["low", "medium", "high", "critical"], str]:
    # Simple heuristic for offline mode
    elapsed = obs.time_elapsed_hours
    sla = obs.sla_hours
    ratio = elapsed / sla if sla > 0 else 1.0
    if ratio > 1.0:
        return "critical", "SLA exceeded, assign critical priority."
    if ratio > 0.75:
        return "high", "SLA burning, assign high priority."
    if obs.customer_tier == "gold":
        return "high", "Gold customer premium priority."
    if "billing" in obs.email_body.lower() or "billing" in obs.email_subject.lower():
        return "medium", "Billing query; medium priority."
    return "low", "Default low priority."


def _local_worker(obs: Observation, priority: str) -> dict:
    if "spam" in obs.email_body.lower() or "unsubscribe" in obs.email_body.lower():
        return {"category": "spam", "decision": "ignore", "reasoning": "Detected spam signals."}
    if "error" in obs.email_body.lower() or "issue" in obs.email_body.lower():
        return {"category": "technical", "decision": "reply", "reasoning": "Technical issue detected."}
    if "invoice" in obs.email_body.lower() or "charge" in obs.email_body.lower():
        return {"category": "billing", "decision": "reply", "reasoning": "Billing-related request."}
    return {"category": "general", "decision": "reply", "reasoning": "Default general response."}


client = None
if use_openai:
    client = AsyncOpenAI(api_key=api_key)


def clean_json_response(text: str) -> str:
    """Strip markdown code fences and normalize JSON text."""
    t = text.strip()
    if t.startswith("```") and t.endswith("```"):
        t = t[3:-3].strip()
    if t.startswith("json"):
        t = t[4:].strip()
    return t


def _extract_content_from_choice(choice):
    if hasattr(choice, "message"):
        m = choice.message
        if isinstance(m, dict):
            return m.get("content", "")
        return getattr(m, "content", "")
    return ""


class Agents:
    """
    Multi-Agent System for Enterprise AI Inbox Simulator.
    Three agents dynamically classify observations into actions.
    """
    
    @staticmethod
    async def manager_agent(obs: Observation) -> tuple[Literal["low", "medium", "high", "critical"], str]:
        """
        Manager Agent decides the Priority (low, medium, high, critical) and returns priority plus reasoning.
        """
        prompt = f"""
        You are an elite Enterprise Triage Manager.
        Analyze this incoming email and the customer constraints.
        
        Email Subject: {obs.email_subject}
        Email Body: {obs.email_body}
        Customer Tier: {obs.customer_tier}
        SLA Target: {obs.sla_hours} hours
        Time Elapsed: {obs.time_elapsed_hours} hours
        
        Determine the Priority from exactly one of these values: ["low", "medium", "high", "critical"]
        Respond ONLY with a valid JSON format like: {{"priority": "value", "reasoning": "..."}}
        """
        if not use_openai or client is None:
            return _local_priority(obs)

        try:
            current_client = client
            assert current_client is not None
            response = await current_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You output JSON directly without markdown wrappers."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0
            )
            raw_content = _extract_content_from_choice(response.choices[0]).strip()
            data = json.loads(clean_json_response(raw_content))
            priority = data.get("priority", "medium").lower()
            if priority not in ("low", "medium", "high", "critical"):
                priority = "medium"
            return cast(Literal["low", "medium", "high", "critical"], priority), data.get("reasoning", "No reasoning provided.")
        except Exception:
            return _local_priority(obs)
    @staticmethod
    async def worker_agent(obs: Observation, priority: str) -> dict:
        """
        Worker Agent decides Category and Action based on Priority from Manager.
        """
        prompt = f"""
        You are a highly capable Support Engineer.
        The Manager has assessed the Priority of this email as: {priority.upper()}.
        
        Email Subject: {obs.email_subject}
        Email Body: {obs.email_body}
        Customer Tier: {obs.customer_tier}
        
        Select exactly ONE Category from: ["billing", "technical", "spam", "general"]
        Select exactly ONE Action from: ["reply", "ignore", "escalate"]
        
        Respond ONLY with a valid JSON format like: {{"category": "value", "decision": "value", "reasoning": "..."}}
        """
        if not use_openai or client is None:
            return _local_worker(obs, priority)

        try:
            current_client = client
            assert current_client is not None
            response = await current_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You output JSON directly without markdown wrappers."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0
            )
            raw_content = _extract_content_from_choice(response.choices[0]).strip()
            data = json.loads(clean_json_response(raw_content))
            return {
                "category": data.get("category", "general").lower(),
                "decision": data.get("decision", "reply").lower(),
                "reasoning": data.get("reasoning", "No reasoning provided.")
            }
        except Exception:
            return _local_worker(obs, priority)

    @staticmethod
    async def critic_agent(obs: Observation, action: Action, initial_reward: float) -> str:
        """
        Critic Agent reviews the performance.
        Useful for providing feedback/reflections on the training loop or logs.
        """
        if not use_openai or client is None:
            return "Stub critic: action evaluated with local heuristic for offline mode."

        prompt = f"""
        You are a Senior Systems Auditor analyzing enterprise triaging decisions.
        Review the execution of an automated Support Workflow based on exact SLA margins and tiered risk scoring.
        
        Observation Space: {obs.model_dump()}
        Agent Action Space: {action.model_dump()}
        Simulated Environment Score (0.0 to 1.0): {initial_reward}
        
        Produce a concise 2-3 sentence reflection analyzing the tradeoffs made. Explicitly mention if their priority label matched the SLA elapsed time, if penalties were applied effectively, and what they could change to approach a 1.0 score.
        Do NOT output JSON. Output raw, unstructured string text. Wait, limit output to a maximum of 3 sentences.
        """
        try:
            current_client = client
            assert current_client is not None
            response = await current_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a highly analytical and unforgiving enterprise performance auditor."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            return _extract_content_from_choice(response.choices[0]).strip()
        except Exception:
            return "Fallback critic: OpenAI unavailable; no detailed insight available."

    @classmethod
    async def run_pipeline(cls, obs: Observation) -> Action:
        """
        Coordinates the multi-agent pipeline and returns a structured Action model.
        """
        # Manager runs first
        priority, manager_reasoning = await cls.manager_agent(obs)

        # Worker uses priority context
        worker_output = await cls.worker_agent(obs, priority)

        # Combine into OpenEnv Action structure
        return Action(
            priority=priority,
            category=worker_output["category"],
            decision=worker_output["decision"],
            reasoning=f"Manager: {manager_reasoning} | Worker: {worker_output.get('reasoning', 'No worker reasoning')}"
        )
