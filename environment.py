from typing import Tuple, Dict, Any, Optional
from models import Action, Observation, Reward, Email
from tasks import ALL_TASKS
from grader import calculate_reward
import random

class InboxEnv:
    def __init__(self, task_tier: str = "easy", current_index: int = 0, total_reward: float = 0.0):
        """
        Initialize the environment for a specific difficulty tier matching openenv.yaml.
        Supports passing state for stateless/serverless instances.
        """
        self.task_tier = task_tier
        self.emails = ALL_TASKS.get(self.task_tier, ALL_TASKS["easy"]).copy()
        self.current_email_index = current_index
        self.total_reward = total_reward

    def reset(self) -> Observation:
        """
        Resets the environment. Returns the initial observation with state.
        """
        self.current_email_index = 0
        self.total_reward = 0.0
        # No shuffle to ensure stateless consistency by index
        
        if len(self.emails) == 0:
            raise ValueError("No emails loaded for task tier.")
            
        return self._get_observation()

    def step(self, action: Action) -> Tuple[Observation, Reward, bool, Dict[str, Any]]:
        """
        Takes an Action model, calculates the Reward, and advances the simulation state.
        Returns: (observation, reward, done, info)
        """
        current_email = self.emails[self.current_email_index]
        
        # Calculate Reward using Deterministic Grader
        r = calculate_reward(action, current_email)
        self.total_reward += r.score
        
        info = {
            "email_id": current_email.id,
            "true_priority": current_email.true_priority,
            "true_category": current_email.true_category,
            "true_action": current_email.true_action,
            "reward_details": r.details,
            "penalty": r.penalty,
        }
        
        # Advance state
        self.current_email_index += 1
        done = self.current_email_index >= len(self.emails)
        
        next_obs = None if done else self._get_observation()
        
        return next_obs, r, done, info

    def state(self) -> Dict[str, Any]:
        """
        Returns the internal state of the environment.
        """
        return {
            "task_tier": self.task_tier,
            "current_email_index": self.current_email_index,
            "total_emails": len(self.emails),
            "total_reward": self.total_reward,
            "done": self.current_email_index >= len(self.emails)
        }

    def _get_observation(self) -> Observation:
        email = self.emails[self.current_email_index]
        return Observation(
            email_subject=email.subject,
            email_body=email.body,
            customer_tier=email.sender_tier,
            sla_hours=email.sla_hours,
            time_elapsed_hours=email.time_elapsed_hours
        )
