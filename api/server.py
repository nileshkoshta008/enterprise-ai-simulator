import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from environment import InboxEnv
from models import Action, Observation, Reward, EnvState
from agents import Agents
from analytics import AnalyticsTracker

# Set up app
app = FastAPI(title="Enterprise AI Inbox Simulator API")

# Setup CORS for React Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global simulation state
env = None

@app.get("/api/ping")
async def ping():
    return {"status": "ok", "message": "Backend is running!"}

class TaskResetData(BaseModel):
    task_tier: str = "easy"

@app.post("/reset", response_model=Observation)
async def reset_env(data: TaskResetData):
    global env
    try:
        env = InboxEnv(task_tier=data.task_tier)
        obs = env.reset()
        obs.state = EnvState(task_tier=data.task_tier, current_email_index=0, total_reward=0.0)
        return obs
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

class StepRequest(BaseModel):
    action: Action
    state: EnvState

class StepResponse(BaseModel):
    observation: Observation | None
    reward: Reward
    done: bool
    info: dict
    state: EnvState

@app.post("/step", response_model=StepResponse)
async def step_env(req: StepRequest):
    global env
    try:
        # Re-initialize env from state for statelessness
        current_env = InboxEnv(
            task_tier=req.state.task_tier, 
            current_index=req.state.current_email_index,
            total_reward=req.state.total_reward
        )
        
        next_obs, reward, done, info = current_env.step(req.action)
        
        new_state = EnvState(
            task_tier=req.state.task_tier,
            current_email_index=current_env.current_email_index,
            total_reward=current_env.total_reward
        )
        if next_obs:
            next_obs.state = new_state

        return StepResponse(
            observation=next_obs,
            reward=reward,
            done=done,
            info=info,
            state=new_state
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/state")
async def get_state():
    global env
    if not env:
        return {"status": "uninitialized"}
    return env.state()

@app.get("/leaderboard")
async def get_leaderboard():
    """Retrieve leaderboard scores"""
    return AnalyticsTracker.get_leaderboard()

class AutoStepRequest(BaseModel):
    state: EnvState

@app.post("/auto-step", response_model=StepResponse)
async def auto_step(req: AutoStepRequest):
    """Triggers the agent pipeline to automatically make a decision for the current step."""
    try:
        # Re-initialize env from state
        current_env = InboxEnv(
            task_tier=req.state.task_tier, 
            current_index=req.state.current_email_index,
            total_reward=req.state.total_reward
        )
        
        # Get current observation for agent
        obs_data = current_env._get_observation()
        
        # Agent predicts
        action = await Agents.run_pipeline(obs_data)
        
        # Step env
        next_obs, reward, done, info = current_env.step(action)
        
        # New state
        new_state = EnvState(
            task_tier=req.state.task_tier,
            current_email_index=current_env.current_email_index,
            total_reward=current_env.total_reward
        )
        if next_obs:
            next_obs.state = new_state
        
        # Log (best effort)
        try:
            AnalyticsTracker.log_step(info["email_id"], action.model_dump(), reward.score, reasoning=action.reasoning)
        except Exception as e:
            print(f"Server logging failed: {e}")
            
        return StepResponse(
            observation=next_obs,
            reward=reward,
            done=done,
            info=info,
            state=new_state
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Entrypoint to serve static files (Once React is built)
from fastapi.staticfiles import StaticFiles
import os

if os.path.exists("frontend/dist"):
    app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="frontend")
