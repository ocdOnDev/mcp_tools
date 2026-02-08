# YouTube Tools Documentation

Complete guide for the three YouTube analysis tools with local Ollama LLM integration.

---

## Overview

Three powerful tools for YouTube video analysis:

1. **`youtube_transcript`** - Extract video transcripts/captions
2. **`summarize_with_ollama`** - Summarize any text using local Ollama LLM
3. **`youtube_summary`** - One-step video summary (combines 1 & 2)

### Key Features

✅ **No API keys required** - Uses public YouTube caption data
✅ **Local LLM** - Runs on your machine via Ollama (no external API calls)
✅ **Privacy-first** - All processing happens locally
✅ **Cost-free** - No usage charges or quotas
✅ **Production-ready** - Robust error handling and validation

---

## Prerequisites

### Required Software

1. **Ollama** - Already installed and running ✅
   ```bash
   # Verify installation
   ollama --version

   # Check running models
   curl http://localhost:11434/api/tags
   ```

2. **Python packages**
   ```bash
   pip install youtube-transcript-api  # Already installed ✅
   ```

### Available Ollama Models

Your current models:
- `gemma:latest` (9B parameters, fast)
- `gpt-oss:20b` (20.9B parameters, more capable)

Install more models:
```bash
ollama pull llama3        # Meta's Llama 3
ollama pull mistral       # Mistral 7B
ollama pull phi           # Microsoft Phi-2
```

---

## Tool 1: `youtube_transcript`

Extracts transcripts/captions from YouTube videos.

### Input Parameters

```python
{
    "url": str,                    # YouTube video URL (required)
    "language": str = "en",        # Caption language code (default: English)
    "preserve_formatting": bool = False  # Include timestamps (default: False)
}
```

### Output

```python
{
    "transcript": str,             # Full transcript text
    "video_id": str,              # Extracted video ID
    "language": str,              # Language of transcript
    "auto_generated": bool,       # True if auto-generated captions
    "word_count": int,            # Number of words in transcript
    "success": bool,              # Operation status
    "error_message": str          # Error details if failed
}
```

### Usage Examples

#### Basic Transcript Extraction

```bash
curl -X POST http://localhost:8080/mcp/tools/invoke \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "youtube_transcript",
    "args": {
      "url": "https://www.youtube.com/watch?v=b8ZFmooE2UQ"
    }
  }'
```

#### With Timestamps

```bash
curl -X POST http://localhost:8080/mcp/tools/invoke \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "youtube_transcript",
    "args": {
      "url": "https://www.youtube.com/watch?v=b8ZFmooE2UQ",
      "preserve_formatting": true
    }
  }'
```

Output format:
```
[00:18] ♪ We're no strangers to love ♪
[00:22] ♪ You know the rules and so do I ♪
[00:27] ♪ A full commitment's what I'm thinking of ♪
```

#### Different Language

```bash
curl -X POST http://localhost:8080/mcp/tools/invoke \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "youtube_transcript",
    "args": {
      "url": "https://www.youtube.com/watch?v=b8ZFmooE2UQ",
      "language": "es"
    }
  }'
```

### Supported URL Formats

- `https://www.youtube.com/watch?v=VIDEO_ID`
- `https://youtu.be/VIDEO_ID`
- `https://www.youtube.com/embed/VIDEO_ID`
- `https://www.youtube.com/v/VIDEO_ID`

### Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Invalid YouTube URL | URL format not recognized | Use standard YouTube URL |
| Video unavailable | Video doesn't exist or is private | Check video URL |
| No transcript available | Video has no captions | Try different video or check caption settings |
| Transcripts disabled | Creator disabled captions | Cannot retrieve transcript |

---

## Tool 2: `summarize_with_ollama`

Summarizes any text using local Ollama LLM.

### Input Parameters

```python
{
    "text": str,                          # Text to summarize (required)
    "model": str = "gemma:latest",        # Ollama model to use
    "summary_length": str = "medium",     # "brief", "medium", or "detailed"
    "ollama_url": str = "http://localhost:11434"  # Ollama server URL
}
```

### Output

```python
{
    "summary": str,              # Generated summary
    "model_used": str,           # Model that generated summary
    "input_length": int,         # Word count of input
    "summary_length": int,       # Word count of summary
    "success": bool,             # Operation status
    "error_message": str         # Error details if failed
}
```

### Summary Length Options

| Option | Description | Typical Output |
|--------|-------------|----------------|
| `brief` | 2-3 sentences | ~40-60 words |
| `medium` | 1-2 paragraphs | ~100-150 words |
| `detailed` | 3-4 paragraphs | ~200-300 words |

### Usage Examples

#### Brief Summary

```bash
  curl -X POST http://localhost:8080/mcp/tools/invoke \
    -H "Content-Type: application/json" \
    -d '{
      "tool": "summarize_with_ollama",
      "args": {
        "text": "I come out of the bathroom I tackle him our liaison partners and our security guys bust in from the side room I have him pinned down and he's like Allah abbar Allah abbar our liaison liaison Partners give him a shot of demeral and it knocks him out people die in hotels every single day so we put him on a gurnie we covered him up like a dead body we took him out the back and put him in the ambulance and when he came to he was tied to a chair so I said now it's my turn the second assassination attempt this is right after you left Greece right yeah what's this story you know out of all the things that I ever did at the agency I think this is the one thing that I'm the most proud of it wasn't the abuaba operation although I was proud of abua I'm ashamed for our country as to what ended up happening after abua we'll get into that in detail yeah but but the second assassination attempt I was so proud of myself because by then I was a seasoned case officer I knew exactly what I was doing and I was good at it how many years had you been working as a case officer at this time by then uh yeah three years doing high-risk stuff like I didn't become a case officer and then go to London or Rome right I went into the mouth of the Beast with 17 November so I get a cable from a buddy of mine who's the chief of a station in the Middle East and he said buddy he goes I got a case we're working on here it's a double agent and it's just too dangerous for me or for any of my people to handle we need somebody who doesn't live here you think you'd like to do it I said heck yeah I was divorced I had nothing to lose could use the overtime you know was looking to buy a house why not so I fly out there and and all these guys are my friends right we were all in training together or in Arabic together or whatever we're all friends so in fact this is the guy that introduced me to my second wife yeah so I go so what what gives and he says well we recruited this guy and he works for an American defense contractor as an engineer but he doesn't know that we know that he's actually a double agent for one of our greatest enemies in the world wow I think they wouldn't let me say the country in the book one of our most serious enemies in the world so so he thinks he's working for us but we know that the bad guys have tasked him with identifying the station chief for an assassination so he said can you pretend to be me I said sure I said we're going to have to like be really serious about security but yeah I can do this so he said Remember the guy has no idea that we know that he's a double I had never worked a double agent case before I had only learned about double agent cases in training like oh this is very rare but in case this happens you know here's what you do and you know all that so so he triggers a meeting or the the original Handler triggers the meeting and um the guy comes and I said hi my name's Nick you wanted to meet the chief you met him hi nice to meet you Nick am I going to be dealing with you from now on I said yes we we believe that you're important enough that uh that I'll handle you directly and he's like okay that's what I that's what I wanted and I said okay well in this in this introductory meeting let's just go over the basic stuff we'll go over security and surveillance surveillance detection and a Communications uh uh strategy so I had what he didn't know was at the time called a triband cell phone cell phones were still very new and this triband cell phone um it was a it was a local number in that country but it would ring no matter where I was in the world revolutionary idea at the time you didn't have to put in 20 digits it was just a local number so he he thought that I was there all the time in fact I'm in Washington uh but if he needed me the phone would ring so I said here's my number so you have my direct number call me if you need anything if you need to meet you need to trigger a meeting we'll come up with a plan in the meantime let's do this on such and such a date at such and such a hotel and what I want you to do is plan out your surveillance detection routes make sure that they're very sophisticated and I want you to go rent a post office box so in the event of an emergency where we can't reach each other by phone you can send a message to the post office box I'll go retrieve it and I'll know where the next meeting should be held okay so we shake hands he shakes hands with the outgoing guy great now he's dealing with the station Chief instead of doing a surveillance detection rope route he drove directly to the enemy Embassy directly now if he had done a surveillance detection route he may have seen that we had four cars with eight officers on him never noticed a thing then they reported back to their Capital he's in with the chief he did it he's in with the chief so we're able to track their Communications so I go back out a month later he rented the the post office box then I go back out a month after that and he did this thing for me and he did that thing for me and we're establishing a rapport so I do this for like six or eight months and then I get a call from my buddy who's the actual Chief and he said listen we're going to have to kill this operation I said what why it's going well he said no um they just gave him orders to kill you in the next meeting I said come on man I said he's afraid of his own shadow he's not gonna he's not going to kill me and he said we we have to we have to kill the operation and I said no no rash decisions let's do a conference call so I got all the headquarters Mucky mucks together and the station guys and I said listen listen let's do the next meeting at the Marriott because every Marriott everywhere in the world is exactly the same you come in the door and the bathroom is right there on your right so we get two adjoining rooms that are connected by a door I'll be in the bathroom and when he knocks on the door I'll say come in I'll have it propped open with the lock the secure lock you know how they do he comes in I grab him you guys and liaison come in from the other room and we get him they're like uh it's risky I said come on guys what do we do for a living here this guy's a Bonafide terrorist he's ordered to kill me then he's going to kill you and he's going to kill you next and he's going to kill you after that we're going to stop these guys or not okay let's do it so I get to the hotel and I'm waiting and I got to the hotel hours early hours which was the plan and we've got our guys in the lobby and one of them calls me from the lobby and he said bad news he goes the bad guys are here in the lobby and they've got at least three teams I said sh [ __ ] I didn't expect that the idea being if he chickens out and doesn't shoot me they're going to shoot me as I'm trying to escape it's like dog G it we didn't consider that we didn't think they'd have the guts to do it we we just thought that they wanted a degree of separation I said okay so we can't use the front door so we have to use the back door and they're like okay he's he's coming in right now and just as he's coming in he calls me and I never would tell him directly what room we're in I would say come up to the fourth floor or come up to the fifth floor and then he would come up to the fifth floor and I'd say I'm in room 2:11 or 8:15 meet me in 5 minutes and then I would take the elevator and he would take the stairs so that way he didn't drag surveillance with him and and then they try to kill me so he calls me he said I'm here I said come up to the to the eighth floor it was the top floor come up to the eighth floor and um and he goes okay so he comes up to the eighth floor and I go walk with me over to the stairs so we walk over the stairs and we go into the stairwell and I said let's go up to the roof he's like what I said' let's go up to the roof he goes I don't I don't think I want to go up to the roof I said yeah come on let's go he said I'm uncomfortable going up to the roof and I said why you think I'm going to throw you off the roof come on let's go we'll talk up there it's a nice day he goes I don't want to go to the roof I said get up up on the [ __ ] roof he said you're scaring me I said and you're pissing me off get up on the roof I don't think I like this I don't like it I don't like it I go what's your problem I thought we're friends you told me last time you were my brother what do you think I'm going to do to you up there I I don't want to I don't want to go up there I go get up on the roof so one step at a time he gets up to the roof I said now stay here for 5 minutes and meet me in room 5:15 and I said you worry me sometimes so I go back down five minutes later he knocks on 5:15 I said come in he comes in I come out of the bathroom I tackle him our liaison partners and our security guys bust in from the side room I have him pinned down and he's like allahar allahar and he says I'll [ __ ] kill you and I said [ __ ] I said do you think I'm so stupid that I didn't know you came here to kill me tonight do you think I'm so unprofessional that I don't know that you're a double agent I said you're the stupid one you're the stupid one because your life is over now over allahar he kept saying I said yeah keep telling your yourself that see how far that gets you but remember the bad guys are in the lobby and they're looking at their watches like where is he we haven't heard anything So the plan we had come up with was our liaison liaison Partners give him a shot of demerell and it knocks him out well the truth is people die in hotels every single day so we put them on a gurnie we covered them up like a dead body we took him out the back and put him in the ambulance and we drove in an ambulance from the back door the cargo whatever the garbage door to their intelligence Service headquarters and when he came to he was tied to a chair so I said now it's my turn you [ __ ] idiot I said your life is over so now I'm going to ask you a question that's going to determine how the rest of your life is going to be spent we know who you are we know who you work for and we know that you're in charge of the arms cash so I want to know where are the weapons he's like [ __ ] you I will never tell you [ __ ] it's like that's the wrong answer he would never tell us so we all huddled they put him in a cell and we all huddled together and I said listen I have an idea we know where he lives and we know that he has he has a safe in the hotel he he had referenced the safe a couple times I said I wonder if the arms are in the safe and they were like okay but how do we get into the hot get into the house I said let's just just break in and they were like no can't do it he's got a livein Filipino made can't do it and I said okay let's declare a an environmental emergency a gas leak we'll say there's a gas leak and then we'll Evacuate the neighborhood he lived in a culde saacs there were like Eight houses and they're like no can't do it we don't have underground gas lines here we use propane I saidoh my God okay get a freaking 18wheeler of propane we'll spill the pro propane on the street and then we'll declare an emergency they're like that we could do so this 18wheeler comes to the house we're all at the house by then there's this giant wheel and I go like this with the Giant Wheel and I spill all this propane on the ground and then we call 115 which is their version of 911 and we said oh there's a big propane spill we need the fire department so the fire department comes and they evacuate all the houses and then we break into his house and the safe is like this big that was it like it's not big enough for anything like the safe in my bedroom is bigger than this this is more like a strong box than a safe so we had the locks and pick guy and he cracks it and uh all it has in it is a a slip of paper it was a a map like a kids map and it had an X he had written this X on the map and I go what are the chances that this is the weapons cache and they were like well this is all we have so let's go for it so we all got in these jeeps and we followed the map to a town that was about an hour south and then past the town we went out into the um the desert and we're following the map you know 100 Paces and 50 paces and 30 paces and there is an abandoned bunker with all the weapons and it wasn't just weapons it was mines and grenades and rocket launchers and that group no longer exists we put the entire group out of business that night yeah and then years later I ran into the chief and I go whatever happened to that guy and he said oh dude he says life without parole means life without parole yeah y what's up guys thank you so much for taking the time to watch the interview um as you could probably tell this is a brand new channel so if you got anything out of this at all please like the video leave me a comment tell me what you thought tell me who you'd like to see on the show um I see every like I read every comment and I appreciate all of it especially in the beginning because because as you know that kind of support goes a long way on these platforms so most importantly I have some awesome guests coming up in the future for interviews um so please subscribe to the channel so you don't miss any of them but again thank you for your time appreciate the support and hope to see you again soon",
        "summary_length": "brief"
      }
    }'
```

#### Use Different Model

```bash
curl -X POST http://localhost:8000/mcp/tools/invoke \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "summarize_with_ollama",
    "args": {
      "text": "Your long text here...",
      "model": "gpt-oss:20b",
      "summary_length": "detailed"
    }
  }'
```

### Model Selection Guide

| Model | Speed | Quality | Best For |
|-------|-------|---------|----------|
| `gemma:latest` | Fast | Good | Quick summaries, shorter texts |
| `gpt-oss:20b` | Slower | Better | Detailed analysis, longer texts |
| `llama3` | Medium | Excellent | Balanced performance |
| `mistral` | Fast | Very Good | General purpose |

### Text Truncation

- Maximum input: **4,000 words** (~5,300 tokens)
- Longer text is automatically truncated
- Prevents context overflow for local models

### Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Cannot connect to Ollama | Ollama not running | Run `ollama serve` |
| Model not found | Model not installed | Run `ollama pull MODEL_NAME` |
| Request timed out | Text too long or slow model | Use shorter text or faster model |
| Invalid summary_length | Wrong parameter value | Use "brief", "medium", or "detailed" |

---

## Tool 3: `youtube_summary`

One-step solution: extracts transcript and generates AI summary.

### Input Parameters

```python
{
    "url": str,                          # YouTube video URL (required)
    "model": str = "gemma:latest",       # Ollama model to use
    "summary_length": str = "medium",    # "brief", "medium", or "detailed"
    "language": str = "en",              # Caption language
    "ollama_url": str = "http://localhost:11434"  # Ollama server URL
}
```

### Output

```python
{
    "summary": str,                   # AI-generated summary
    "video_id": str,                 # YouTube video ID
    "title": str,                    # Video title
    "author": str,                   # Channel name
    "transcript_word_count": int,    # Words in transcript
    "summary_word_count": int,       # Words in summary
    "model_used": str,               # LLM model used
    "auto_generated_captions": bool, # Caption source
    "success": bool,                 # Operation status
    "error_message": str             # Error details if failed
}
```

### Usage Examples

#### Quick Summary

```bash
curl -X POST http://localhost:8000/mcp/tools/invoke \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "youtube_summary",
    "args": {
      "url": "https://www.youtube.com/watch?v=EmfoQWQ1DR8"
    }
  }'
```

#### Brief Summary with Specific Model

```bash
curl -X POST http://localhost:8000/mcp/tools/invoke \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "youtube_summary",
    "args": {
      "url": "https://www.youtube.com/watch?v=EmfoQWQ1DR8",
      "summary_length": "brief",
      "model": "gpt-oss:20b"
    }
  }'
```

#### Detailed Analysis

```bash
curl -X POST http://localhost:8000/mcp/tools/invoke \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "youtube_summary",
    "args": {
      "url": "https://www.youtube.com/watch?v=EmfoQWQ1DR8",
      "summary_length": "detailed",
      "model": "gemma:latest"
    }
  }'
```

### Real-World Example

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
  "summary": "The video compares GitHub Copilot and Claude Code, two AI coding assistants. Copilot is IDE-integrated with more model options and starts at $10/month. Claude Code is terminal-based, more autonomous, and starts at $17/month. The best choice depends on individual needs and preferences.",
  "video_id": "EmfoQWQ1DR8",
  "title": "GitHub Copilot vs. Claude Code: Which AI Assistant Should You Use in 2025?",
  "author": "Adam Tarantino",
  "transcript_word_count": 4384,
  "summary_word_count": 55,
  "model_used": "gemma:latest",
  "auto_generated_captions": false,
  "success": true
}
```

---

## Performance Considerations

### Processing Times (Approximate)

| Video Length | Transcript | Summary (gemma) | Summary (gpt-oss:20b) |
|--------------|------------|-----------------|----------------------|
| 5 minutes | 1-2 sec | 5-10 sec | 15-30 sec |
| 15 minutes | 2-3 sec | 10-20 sec | 30-60 sec |
| 30 minutes | 3-5 sec | 15-30 sec | 60-120 sec |
| 60 minutes | 5-8 sec | 30-60 sec | 120-240 sec |

**Note:** Times vary based on:
- Model size and quantization
- CPU/GPU performance
- System load
- Transcript length

### Memory Usage

| Model | RAM Required | VRAM (GPU) |
|-------|--------------|------------|
| gemma:latest | ~6 GB | ~5 GB |
| gpt-oss:20b | ~14 GB | ~12 GB |
| llama3 | ~8 GB | ~6 GB |

---

## Best Practices

### 1. Choose the Right Tool

- **Just need transcript?** → Use `youtube_transcript`
- **Already have text?** → Use `summarize_with_ollama`
- **Want one-step solution?** → Use `youtube_summary`

### 2. Model Selection

```bash
# Fast summaries (< 10 seconds)
"model": "gemma:latest"

# Better quality (10-30 seconds)
"model": "llama3"

# Best quality (30-120 seconds)
"model": "gpt-oss:20b"
```

### 3. Summary Length

```bash
# Quick overview
"summary_length": "brief"      # 2-3 sentences

# Balanced detail
"summary_length": "medium"     # 1-2 paragraphs (default)

# Comprehensive analysis
"summary_length": "detailed"   # 3-4 paragraphs
```

### 4. Long Videos

For videos > 60 minutes:
1. Use `youtube_transcript` to get full transcript
2. Manually chunk the transcript
3. Summarize each chunk with `summarize_with_ollama`
4. Combine summaries

### 5. Error Recovery

```python
# Check Ollama status
curl http://localhost:11434/api/tags

# If not running:
ollama serve

# Test with simple generation:
curl http://localhost:11434/api/generate -d '{
  "model": "gemma:latest",
  "prompt": "Say hello",
  "stream": false
}'
```

---

## Integration Examples

### Python Script

```python
import requests

def summarize_video(url, summary_length="medium"):
    """Get AI summary of YouTube video."""
    response = requests.post(
        "http://localhost:8000/mcp/tools/invoke",
        json={
            "tool": "youtube_summary",
            "args": {
                "url": url,
                "summary_length": summary_length
            }
        }
    )
    result = response.json()

    if result["result"]["success"]:
        return result["result"]["summary"]
    else:
        raise Exception(result["result"]["error_message"])

# Usage
summary = summarize_video("https://www.youtube.com/watch?v=VIDEO_ID")
print(summary)
```

### Bash Script

```bash
#!/bin/bash

# summarize_youtube.sh
URL=$1
LENGTH=${2:-medium}

curl -s -X POST http://localhost:8000/mcp/tools/invoke \
  -H "Content-Type: application/json" \
  -d "{
    \"tool\": \"youtube_summary\",
    \"args\": {
      \"url\": \"$URL\",
      \"summary_length\": \"$LENGTH\"
    }
  }" | python -m json.tool

# Usage:
# ./summarize_youtube.sh "https://www.youtube.com/watch?v=VIDEO_ID" brief
```

---

## Troubleshooting

### Common Issues

#### 1. "Cannot connect to Ollama"

**Solution:**
```bash
# Check if Ollama is running
ps aux | grep ollama

# Start Ollama if not running
ollama serve &

# Test connection
curl http://localhost:11434/api/tags
```

#### 2. "Model not found"

**Solution:**
```bash
# List installed models
ollama list

# Install missing model
ollama pull gemma:latest
```

#### 3. "No transcript available"

**Causes:**
- Video has no captions
- Captions disabled by creator
- Video is private/unavailable

**Solutions:**
- Check video has captions (CC button on YouTube)
- Try different video
- Request creator enable captions

#### 4. "Request timed out"

**Solutions:**
```bash
# Use faster model
"model": "gemma:latest"

# Use shorter summary
"summary_length": "brief"

# Increase timeout (if using custom client)
timeout=300  # 5 minutes
```

#### 5. Summary quality is poor

**Solutions:**
```bash
# Use larger model
"model": "gpt-oss:20b"  # or "llama3"

# Request detailed summary
"summary_length": "detailed"

# Check transcript quality first
# (auto-generated captions may have errors)
```

---

## API Reference

### Endpoints

```
GET  /tools                    # List all tools
POST /mcp/tools/invoke         # Execute tool
GET  /mcp/tools/metadata       # Get tool schemas
```

### Tool Names

- `youtube_transcript`
- `summarize_with_ollama`
- `youtube_summary`

### Request Format

```json
{
  "tool": "TOOL_NAME",
  "args": {
    "param1": "value1",
    "param2": "value2"
  }
}
```

### Response Format

```json
{
  "tool": "TOOL_NAME",
  "success": true,
  "result": {
    // Tool-specific output fields
    "success": true,
    "error_message": ""
  }
}
```

---

## Testing

### Run Test Suite

```bash
# Run all tests
python test_youtube_tools.py

# Test individual tools
python -c "from tools.youtube_transcript import *; ..."
```

### Test Data

Safe test videos (with captions):
- `https://www.youtube.com/watch?v=dQw4w9WgXcQ` (Rick Astley - Never Gonna Give You Up)
- `https://www.youtube.com/watch?v=9bZkp7q19f0` (Gangnam Style)

---

## Legal & Ethical Considerations

### ✅ Legal & Ethical

- ✅ Extracting public captions/transcripts
- ✅ Summarizing for personal use
- ✅ Educational and research purposes
- ✅ Accessibility improvements
- ✅ Using local LLM (privacy-preserving)

### ❌ Not Legal/Ethical

- ❌ Downloading video/audio files
- ❌ Bypassing content protection
- ❌ Commercial use without permission
- ❌ Redistributing copyrighted content
- ❌ Violating YouTube Terms of Service

### Fair Use Guidelines

This tool is designed for:
- Personal research and learning
- Accessibility (helping those who can't watch videos)
- Time-saving summaries
- Content analysis

Always respect:
- Creator's copyright
- YouTube's Terms of Service
- Fair use principles

---

## Performance Optimization

### Speed Tips

1. **Use faster models for quick summaries**
   ```json
   {"model": "gemma:latest"}  // Fastest
   ```

2. **Choose appropriate summary length**
   ```json
   {"summary_length": "brief"}  // 2-3 sentences, fast
   ```

3. **Run Ollama with GPU acceleration**
   ```bash
   # Ollama automatically uses GPU if available
   nvidia-smi  # Check GPU usage
   ```

4. **Increase Ollama context window** (for very long videos)
   ```bash
   # In Modelfile
   PARAMETER num_ctx 8192
   ```

---

## Future Enhancements

Potential additions:
- [ ] Multi-language summary translation
- [ ] Chapter detection and segmented summaries
- [ ] Key point extraction (bullet points)
- [ ] Sentiment analysis
- [ ] Speaker diarization (who said what)
- [ ] Integration with other video platforms
- [ ] Batch processing multiple videos
- [ ] Caching summaries to avoid re-processing

---

## Support

### Getting Help

1. Check this documentation
2. Review error messages carefully
3. Test with known-good videos
4. Verify Ollama is running
5. Check system resources (RAM/VRAM)

### Reporting Issues

When reporting issues, include:
- Video URL
- Tool used
- Model selected
- Error message
- Ollama model list (`ollama list`)
- System specs (RAM, GPU)

---

## Conclusion

You now have three powerful tools for YouTube video analysis:

1. **`youtube_transcript`** - Fast, flexible transcript extraction
2. **`summarize_with_ollama`** - Local AI summarization for any text
3. **`youtube_summary`** - Complete one-step video summarization

All running locally with **zero API costs** and **complete privacy**.

Happy summarizing! 🎥✨
