# Ara realtime voice

`livekit_agent.py` is the headless, continuous voice doorway to the existing
Conductor. OpenAI Realtime handles speech, turn detection, interruptions, and
spoken output. The `consult_conductor` tool sends substantive requests to the
existing Conductor API so memory, Firecrawl, and provider routing stay in one
place.

## Required environment

- `LIVEKIT_URL`
- `LIVEKIT_API_KEY`
- `LIVEKIT_API_SECRET`
- `OPENAI_API_KEY`
- `CONDUCTOR_API_URL` (defaults to the current Render service)

Optional:

- `LIVEKIT_AGENT_NAME` (defaults to `ara-conductor`)
- `OPENAI_REALTIME_MODEL` (defaults to `gpt-realtime`)
- `OPENAI_REALTIME_VOICE` (defaults to `marin`)
- `CONDUCTOR_AUTH_TOKEN` when the Conductor endpoint is protected

## Run and deploy

```shell
uv run livekit_agent.py console
uv run livekit_agent.py dev
lk agent create
```

The existing web application remains available as the no-LiveKit fallback. Its
hands-free mode requires one initial browser tap to grant microphone access and
then automatically detects silence and restarts listening after each response.
