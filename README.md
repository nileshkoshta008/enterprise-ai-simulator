# Enterprise AI Inbox Simulator (OpenEnv)

## 🚀 Project Overview
The **Enterprise AI Inbox Simulator** is a full-stack, state-of-the-art simulation of a real-world enterprise email triage system. This project adheres to the **OpenEnv** specifications, meaning it exposes an environment with `reset()`, `step()`, and `state()` functionality that models complex data systems.

The core motivation is simple: *Customer Support is hard*. Human operators often struggle to correctly interpret context, handle furious VIP customers, and meet Service Level Agreements (SLAs) under stress. This simulator spins up three powerful AI Agents working together to tackle an inbox simulation:
1. **Manager Agent**: Analyzes urgency and determines the Priority of an email based on SLAs and customer tiers.
2. **Worker Agent**: Consumes the Manager's context and determines exactly what topic Category the email belongs to, and what Action should be immediately taken.
3. **Critic Agent**: Audits the result, providing reflections for reinforcement learning loops.

## 🗂 Definitions
### Observation Space
Data visible to the agent:
- `email_subject`: (str)
- `email_body`: (str)
- `customer_tier`: (bronze | silver | gold)
- `sla_hours`: (int) Maximum acceptable response time.
- `time_elapsed_hours`: (float) Simulated SLA burn rate.

### Action Space
Output required from the agent:
- `priority`: (low | medium | high | critical)
- `category`: (billing | technical | spam | general)
- `decision`: (reply | ignore | escalate)

### Reward System
A strict deterministic grader ensures rewards strictly map between `0.0` and `1.0`. 
- **+0.3** for getting the correct category.
- **+0.3** for getting the correct priority.
- **+0.3** for getting the correct final decision.
- **Penalties**: Applying a poor priority to a critical task, or missing an SLA window due to elapsed time, will result in deep negative penalties up to `-0.5` points.

## 🎯 Tasks
Included in `openenv.yaml`:
- **Easy**: Basic spam detection and generic queries.
- **Medium**: Mixed intents including billing confusion and simple technical errors.
- **Hard**: Urgent, ambiguous, real-world scenarios featuring hacked accounts, VIP litigations, and strict SLA constraints.

## 💻 Setup Instructions

### 1. Local Run
To run this application locally without Docker, you will need an active OpenAI API Key for the multi-agent system.
```bash
# 1. Clone the project and set key (Windows PowerShell shown)
$env:OPENAI_API_KEY="sk-..."

# 2. Install Backend Dependencies
pip install -r requirements.txt

# 3. Scaffold and build the UI
cd frontend
npm install
npm run build
cd ..

# 4. Start the FastAPI Server via helper entrypoint
python run_backend.py

# Optionally use custom port:
$env:PORT=7860
python run_backend.py
```
Then navigate to `http://localhost:8000/` (or `http://localhost:7860/` if custom port set).

### 2. Docker Run (Hugging Face Spaces Ready)
This project is pre-configured to build into a multi-stage Docker container natively serving the React output over FastAPI port `7860`.
```bash
docker build -t openenv-simulator .
docker run -p 7860:7860 -e OPENAI_API_KEY="sk-..." openenv-simulator
```

## 🔌 API Usage
The `server.py` exposes RESTful hooks directly to the simulation state:
- `POST /reset`: Resets the underlying state and fetches observation 1.
- `GET /state`: See the active index, max queue, and current reward cache.
- `POST /step`: Manually submit an `Action` JSON to progress the simulation loop.
- `POST /auto-step`: Triggers the Agents to process the loop dynamically.
- `GET /leaderboard`: Lists the sorted highest performers.

## 📈 Baseline Scores
- Base `gpt-4o-mini`: `~0.90` on Easy, `~0.82` on Medium, `~0.65` on Hard.
