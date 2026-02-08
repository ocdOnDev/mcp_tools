# YouTube Tools - Quick Start Guide

## 🚀 Quick Reference

Three tools for YouTube video analysis with local Ollama LLM:

### 1️⃣ Extract Transcript
```bash
curl -X POST http://localhost:8000/mcp/tools/invoke \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "youtube_transcript",
    "args": {"url": "https://www.youtube.com/watch?v=VIDEO_ID"}
  }'
```

### 2️⃣ Summarize Any Text
```bash
curl -X POST http://localhost:8000/mcp/tools/invoke \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "summarize_with_ollama",
    "args": {"text": "Your long text here..."}
  }'
```

### 3️⃣ Get Video Summary (One Step)
```bash
curl -X POST http://localhost:8000/mcp/tools/invoke \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "youtube_summary",
    "args": {"url": "https://www.youtube.com/watch?v=VIDEO_ID"}
  }'
```

---

## 📊 Example Output

**Input:**
```json
{
  "tool": "youtube_summary",
  "args": {
    "url": "https://www.youtube.com/watch?v=EmfoQWQ1DR8",
    "summary_length": "brief"
  }
}
```

**Output:**
```json
{
  "summary": "Comparison of GitHub Copilot and Claude Code...",
  "video_id": "EmfoQWQ1DR8",
  "title": "GitHub Copilot vs. Claude Code...",
  "author": "Adam Tarantino",
  "transcript_word_count": 4384,
  "summary_word_count": 155,
  "model_used": "gemma:latest",
  "success": true
}
```

---

## ⚙️ Common Options

### Summary Lengths
- `"summary_length": "brief"` → 2-3 sentences
- `"summary_length": "medium"` → 1-2 paragraphs (default)
- `"summary_length": "detailed"` → 3-4 paragraphs

### Models
- `"model": "gemma:latest"` → Fast (5-10 sec)
- `"model": "gpt-oss:20b"` → Better quality (15-30 sec)

### Transcript Options
- `"preserve_formatting": true` → Include timestamps
- `"language": "es"` → Spanish captions

---

## 🧪 Test It

```bash
# Start server
python -m uvicorn app:app --reload

# Run tests
python test_youtube_tools.py
```

---

## 🆘 Troubleshooting

### Ollama not running?
```bash
ollama serve
```

### Model not found?
```bash
ollama pull gemma:latest
```

### Check available tools
```bash
curl http://localhost:8000/tools
```

---

## 📖 Full Documentation

See [YOUTUBE_TOOLS_DOCUMENTATION.md](YOUTUBE_TOOLS_DOCUMENTATION.md) for complete guide.

---

## ✅ Features

- ✅ No API keys required
- ✅ 100% local processing (privacy!)
- ✅ Zero cost
- ✅ Works offline (except fetching transcript)
- ✅ Multiple models supported
- ✅ Robust error handling
