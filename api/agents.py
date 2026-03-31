import json
import os
from openai import AsyncOpenAI
from dotenv import load_dotenv
from models import Observation, Action

# Load .env file automatically
load_dotenv()

api_key = os.environ.get("OPENAI_API_KEY", "")
if not api_key:
    print("WARNING: OPENAI_API_KEY not found in environment!")
else:
    print(f"DEBUG: OPENAI_API_KEY found (length: {len(api_key)})")

client = AsyncOpenAI(api_key=api_key)

def clean_json_response(text: str) -> str:
    """Helper to strip markdown backticks and extract JSON content."""
    text = text.strip()
    if text.startswith("```"):
        # Remove starting ```json or ```
        if text.startswith("```json"):
            text = text[7:]
        else:
            text = text[3:]
        # Remove ending ```
        if text.endswith("```"):
            text = text[:-3]
    return text.strip()

class Agents:
    """
    Multi-Agent System for Enterprise AI Inbox Simulator.
    Three agents dynamically classify observations into actions.
    """
    
    @staticmethod
    async def manager_agent(obs: Observation) -> str:
        """
        Manager Agent decides the Priority (low, medium, high, critical)
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
        Respond ONLY with a valid JSON format like: {{"priority": "value"}}
        """
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a triage manager. You MUST respond with JSON. Include a 'reasoning' field explaining your choice."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0
        )
        content = clean_json_response(response.choices[0].message.content)
        try:
            data = json.loads(content)
            return data.get("priority", "medium").lower(), data.get("reasoning", "No reasoning provided.")
        except:
            return "medium", "Failed to parse manager response."

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
        
        Respond ONLY with a valid JSON format like: {{"category": "value", "decision": "value"}}
        """
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a support agent. You MUST respond with JSON. Include a 'reasoning' field explaining your choice."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0
        )
        content = clean_json_response(response.choices[0].message.content)
        try:
            data = json.loads(content)
            return {
                "category": data.get("category", "general").lower(),
                "decision": data.get("decision", "reply").lower(),
                "reasoning": data.get("reasoning", "No reasoning provided.")
            }
        except:
            return {"category": "general", "decision": "reply", "reasoning": "Failed to parse worker response."}

    @staticmethod
    async def critic_agent(obs: Observation, action: Action, initial_reward: float) -> str:
        """
        Critic Agent reviews the performance.
        Useful for providing feedback/reflections on the training loop or logs.
        """
        prompt = f"""
        You are a Senior Systems Auditor analyzing enterprise triaging decisions.
        Review the execution of an automated Support Workflow based on exact SLA margins and tiered risk scoring.
        
        Observation Space: {obs.model_dump()}
        Agent Action Space: {action.model_dump()}
        Simulated Environment Score (0.0 to 1.0): {initial_reward}
        
        Produce a concise 2-3 sentence reflection analyzing the tradeoffs made. Explicitly mention if their priority label matched the SLA elapsed time, if penalties were applied effectively, and what they could change to approach a 1.0 score.
        Do NOT output JSON. Output raw, unstructured string text. Wait, limit output to a maximum of 3 sentences.
        """
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a highly analytical and unforgiving enterprise performance auditor."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content.strip()

    @classmethod
    async def run_pipeline(cls, obs: Observation) -> Action:
        """
        Coordinates the multi-agent pipeline and returns a structured Action model.
        """
        # Manager runs first
        priority, manager_reasoning = await cls.manager_agent(obs)
        
        # Worker uses priority context
        worker_output = await cls.worker_agent(obs, priority)
        
        # Combine into Action structure with reasoning trace
        return Action(
            priority=priority,
            category=worker_output["category"],
            decision=worker_output["decision"],
            reasoning=f"Manager: {manager_reasoning} | Worker: {worker_output.get('reasoning')}"
        )
