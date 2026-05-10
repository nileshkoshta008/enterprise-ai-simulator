import asyncio
from api.agents import Agents
from api.models import Observation
obs=Observation(email_subject='Test', email_body='Hello', customer_tier='gold', sla_hours=24, time_elapsed_hours=1.0)
async def run():
    try:
        action=await Agents.run_pipeline(obs)
        print('Action:', action)
    except Exception as e:
        import traceback; traceback.print_exc()

asyncio.run(run())
