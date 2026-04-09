"""
Video Analysis Module for AI Toolkit
Complete video understanding with visual + audio + OCR
Supports Short, Medium, and Detailed summaries
"""

import cv2
import tempfile
import os
import subprocess
import numpy as np
try:
    from .core import set_response
    from .image import analyze_image
    from .faster_whisper_stt import transcribe
except ImportError:
    from core import set_response
    from image import analyze_image
    from faster_whisper_stt import transcribe

def extract_video_metadata(video_path):
    """Extract basic video information"""
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps if fps > 0 else 0
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()
    return {
        "fps": fps,
        "duration": duration,
        "frames": total_frames,
        "resolution": f"{width}x{height}"
    }

def adaptive_frame_count(duration):
    """Determine number of frames based on video duration"""
    if duration < 30:  # Less than 30 seconds
        return 6
    elif duration < 120:  # Less than 2 minutes
        return 10
    elif duration < 600:  # Less than 10 minutes
        return 15
    else:  # Longer videos
        return 20

def extract_audio_from_video(video_path):
    """Extract audio from video and transcribe with Whisper"""
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        audio_path = f.name

    try:
        subprocess.run([
            'ffmpeg', '-i', video_path, 
            '-q:a', '0', '-map', 'a', 
            audio_path, '-y'
        ], capture_output=True, check=True)

        text = transcribe(audio_path, language="en")
        os.unlink(audio_path)
        return text if text else "No speech detected"
    except:
        return "No audio track found"

def extract_video_frames(video_path, num_frames=None):
    """Extract key frames from video"""
    cap = cv2.VideoCapture(video_path)
    duration = cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS)

    if num_frames is None:
        num_frames = adaptive_frame_count(duration)

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_indices = [int(i * total_frames / num_frames) for i in range(num_frames)]

    frames = []
    for idx in frame_indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ret, frame = cap.read()
        if ret:
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
                cv2.imwrite(f.name, frame)
                frames.append({
                    "path": f.name,
                    "timestamp": idx / cap.get(cv2.CAP_PROP_FPS)
                })
    cap.release()
    return frames

def analyze_frames_with_bakllava(frames, max_frames=8):
    """Analyze frames using BakLLaVA"""
    descriptions = []
    step = max(1, len(frames) // max_frames)
    selected_frames = frames[::step][:max_frames]

    for i, frame in enumerate(selected_frames):
        prompt = """Describe what you see in this frame. Include:
        - Main objects/subjects
        - Their position (left, center, right, top, bottom)
        - Any action or movement implied
        - People, animals, or vehicles visible
        Keep it concise."""

        description = analyze_image(frame["path"], prompt)
        descriptions.append({
            "timestamp": frame["timestamp"],
            "description": description
        })
        os.unlink(frame["path"])

    return descriptions

def extract_onscreen_text(video_path, interval_seconds=2):
    """Extract text from video frames using OCR"""
    try:
        import pytesseract
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_interval = int(fps * interval_seconds)
        frame_count = 0
        all_text = []

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            if frame_count % frame_interval == 0:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                text = pytesseract.image_to_string(gray)
                if text.strip():
                    all_text.append(text.strip())
            frame_count += 1

        cap.release()
        return "\n".join(set(all_text)) if all_text else "No text detected"
    except ImportError:
        return "OCR not available (install pytesseract)"
    except Exception as e:
        return f"OCR error: {e}"

def analyze_video(video_path, summary_type="medium"):
    """
    Complete video analysis with three summary levels

    summary_type options:
    - "short": 2-3 sentence overview
    - "medium": 1-2 paragraph detailed summary
    - "detailed": Comprehensive analysis with timestamps and bullet points
    """
    print("="*50)
    print(f"🎬 Analyzing video: {os.path.basename(video_path)}")
    print(f"📊 Summary type: {summary_type.upper()}")
    print("="*50)

    # Extract metadata
    metadata = extract_video_metadata(video_path)
    print(f"📹 Duration: {metadata['duration']:.1f}s | Resolution: {metadata['resolution']}")

    # Extract audio
    print("🎤 Transcribing audio...")
    audio_text = extract_audio_from_video(video_path)

    # Extract and analyze frames
    print("🖼️ Analyzing frames...")
    frames = extract_video_frames(video_path)
    visual_analysis = analyze_frames_with_bakllava(frames, max_frames=8)

    # Extract onscreen text
    print("📝 Extracting onscreen text...")
    onscreen_text = extract_onscreen_text(video_path)

    # Build visual summary
    visual_summary = "\n".join([f"At {v['timestamp']:.1f}s: {v['description']}" for v in visual_analysis])

    # Choose prompt based on summary type
    if summary_type == "short":
        prompt = f"""Based on this video analysis, provide a VERY CONCISE summary (2-3 sentences only).

VISUAL: {visual_summary}
AUDIO: {audio_text if audio_text else 'No audio'}
TEXT: {onscreen_text if onscreen_text != 'No text detected' else 'No text'}

Give a brief 2-3 sentence overview of what happens in this video."""

    elif summary_type == "medium":
        prompt = f"""Based on this video analysis, provide a DETAILED SUMMARY (1-2 paragraphs).

VISUAL (frame by frame):
{visual_summary}

AUDIO TRANSCRIPT:
{audio_text if audio_text else "No audio detected"}

ONSCREEN TEXT:
{onscreen_text if onscreen_text != 'No text detected' else "No text detected"}

Provide a clear, natural 1-2 paragraph summary covering:
- What is visually happening
- Any speech or important sounds
- Any text that appears on screen"""

    else:  # detailed
        prompt = f"""Based on this video analysis, provide a COMPREHENSIVE DETAILED ANALYSIS.

VIDEO METADATA:
- Duration: {metadata['duration']:.1f} seconds
- Resolution: {metadata['resolution']}
- FPS: {metadata['fps']:.1f}

FRAME-BY-FRAME VISUAL ANALYSIS:
{visual_summary}

AUDIO TRANSCRIPT:
{audio_text if audio_text else "No audio detected"}

ONSCREEN TEXT DETECTED:
{onscreen_text if onscreen_text != 'No text detected' else "No text detected"}

Provide a comprehensive analysis including:
1. TIMELINE of key events (with approximate timestamps)
2. VISUAL details (objects, people, actions, positions)
3. AUDIO content (speech, sounds, music)
4. TEXT overlays detected
5. OVERALL narrative or purpose of the video

Format with bullet points and clear sections."""

    final_summary = set_response(prompt)

    return {
        "metadata": metadata,
        "audio": audio_text,
        "visual_frames": visual_analysis,
        "onscreen_text": onscreen_text,
        "summary": final_summary,
        "summary_type": summary_type
    }

def analyze_video_short(video_path):
    """Quick 2-3 sentence summary"""
    return analyze_video(video_path, summary_type="short")

def analyze_video_medium(video_path):
    """Standard 1-2 paragraph summary"""
    return analyze_video(video_path, summary_type="medium")

def analyze_video_detailed(video_path):
    """Comprehensive analysis with timestamps and details"""
    return analyze_video(video_path, summary_type="detailed")

def print_video_analysis(result):
    """Pretty print video analysis results"""
    print("\n" + "="*60)
    print(f"📹 VIDEO ANALYSIS ({result['summary_type'].upper()})")
    print("="*60)

    print(f"\n📊 METADATA:")
    print(f"   Duration: {result['metadata']['duration']:.1f} seconds")
    print(f"   Resolution: {result['metadata']['resolution']}")

    print(f"\n🎤 AUDIO TRANSCRIPT:")
    print(f"   {result['audio']}")

    print(f"\n📝 ONSCREEN TEXT:")
    print(f"   {result['onscreen_text']}")

    print("\n" + "="*60)
    print("📝 SUMMARY")
    print("="*60)
    print(result['summary'])

    return result

print("✅ Video Analysis Module loaded!")
print("   Functions: analyze_video_short(), analyze_video_medium(), analyze_video_detailed()")
