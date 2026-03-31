import asyncio
from environment import InboxEnv
from agents import Agents
from analytics import AnalyticsTracker

async def main():
    print("Starting Training Loop over Easy, Medium, and Hard Tasks...")
    total_episodes = 0
    cumulative_reward = 0.0

    for tier in ["easy", "medium", "hard"]:
        print(f"\n[{tier.upper()} TASKS]")
        env = InboxEnv(task_tier=tier)
        obs = env.reset()
        done = False

        while not done:
            total_episodes += 1
            print(f"--- Episode {total_episodes} ---")
            print(f"Observation: {obs.email_subject} ({obs.customer_tier} tier - {obs.time_elapsed_hours}h elapsed, SLA {obs.sla_hours}h)")
            
            # Predict using Agents
            action = await Agents.run_pipeline(obs)
            print(f"Action Taken: Priority={action.priority}, Category={action.category}, Decision={action.decision}")
            
            # Step Env
            next_obs, reward, done, info = env.step(action)
            cumulative_reward += reward.score
            
            # Call Critic
            critic_feedback = await Agents.critic_agent(obs, action, reward.score)
            
            print(f"Reward Received: {reward.score}")
            print(f"Reward Details: {reward.details}")
            print(f"Critic Feedback: {critic_feedback}")

            # Logs & Analytics
            AnalyticsTracker.log_step(info["email_id"], action.model_dump(), reward.score)
            obs = next_obs
            
    # Calculate Average
    avg_score = round(cumulative_reward / total_episodes, 2)
    print(f"\n--- TRAINING SUMMARY ---")
    print(f"Total Episodes Processed: {total_episodes}")
    print(f"Total Cumulative Reward: {round(cumulative_reward, 2)}")
    print(f"Average Reward: {avg_score}")

    AnalyticsTracker.update_leaderboard("gpt-4o-mini-baseline", avg_score)
    print("Leaderboard Updated!")

if __name__ == "__main__":
    asyncio.run(main())
