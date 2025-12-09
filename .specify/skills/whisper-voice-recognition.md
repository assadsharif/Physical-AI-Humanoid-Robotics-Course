# Skill: Whisper Voice Recognition & Transcription

**Description**: Integrating OpenAI Whisper for accurate speech-to-text transcription in the capstone project.

**Scope**:
- Audio file upload and processing
- Real-time voice streaming
- Multilingual transcription
- Timestamp and confidence scores
- Error handling and retries

**Key Technologies**:
- OpenAI Whisper API
- Python openai SDK
- Audio processing (librosa, soundfile)
- FastAPI for endpoint exposure

**Transcription Workflow**:
1. Student clicks microphone button
2. Browser records audio (WebRTC / MediaRecorder API)
3. Audio sent to FastAPI endpoint
4. Whisper processes audio → text
5. Text sent to LLM planner

**FastAPI Endpoint**:
```python
from fastapi import FastAPI, UploadFile, File
from openai import OpenAI

app = FastAPI()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.post("/api/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    audio_data = await file.read()

    with open("temp_audio.wav", "wb") as f:
        f.write(audio_data)

    with open("temp_audio.wav", "rb") as f:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=f,
            language="en"
        )

    return {"transcript": transcript.text}
```

**Browser Audio Recording** (JavaScript):
```javascript
const mediaRecorder = new MediaRecorder(stream);
const audioChunks = [];

mediaRecorder.ondataavailable = (event) => {
  audioChunks.push(event.data);
};

mediaRecorder.onstop = async () => {
  const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
  const formData = new FormData();
  formData.append('file', audioBlob);

  const response = await fetch('/api/transcribe', {
    method: 'POST',
    body: formData
  });

  const result = await response.json();
  console.log(result.transcript);
};
```

**Audio Formats Supported**:
- MP3, MP4, MPEG, MPGA, M4A, WAV, WEBM
- Max file size: 25 MB
- Recommended: 16-bit PCM WAV

**Transcription Quality**:
- Accuracy: > 95% (English)
- Supports 99 languages
- Timestamp accuracy: ± 100ms

**Performance**:
- Typical latency: 5-15 seconds (depending on audio length)
- Retry logic: 3 attempts on failure
- Timeout: 60 seconds per request

**Cost Optimization**:
- OpenAI pricing: $0.006 per minute of audio
- Batch processing if needed
- Cache transcripts to avoid re-processing

**Error Handling**:
```python
try:
    transcript = client.audio.transcriptions.create(...)
except openai.APIError as e:
    logger.error(f"Whisper API error: {e}")
    return {"error": "Transcription failed", "retry": True}
```

**Testing**:
- Mock Whisper API responses
- Test with various accents and audio quality
- Validate output format

**Owner**: Capstone VLA Agent

**Related**: capstone-vla-agent.md, fastapi-backend.md
