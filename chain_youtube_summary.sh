#!/bin/bash
# Chain YouTube transcript extraction with Ollama summarization

# Step 1: Get the transcript
echo "Fetching YouTube transcript..."
TRANSCRIPT_RESPONSE=$(curl -s -X POST http://localhost:8080/mcp/tools/invoke \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "youtube_transcript",
    "args": {
      "url": "https://www.youtube.com/watch?v=b8ZFmooE2UQ",
      "language": "es"
    }
  }')

# Step 2: Extract the transcript text using jq
TRANSCRIPT_TEXT=$(echo "$TRANSCRIPT_RESPONSE" | jq -r '.result.transcript')

# Check if we got the transcript
if [ -z "$TRANSCRIPT_TEXT" ] || [ "$TRANSCRIPT_TEXT" = "null" ]; then
  echo "Error: Failed to get transcript"
  echo "Response was: $TRANSCRIPT_RESPONSE"
  exit 1
fi

echo "Transcript retrieved successfully (${#TRANSCRIPT_TEXT} characters)"

# Step 3: Create JSON payload for summarization
# We need to properly escape the text for JSON
SUMMARY_PAYLOAD=$(jq -n \
  --arg text "$TRANSCRIPT_TEXT" \
  '{
    tool: "summarize_with_ollama",
    args: {
      text: $text,
      summary_length: "brief"
    }
  }')

# Step 4: Call the summarization tool
echo "Generating summary..."
SUMMARY_RESPONSE=$(curl -s -X POST http://localhost:8080/mcp/tools/invoke \
  -H "Content-Type: application/json" \
  -d "$SUMMARY_PAYLOAD")

# Step 5: Display the result
echo "Summary Result:"
echo "$SUMMARY_RESPONSE" | jq '.'
