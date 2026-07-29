# Cramer Consulting Group — AI Stack Business Plan
## Durable copy (keep this file even if AI chats are wiped)

**Repo path:** `Documents/GitHub/Super-conductor-agent-/docs/CCG_BUSINESS_PLAN.md`
**Also keep a copy:** OneDrive / Notes / print if you want offline
**Owner:** CCG (2-person operation)
**Products in play:** TypingMind + Mem0, Super-conductor, LiveKit ARA, phone DIDs, Grok/xAI, OpenRouter, Twilio

This document is the single source of truth for **what we are building**, **why**, **what to keep**, and **the exact order of work**. No deadlines. Go as slow as you need. Do not give up.

---

# 1. Business purpose

## 1.1 Two tracks (always)

| Track | Name | Goal |
|-------|------|------|
| **Track A** | **Make money now** | Use the stack for real client work, demos, and billable delivery |
| **Track B** | **Sell the system later** | Package Super-conductor + memory + optional voice as a product others can buy |

Both tracks share one **kernel**. Do not build a new system for every idea.

## 1.2 Kernel (the product core)

```
TypingMind (human UI)  +  Mem0 (live memory)  +  Grok 4.5 (brain)
         +
Super-conductor (backend, ingest, API, phone bridge)
         +
LiveKit ARA (optional voice face of the product)
```

Everything else (Azure experiments, extra numbers, extra clouds) is optional until Track A is solid.

## 1.3 Success definition (pick the lowest level that still feels real)

| Level | What “working” means |
|-------|----------------------|
| **Level 1** | TypingMind answers with **Grok** + **Mem0 remembers** one fact |
| **Level 2** | Level 1 + Super-conductor `.env` uses the **same Mem0 user id** |
| **Level 3** | Level 2 + phone path ready (`/ready/telephony` true) + one test call works **or** paid DIDs consciously parked |

**Minimum win:** Level 1.
**Stretch:** Level 3.
Never require Level 3 to feel successful.

## 1.4 Team shape

- **Two people.** Cannot maintain every cloud at full burn.
- Prefer **one brain**, **one memory**, **one paid phone max**.
- Free **T-Mobile throw-in number on iPhone 16** is for **you** to call and test — not waste.

---

# 2. What each piece is (so nothing is mysterious)

| # | Piece | Job | Not its job |
|---|--------|-----|-------------|
| 2.1 | **TypingMind** | Daily chat UI; multi-model; Mem0 plugin | Not the phone switch |
| 2.2 | **Mem0** | Long-term memory shared across chat (and later phone) | Not a phone company |
| 2.3 | **Grok / xAI** | Main model (prefer **grok-4.5**) | X app voice ≠ your 619 numbers |
| 2.4 | **OpenRouter** | Optional router for many models with one key | Not required if direct xAI works |
| 2.5 | **Super-conductor** | Code: API, RAG ingest, Twilio→LiveKit bridge, ARA worker | Not SuperGrok.com |
| 2.6 | **grok_processor.py** | Import **Grok export ZIP** into archive memory | Does **not** answer the phone |
| 2.7 | **LiveKit + ARA** | Voice rooms + agent named **`ara`** | Useless without secrets + running worker |
| 2.8 | **Twilio 619-583-3329** | Optional DID + webhook bridge | Idle rent if unused |
| 2.9 | **LiveKit 619-639-4611** | ARA product DID (if kept) | Idle rent if worker never runs |
| 2.10 | **T-Mobile free line** | Your personal/test phone | Keep always |
| 2.11 | **Grok Build / coding agent** | Builds and fixes code on the Mac | Does not replace TypingMind chat |
| 2.12 | **X / SuperGrok app voice** | xAI consumer product | Separate island; not your DID |

## 2.13 Phone architecture (when enabled)

```
Caller
  → one paid DID (LiveKit OR Twilio, not both forever)
  → (if Twilio) HTTPS POST /twilio/incoming on Super-conductor
  → LiveKit room + dispatch agent_name=ara
  → ARA worker running
  → Voice brain: VOICE_MODE=grok_pipeline (default, cheaper)
       STT + Grok 4.5 + TTS
  → Mem0 same user_id as TypingMind
```

**HTTP 503 on Twilio webhook** means: missing env on the **live host**:
`LIVEKIT_URL`, `LIVEKIT_API_KEY`, `LIVEKIT_API_SECRET`, `TWILIO_AUTH_TOKEN`.

Check anytime:

```bash
curl -s https://YOUR_PUBLIC_HOST/ready/telephony
```

Want: `"telephony_ready": true`
If false: fix only the names listed in `"missing"`.

---

# 3. Cost control and keep / ditch

## 3.1 Cost rules (non-negotiable for 2 people)

1. **Max one paid AI phone number** until revenue from voice.
2. **Default voice:** `VOICE_MODE=grok_pipeline` (Grok + cheap STT/TTS).
3. **OpenAI Realtime** only for special low-latency demos (`VOICE_MODE=openai_realtime`).
4. **One Mem0 project**, one `MEM0_USER_ID` (example: `ccg-operator`).
5. Do not open a new cloud product until the current path works.
6. Idle paid DIDs = release them; free T-Mobile line is never “waste.”

## 3.2 Keep / ditch matrix

| Asset | Verdict | Rule |
|-------|---------|------|
| TypingMind + Mem0 + Grok | **KEEP** | Primary Track A tool |
| OpenRouter | **KEEP** if already paid/used | Backup multi-model |
| xAI API key | **KEEP** | Direct Grok |
| Super-conductor repo | **KEEP** | Kernel for Track B |
| LiveKit project ARA | **KEEP if used** | Earn keep with real demos/calls |
| **619-639-4611** (LiveKit) | **ONE paid DID candidate** | Keep only if ARA is real |
| **619-583-3329** (Twilio) | **DITCH if idle** | Keep only if webhook live + SMS plan |
| T-Mobile free iPhone number | **KEEP** | Test line forever |
| Dual paid DIDs both idle | **NEVER** | Pick one or none |
| Extra Azure/GCP experiments | **PARK** | After prototype need only |

## 3.3 Phone decision (write one letter and stick to it)

| Choice | Meaning |
|--------|---------|
| **A** | Keep **LiveKit 619-639-4611** only; release Twilio when ready |
| **B** | Keep **Twilio 619-583-3329** only if webhook path is finished |
| **C** | **No paid AI DID for now** — Level 1–2 chat only; free T-Mobile for life |

**Default when tired or overloaded: C or A, never both idle.**

---

# 4. Work plan (order of operations)

Do **in this order**. Finish one block before the next. No dates.

## 4.1 Priority order of the five workstreams

| Priority | Workstream | Why |
|----------|------------|-----|
| **1** | Fix telephony honesty (503 + `/ready/telephony`) | Stop paying for mystery phones |
| **5** | Grok ZIP ingest (`grok_processor` / `ingest.py`) | Archive memory for demos; not required for chat |
| **3** | Mem0 shared (TypingMind = Conductor = ARA) | Product differentiator: “it remembers” |
| **4** | Phone brain = Grok pipeline (not Realtime default) | LiveKit can earn keep without burning cash |
| **2** | One-number policy + free T-Mobile test line | Stifle cost |

In practice for a human who is tired: **do Level 1 chat first**, then secrets/phone, then ingest.

---

## 4.2 Part A — Make money path (chat + memory) — DO THIS FIRST

### Step A1 — Open the correct TypingMind
- Use the workspace that already has models/keys (not a blank trial window).
- **Done when:** You can type in a chat.

### Step A2 — Grok answers
- Select **Grok 4.5** if available; else **Grok 4.20 Multi-Agent** is still valid for Level 1.
- Keys: xAI at console.x.ai **or** OpenRouter Grok model id.
- Test:

```text
Reply with one line: which model you are, and say "CCG chat online".
```

- **Done when:** You get a normal reply.

### Step A3 — Mem0 memory
- Confirm Mem0 plugin has API key.
- Set / note **user id** (recommend `ccg-operator` — any fixed string is fine if consistent).
- Test:

```text
Remember this for later: CCG primary operator is Jay; priority is one working demo path, not every cloud.
```

Then new chat:

```text
What do you remember about CCG priorities?
```

- **Done when:** It recalls something close.
- **If fail:** Fix only Mem0 key/user id. Do not touch phone.

### Step A4 — Super-conductor local env (optional for Level 1, needed for Level 2)
- Folder: `Documents/GitHub/Super-conductor-agent-`
- Copy `.env.example` → `.env` if needed.
- Minimum useful:

```env
XAI_API_KEY=...
# or OPENROUTER_API_KEY=...
OPENAI_API_KEY=...
MEM0_API_KEY=...
MEM0_USER_ID=ccg-operator
VOICE_MODE=grok_pipeline
VOICE_GROK_MODEL=grok-4.5
CONDUCTOR_PROVIDER=xai
CONDUCTOR_MODEL=grok-4.5
OPERATOR_USERNAME=operator
OPERATOR_PASSWORD=long-random-password
```

- Never commit real keys.
- **Done when:** Mem0 user id matches TypingMind.

**Part A complete = Track A is alive. You may stop here and still have a real system.**

---

## 4.3 Part B — Phone / LiveKit (only after Part A)

### Step B1 — Write phone choice A / B / C
- **Done when:** Written down.

### Step B2 — Put secrets on the **public host** (not only laptop)
Required for Twilio bridge 503 to go away:

```text
LIVEKIT_URL
LIVEKIT_API_KEY
LIVEKIT_API_SECRET
TWILIO_AUTH_TOKEN
```

Also for Grok voice + memory:

```text
XAI_API_KEY or OPENROUTER_API_KEY
OPENAI_API_KEY
MEM0_API_KEY
MEM0_USER_ID
VOICE_MODE=grok_pipeline
```

- Redeploy/restart after setting.
- **Done when:** Host env UI shows those names filled.

### Step B3 — Readiness check

```bash
curl -s https://YOUR_PUBLIC_HOST/ready/telephony
# or from repo:
./scripts/check_telephony.sh https://YOUR_PUBLIC_HOST
```

- **Done when:** `"telephony_ready": true` OR you chose C and parked paid DIDs.

### Step B4 — Start ARA worker (must stay running for calls)

```bash
cd ~/Documents/GitHub/Super-conductor-agent-
source .venv/bin/activate
python -m livekit_agent.agent start
```

- Agent name must remain **`ara`**.
- **Done when:** Process starts without crash.

### Step B5 — Twilio webhook (only if choice B or dual-bridge still needed)
- Twilio Console → number → Voice → POST
  `https://YOUR_PUBLIC_HOST/twilio/incoming`
- **Done when:** URL saved.

### Step B6 — Test call from free T-Mobile iPhone
- Call the **one** paid DID you kept.
- Expect connect / ARA voice, or a clear failure you can fix.
- **Done when:** Call result is known (success or named error).

### Step B7 — Release idle paid number
- If Twilio never used after bridge decision: release **619-583-3329**.
- If LiveKit never used: release or park **619-639-4611**.
- Never keep both idle.

---

## 4.4 Part C — Grok archive ingest (workstream 5; optional)

Does **not** make the phone work. Builds long archive RAG for demos / “we know your history.”

1. Export Grok ZIP from Grok/X data tools.
2. Save as: `Super-conductor-agent-/data/raw/grok_export.zip`
3. Run:

```bash
cd ~/Documents/GitHub/Super-conductor-agent-
source .venv/bin/activate
python ingest.py --grok data/raw/grok_export.zip
```

4. Details: `docs/GROK_INGEST.md`
5. **Done when:** Ingest completes without error (or you have the log to fix).

---

## 4.5 Part D — Track B (sell later) — only after Track A is real

1. One deploy story (one host, one env template = `.env.example`).
2. Mem0: later use `user_id` per client.
3. White-label UI later (Open WebUI or custom); TypingMind is fine for operators now.
4. Voice as optional SKU (LiveKit worker image + one DID).
5. Document for buyers = this file + `TELEPHONY.md` + `GROK_INGEST.md`.

---

# 5. Key files in the repo (if chat is wiped, open these)

| File | Why |
|------|-----|
| `docs/CCG_BUSINESS_PLAN.md` | **This plan** |
| `docs/BUSINESS_STACK.md` | Short stack summary |
| `docs/TELEPHONY.md` | 503, DIDs, deploy checklist |
| `docs/GROK_INGEST.md` | Grok ZIP import |
| `.env.example` | Every env name |
| `livekit_agent/agent.py` | ARA voice worker (Grok pipeline default) |
| `memory/mem0_client.py` | Shared Mem0 client |
| `api/server.py` | `/ready/telephony`, `/twilio/incoming` |
| `data_processors/grok_processor.py` | Grok export → conversations |
| `scripts/check_telephony.sh` | One-command health check |
| `conductor/agent.py` | Text conductor + Mem0 |

---

# 6. Environment cheat sheet (copy into host secrets)

```env
# Operator
OPERATOR_USERNAME=operator
OPERATOR_PASSWORD=...

# Brain
XAI_API_KEY=...
# OPENROUTER_API_KEY=...
OPENAI_API_KEY=...

# Memory (must match TypingMind Mem0)
MEM0_API_KEY=...
MEM0_HOST=https://api.mem0.ai
MEM0_USER_ID=ccg-operator

# Voice cost default
VOICE_MODE=grok_pipeline
VOICE_GROK_MODEL=grok-4.5

# LiveKit
LIVEKIT_URL=wss://....livekit.cloud
LIVEKIT_API_KEY=...
LIVEKIT_API_SECRET=...
# LIVEKIT_PHONE_NUMBER=+16196394611

# Twilio (only if using Twilio DID)
# TWILIO_ACCOUNT_SID=AC...
# TWILIO_AUTH_TOKEN=...
# TWILIO_PHONE_NUMBER=+16195833329
```

---

# 7. Test scripts (copy-paste)

### 7.1 Chat model

```text
Reply with one line: which model you are, and say "CCG chat online".
```

### 7.2 Memory

```text
Remember this for later: CCG primary operator is Jay; priority is one working demo path, not every cloud.
```

```text
What do you remember about CCG priorities?
```

### 7.3 Telephony ready

```bash
curl -s https://YOUR_PUBLIC_HOST/ready/telephony
```

### 7.4 Start ARA

```bash
cd ~/Documents/GitHub/Super-conductor-agent-
source .venv/bin/activate
python -m livekit_agent.agent start
```

### 7.5 Ingest Grok

```bash
python ingest.py --grok data/raw/grok_export.zip
```

---

# 8. Decision log (fill in by hand; survives any AI wipe)

| Date | Decision | Choice | Notes |
|------|----------|--------|-------|
| | Phone policy | A / B / C | |
| | Lead model | grok-4.5 / other | |
| | Mem0 user id | | |
| | Public host URL | | |
| | Kept paid DID | | |
| | Released DID | | |
| | Level achieved | 1 / 2 / 3 | |

---

# 9. What not to do (protection list)

1. Do not run five half-wired clouds at once.
2. Do not keep two idle paid phone numbers.
3. Do not expect `grok_processor.py` to answer the phone.
4. Do not expect X app Grok voice to use your 619 numbers.
5. Do not put API keys in git or public chats.
6. Do not switch to OpenAI Realtime as default “just because.”
7. Do not change Mem0 user id on one side only (breaks shared memory).
8. Do not assume laptop `.env` fixes production 503 — host secrets must match.

---

# 10. One-page summary (print this)

**Business:** 2 people. Make money now with chat+memory. Sell the system later as a package.

**Kernel:** TypingMind + Mem0 + Grok + Super-conductor (+ optional LiveKit ARA).

**Win levels:** (1) Grok chat + Mem0 recall → (2) same Mem0 in Conductor → (3) phone ready or consciously off.

**Cost:** One paid DID max. Free T-Mobile for testing. Grok pipeline voice. Release idle Twilio/LiveKit DIDs.

**Order:** Chat Grok → Mem0 → env match → host secrets → `/ready/telephony` → ARA worker → one test call → ingest Grok ZIP when ready.

**If AI chat is wiped:** Open this file
`Documents/GitHub/Super-conductor-agent-/docs/CCG_BUSINESS_PLAN.md`

---

*End of durable business plan. You go at your own pace. One step at a time is still progress.*
