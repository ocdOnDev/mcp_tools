uvicorn app:app --host 0.0.0.0 --port 8080


curl -X POST http://localhost:8080/tools/get_system_metrics

curl -X POST http://localhost:8080/tools/extract_pdf_text \
  -H "Content-Type: application/json" \
  -d '{"file_path":"/home/user/sample.pdf"}'


  curl -X GET http://localhost:8080/tools/metadata



  uvicorn app:app2 --host 0.0.0.0 --port 8181 &

  curl -X GET http://localhost:8181/mcp/tools/metadata


  curl -X POST http://localhost:8080/tools/get_system_metrics \
  -H "Content-Type: application/json" \
  -d '{}'

  ps aux | grep uvicorn


  curl -X POST http://localhost:8181/mcp/tools/invoke \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "get_system_metrics",
    "args": {}
  }'


  curl -X GET http://localhost:8080/mcp/tools/metadata



  curl -X POST http://localhost:8080/mcp/tools/invoke \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "get_weather",
    "args": {
      "location": "Amsterdam"
    }
  }'

  the latest tool:
  # Start the server
python -m uvicorn app:app --reload

# Test via API
curl -X POST http://localhost:8080/mcp/tools/invoke \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "youtube_analyzer",
    "args": {"url": "https://www.youtube.com/watch?v=H3TI1JjPmtI"}
  }'

  # another model instead of ollama

  curl -X POST http://your-server:8080/tools/youtube_summary_anthropic \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=VIDEO_ID"}'