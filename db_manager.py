# Backend Hardening Checklist

- [ ] Update `models.py` (Add `reasoning` and `feedback` fields)
- [ ] Update `agents.py`
    - [ ] Create `_clean_json` helper
    - [ ] Add reasoning to `Manager` agent
    - [ ] Add reasoning to `Worker` agent
    - [ ] Add reasoning to `Critic` agent
- [ ] Update `analytics.py` (Record reasoning in logs)
- [ ] Update `server.py` (Expose reasoning in API responses)
- [ ] Verify with `python train.py`
