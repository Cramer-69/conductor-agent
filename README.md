# Conductor Super Agent

A local-first AI system that aggregates conversations from **Grok**, **ChatGPT**, **Gemini**, and **Antigravity** into a unified knowledge base with persistent memory across all your AI interactions.

## 🎯 Features

- **Multi-Platform Aggregation**: Combine conversations from all major AI platforms
- **Semantic Search**: RAG-based retrieval using ChromaDB vector database
- **Persistent Memory**: Never lose context across conversations
- **Code Snippet Extraction**: Automatically extracts and indexes code from all conversations
- **Privacy First**: Runs 100% locally on your machine
- **Rich CLI Interface**: Beautiful terminal interface with search and filtering

## 🚀 Quick Start (Windows)

**Double-click `Start_Super_Agent.bat` on your Desktop.**

This will:

1. Auto-configure the environment
2. Install any missing dependencies (self-healing)
3. Launch the Multi-AI Super Agent interface

---

## 🤖 Supported Providers

- **Google Gemini** (Primary, Auto-configured)
- **Grok / xAI** (Added via Desktop key)
- **Perplexity** (Search enabled)
- **OpenAI** (Fallback)
- **Claude / Titan / Llama on AWS Bedrock** — reach these through your own
  AWS account, no per-provider API key required. See
  [AWS Bedrock](#aws-bedrock) below.

The conductor auto-detects whichever provider is configured. Bedrock is
selected when AWS credentials are present and no higher-priority key is set —
its calls go through Bedrock's model-agnostic **Converse** API, so switching
models is just a `BEDROCK_MODEL_ID` change.

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd conductor_agent
pip install -r requirements.txt
```

### 2. Configure Environment

Copy the example environment file and add your API keys:

```bash
copy .env.example .env
```

Edit `.env` and add your OpenAI API key:

```
OPENAI_API_KEY=sk-your-key-here
```

### 3. Export Your Conversations

#### ChatGPT

1. Go to [chat.openai.com](https://chat.openai.com)
2. Click your profile → Settings → Data Controls
3. Click "Export Data"
4. Download the ZIP file (you'll receive an email)
5. Extract `conversations.json`

#### Gemini

- **Method 1**: Use [Google Takeout](https://takeout.google.com)
  - Select "Gemini Apps Activity"
  - Download and extract
- **Method 2**: Save conversations as HTML
  - Open conversation in browser
  - Right-click → Save As → HTML

#### Grok/xAI

- Export from Grok settings (ZIP format)

#### Antigravity

- Conversations are automatically available at:

  ```
  C:\Users\<username>\.gemini\antigravity\brain
  ```

### 4. Ingest Your Data

Run the ingestion script to process and index your conversations:

```bash
# Ingest all platforms
python ingest.py --chatgpt "path/to/conversations.json" --gemini "path/to/gemini_export" --grok "path/to/grok_export.zip" --antigravity "C:/Users/jjc29/.gemini/antigravity/brain"

# Or just Antigravity (default)
python ingest.py

# Reset database and re-ingest
python ingest.py --reset --antigravity "C:/Users/jjc29/.gemini/antigravity/brain"
```

### 5. Start the CLI

```bash
python -m cli.interactive
```

## 💡 Usage Examples

### Basic Search

```
You: How did I implement authentication in previous projects?
```

### Search Code

```
You: /code python async patterns
```

### Platform-Specific Search

```
You: /platform chatgpt explain RAG architecture
```

### View Statistics

```
You: /stats
```

## 📁 Project Structure

```
conductor_agent/
├── config/              # Configuration management
│   └── settings.py
├── data_processors/     # Platform-specific processors
│   ├── base_processor.py
│   ├── chatgpt_processor.py
│   ├── gemini_processor.py
│   ├── grok_processor.py
│   └── antigravity_processor.py
├── knowledge_base/      # Vector store and retrieval
│   ├── embeddings.py
│   ├── vector_store.py
│   └── retrieval.py
├── cli/                 # Command-line interface
│   └── interactive.py
├── utils/               # Utilities
│   └── logger.py
├── data/                # Data storage
│   ├── raw/            # Raw exports
│   ├── processed/      # Processed conversations
│   └── chroma_db/      # Vector database
├── ingest.py           # Data ingestion script
├── requirements.txt     # Python dependencies
└── .env.example        # Environment template
```

## 🔧 Configuration

All settings can be configured in `.env`:

```env
# LLM Configuration
CONDUCTOR_MODEL=gpt-4o-mini
EMBEDDING_MODEL=text-embedding-3-small

# Vector Database
CHROMA_PERSIST_DIR=./data/chroma_db

# Search Parameters
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
TOP_K=5

# Data Paths
ANTIGRAVITY_BRAIN_DIR=C:/Users/jjc29/.gemini/antigravity/brain
```

## 🎨 CLI Commands

| Command | Description |
|---------|-------------|
| `<query>` | Ask any question |
| `/search <query>` | Search conversations |
| `/code <query>` | Search code snippets |
| `/platform <name> <query>` | Search specific platform |
| `/stats` | Show database statistics |
| `/clear` | Clear screen |
| `/help` | Show help |
| `/exit` | Exit application |

## 🔍 How It Works

1. **Data Processing**: Platform-specific processors parse and standardize conversations
2. **Embedding Generation**: Text is chunked and converted to semantic embeddings (OpenAI)
3. **Vector Storage**: Embeddings stored in ChromaDB for fast similarity search
4. **Retrieval**: Hybrid search with re-ranking by recency and relevance
5. **Context**: Retrieved conversations provide context for queries

## 🛠️ Troubleshooting

### "No relevant conversations found"

- Ensure you've run `ingest.py` to load your data
- Check that your export files are in the correct format
- Run `/stats` to verify database has content

### API Key Errors

- Verify `OPENAI_API_KEY` is set in `.env`
- Ensure the key has sufficient credits

### Import Errors

- Run `pip install -r requirements.txt`
- Ensure Python 3.9+ is installed

## 📊 Performance

- **Embedding Generation**: ~1000 tokens/second with caching
- **Search Speed**: <500ms for most queries
- **Storage**: ~1MB per 100 conversations
- **Cost**: ~$0.10 per 1000 conversations (embeddings)

## 🔐 Privacy

- **100% Local**: All data stays on your machine
- **No Telemetry**: ChromaDB telemetry disabled
- **API Calls**: Only for embeddings (text only, no PII)

## 🚀 Deploy

The web/voice API in `api/server.py` runs anywhere a Python container runs. The
recommended target is **Google Cloud Run** with the API key stored in **Secret
Manager**. Local Docker and Render also work.

### Required env vars

At least one LLM provider key:

| Variable | Where to get it |
|---|---|
| `OPENAI_API_KEY` | https://platform.openai.com/api-keys |
| `ANTHROPIC_API_KEY` | https://console.anthropic.com/settings/keys |
| `GOOGLE_API_KEY` | https://aistudio.google.com/app/apikey |
| `AWS_BEARER_TOKEN_BEDROCK` *or* `AWS_ACCESS_KEY_ID` + `AWS_SECRET_ACCESS_KEY` | AWS Bedrock (see below) |

The container binds to `0.0.0.0:${PORT}` (default `8080`). Cloud Run / Render
inject `PORT` automatically.

### AWS Bedrock

Reach Claude, Titan, Llama and other models through your own AWS account —
no separate provider API key to manage, since auth rides on whatever AWS
credentials the box already has. Calls go through Bedrock's model-agnostic
**Converse** API, so switching models is just a `BEDROCK_MODEL_ID` change.

#### 1. Enable model access

In the [Bedrock console](https://console.aws.amazon.com/bedrock/home#/modelaccess),
pick your **region** and request access to the model(s) you want (e.g. a
Claude model). Access is granted per-region and is usually instant. The region
must be one where both Bedrock and that model are available (e.g. `us-east-1`).

#### 2. Configure credentials — pick one

- **Bedrock API key (simplest):** Bedrock console → **API keys** → *Generate*.
  Set `AWS_BEARER_TOKEN_BEDROCK=...`.
- **AWS access keys:** an IAM user/role with `bedrock:InvokeModel` (and
  `bedrock:InvokeModelWithResponseStream` for streaming). IAM → Users →
  *Security credentials* → *Create access key*. Set `AWS_ACCESS_KEY_ID` and
  `AWS_SECRET_ACCESS_KEY` (plus `AWS_SESSION_TOKEN` for temporary STS creds).
- **Instance role (AWS compute only):** on EC2 / ECS / EKS / Lambda with an
  attached role that has Bedrock permissions, leave the above unset — boto3
  picks up the role automatically. Just set `AWS_REGION`. (Cloud Run and
  Render don't provide AWS IAM roles to containers — use explicit credentials
  there; see [Using Bedrock on Cloud Run / Render](#using-bedrock-on-cloud-run--render).)

#### 3. Pick a model (optional)

`BEDROCK_MODEL_ID` defaults to `anthropic.claude-3-5-sonnet-20240620-v1:0`.
List the exact IDs enabled in your account/region — some newer models are
inference-profile only and need a region-prefixed id like
`us.anthropic.claude-3-5-sonnet-20241022-v2:0`:

```bash
aws bedrock list-foundation-models --region us-east-1 \
  --query "modelSummaries[?providerName=='Anthropic'].modelId" --output table
```

#### 4. Run it

```bash
docker run --rm -p 8080:8080 \
  -e AWS_REGION=us-east-1 \
  -e AWS_BEARER_TOKEN_BEDROCK=your_bedrock_api_key \
  -e BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20240620-v1:0 \
  conductor-agent
```

Confirm with `/health` — `providers` should include `bedrock` and
`api_keys_configured` should be `true`.

### Local Docker

```bash
docker build -t conductor-agent .
docker run --rm -p 8080:8080 -e OPENAI_API_KEY=sk-... conductor-agent
# or pass a whole .env file:
docker run --rm -p 8080:8080 --env-file .env conductor-agent
```

Open http://localhost:8080 and check `/health` — `api_keys_configured` should be
`true`.

### Google Cloud Run (recommended)

One-time setup (replace `$PROJECT_ID`):

```bash
gcloud config set project $PROJECT_ID
gcloud services enable run.googleapis.com \
  artifactregistry.googleapis.com \
  secretmanager.googleapis.com

# Store the key in Secret Manager
echo -n "sk-your-openai-key" | \
  gcloud secrets create openai-api-key --data-file=-

# Grant the Cloud Run runtime SA access (project-default Compute SA)
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')
gcloud secrets add-iam-policy-binding openai-api-key \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

Build + deploy:

```bash
gcloud run deploy conductor-agent \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-secrets OPENAI_API_KEY=openai-api-key:latest
```

The deploy URL appears at the end. Hit `/health` to confirm
`api_keys_configured: true`.

To rotate the key:

```bash
echo -n "sk-new-key" | \
  gcloud secrets versions add openai-api-key --data-file=-
gcloud run services update conductor-agent --region us-central1 \
  --set-secrets OPENAI_API_KEY=openai-api-key:latest
```

### Render

The repo includes `render.yaml`. In the Render dashboard set `OPENAI_API_KEY`
under **Environment** — do not commit it. Render injects `PORT` automatically.

### Using Bedrock on Cloud Run / Render

Cloud Run and Render don't give containers AWS IAM roles the way EC2/ECS do,
so pass explicit AWS credentials as secrets alongside `AWS_REGION`:

```bash
gcloud run deploy conductor-agent \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars AWS_REGION=us-east-1 \
  --set-secrets AWS_ACCESS_KEY_ID=aws-access-key-id:latest,AWS_SECRET_ACCESS_KEY=aws-secret-access-key:latest
```

Scope the IAM user/role to `bedrock:InvokeModel` and
`bedrock:InvokeModelWithResponseStream` on the model ARNs you use. A Bedrock
API key (`AWS_BEARER_TOKEN_BEDROCK`) works here too, as a single secret.

### Troubleshooting

| Symptom | Fix |
|---|---|
| `502` / "service unavailable" on Cloud Run | Container didn't bind to `$PORT`. Ensure you're using the Dockerfile in this repo (shell-form `CMD`). |
| Logs show `No LLM API key is configured` | Set `OPENAI_API_KEY` (or `--set-secrets`) and redeploy. |
| `/api/chat` returns 500 | Check `/health` — if `api_keys_configured: false`, the key isn't reaching the container. |
| Bedrock calls fail with `AccessDeniedException` | Model access isn't enabled for that model/region in the Bedrock console, or the IAM principal lacks `bedrock:InvokeModel*`. |
| Bedrock calls fail with `ValidationException: invalid model identifier` | `BEDROCK_MODEL_ID` isn't a valid ID for that region. Run `aws bedrock list-foundation-models` (see [step 3](#3-pick-a-model-optional)); some models need a `us.`-prefixed inference-profile id. |
| `FileNotFoundError` for `antigravity_brain_dir` | Leave `ANTIGRAVITY_BRAIN_DIR` blank unless you actually have that folder. |

## 🚧 Future Enhancements

- [x ] LangGraph conductor orchestration with specialized sub-agents
- [ x] Web UI interface
- [x ] Support for more platforms (Claude, Perplexity)
- [ x] Real-time conversation sync
- [x ] Export to NotebookLM format
- [x ] Conversation analytics and insights

## 📝 License

MIT License - Feel free to use and modify

## 🤝 Contributing

This is a personal project, but feel free to fork and adapt for your needs!

---

**Built with**: Python, ChromaDB, OpenAI, LangChain, Rich CLI
