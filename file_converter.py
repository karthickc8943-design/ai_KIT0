"""
JARVIS File Converter Module
Supports Images, Documents, and Spreadsheets
"""
import os
import subprocess
from PIL import Image
import pandas as pd

def convert_file(input_path, target_format):
    """
    Main entry point for file conversion.
    Returns the path to the converted file or an error message.
    """
    if not os.path.exists(input_path):
        return f"Error: File not found at {input_path}"
    
    filename = os.path.basename(input_path)
    base_name, ext = os.path.splitext(filename)
    ext = ext.lower()
    target_format = target_format.lower().replace('.', '')
    
    # Define output path
    output_dir = os.path.dirname(input_path)
    output_path = os.path.join(output_dir, f"{base_name}.{target_format}")
    
    # 1. Image formats
    image_formats = ['jpg', 'jpeg', 'png', 'webp', 'bmp', 'tiff', 'gif']
    # 2. Video formats
    video_formats = ['mp4', 'mkv', 'mov', 'avi', 'webm', 'flv']
    # 3. Audio formats
    audio_formats = ['mp3', 'wav', 'ogg', 'm4a', 'flac', 'aac']
    
    ext_clean = ext.replace('.', '')

    # --- IMAGE CONVERSION ---
    if ext_clean in image_formats and target_format in image_formats:
        try:
            img = Image.open(input_path)
            if target_format in ['jpg', 'jpeg'] and img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            img.save(output_path)
            return output_path
        except Exception as e:
            return f"Image Error: {e}"

    # --- MEDIA CONVERSION (Video/Audio) ---
    is_video_src = ext_clean in video_formats
    is_audio_src = ext_clean in audio_formats
    is_video_dst = target_format in video_formats
    is_audio_dst = target_format in audio_formats

    if (is_video_src or is_audio_src) and (is_video_dst or is_audio_dst):
        try:
            print(f"🎬 Transcoding Media: {filename} -> {target_format}")
            
            # --- START HARDWARE ACCELERATION LOGIC ---
            # Using VA-API on Linux for better stability than QSV
            hw_encoder = 'libx264'
            extra_flags = ['-preset', 'ultrafast', '-crf', '23', '-pix_fmt', 'yuv420p']
            
            if is_video_dst:
                if target_format == 'mp4':
                    # Priority 1: VA-API (Intel/AMD GPU)
                    hw_encoder = 'h264_vaapi'
                    extra_flags = ['-vaapi_device', '/dev/dri/renderD128', '-vf', 'format=nv12,hwupload', '-qp', '24']
                elif target_format == 'mkv':
                    hw_encoder = 'h264_vaapi'
                    extra_flags = ['-vaapi_device', '/dev/dri/renderD128', '-vf', 'format=nv12,hwupload', '-qp', '24']
            # --- END HARDWARE ACCELERATION LOGIC ---

            cmd = ['ffmpeg', '-y', '-hwaccel', 'vaapi', '-hwaccel_device', '/dev/dri/renderD128', '-hwaccel_output_format', 'vaapi', '-i', input_path]
            
            # 1. Handle Audio Extraction (Video to Audio)
            if is_video_src and is_audio_dst:
                cmd = ['ffmpeg', '-y', '-i', input_path] # Reset cmd for audio-only
                cmd.extend(['-vn', '-acodec', 'libmp3lame' if target_format == 'mp3' else 'pcm_s16le'])
            
            # 2. Handle Video-to-Video Speed Optimization
            elif is_video_src and is_video_dst:
                cmd.extend(['-c:v', hw_encoder])
                cmd.extend(extra_flags)

            # Global optimization: Use all CPU cores for non-HW parts
            cmd.extend(['-threads', '0'])
            
            cmd.append(output_path)
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # If VA-API failed (often returns 0 or small file), retry with software as ultimate fallback
            if not os.path.exists(output_path) or os.path.getsize(output_path) < 1000:
                print(f"⚠️ HW Encoding failed or produced empty file, falling back to software...")
                if os.path.exists(output_path): os.remove(output_path)
                cmd_sw = ['ffmpeg', '-y', '-i', input_path, '-preset', 'ultrafast', '-crf', '23', '-pix_fmt', 'yuv420p', '-threads', '0', output_path]
                subprocess.run(cmd_sw, capture_output=True, text=True)
                
            if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
                return output_path
                
            return f"Media Error: {result.stderr}"
        except Exception as e:
            return f"Media Process Error: {e}"

    # --- DOCUMENT CONVERSION ---
    doc_extensions = ['.docx', '.doc', '.pptx', '.ppt', '.odt', '.rtf', '.txt', '.md']
    if ext in doc_extensions or target_format in ['pdf', 'html', 'txt', 'docx']:
        try:
            print(f"📄 Converting Document: {filename} -> {target_format}")
            # LibreOffice handles most doc -> pdf/html/txt
            result = subprocess.run([
                'libreoffice', '--headless', 
                '--convert-to', target_format, 
                '--outdir', output_dir, 
                input_path
            ], capture_output=True, text=True)
            
            if os.path.exists(output_path):
                return output_path
            return f"Document Error: {result.stderr}"
        except Exception as e:
            return f"Document Process Error: {e}"

    # --- SPREADSHEET CONVERSION ---

    # 3. Spreadsheet Conversion (using Pandas)
    if ext in ['.csv', '.xlsx', '.xls'] and target_format in ['csv', 'xlsx']:
        try:
            if ext == '.csv':
                df = pd.read_csv(input_path)
            else:
                df = pd.read_excel(input_path)
            
            if target_format == 'csv':
                df.to_csv(output_path, index=False)
            else:
                df.to_excel(output_path, index=False)
            return output_path
        except Exception as e:
            return f"Spreadsheet Error: {e}"

    # 4. Image to PDF
    if ext.replace('.', '') in image_formats and target_format == 'pdf':
        try:
            img = Image.open(input_path)
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            img.save(output_path, "PDF", resolution=100.0)
            return output_path
        except Exception as e:
            return f"Image-to-PDF Error: {e}"

    return f"Conversion from {ext} to {target_format} is not supported yet, sir."

def compress_file(input_path, intensity):
    """
    Compress file size based on intensity (0-100).
    Higher intensity = smaller file size (lower quality).
    """
    if not os.path.exists(input_path):
        return f"Error: File not found"
    
    filename = os.path.basename(input_path)
    base_name, ext = os.path.splitext(filename)
    ext = ext.lower()
    
    output_dir = os.path.dirname(input_path)
    output_path = os.path.join(output_dir, f"{base_name}_compressed{ext}")
    
    # Image formats
    image_formats = ['.jpg', '.jpeg', '.png', '.webp']
    # Video formats
    video_formats = ['.mp4', '.mkv', '.mov', '.avi', '.webm']
    
    try:
        # 1. IMAGE COMPRESSION
        if ext in image_formats:
            img = Image.open(input_path)
            # Map intensity 0-100 to quality 95-5
            quality = max(5, 95 - intensity)
            if ext in ['.jpg', '.jpeg'] and img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            img.save(output_path, quality=quality, optimize=True)
            return output_path

        # 2. VIDEO COMPRESSION (Using FFmpeg)
        if ext in video_formats:
            # We standardize on MP4 for compression as it's best for size/compatibility
            output_path = os.path.join(output_dir, f"{base_name}_compressed.mp4")
            if os.path.exists(output_path): os.remove(output_path)
            
            # Map intensity 0-100 to quality
            # libx264 uses CRF (18-51, lower is better)
            # h264_vaapi uses -qp (18-51, lower is better)
            q_val = 18 + int((intensity / 100) * (51 - 18))
            
            print(f"🎬 Compressing Video: {filename} -> MP4 (Target Quality: {q_val})")
            
            # --- HW ATTEMPT (VA-API) ---
            hw_success = False
            if os.path.exists('/dev/dri/renderD128'):
                try:
                    cmd_hw = [
                        'ffmpeg', '-y', '-hwaccel', 'vaapi', '-hwaccel_device', '/dev/dri/renderD128',
                        '-hwaccel_output_format', 'vaapi', '-i', input_path,
                        '-c:v', 'h264_vaapi', '-qp', str(q_val),
                        '-vf', 'format=nv12,hwupload', '-threads', '0',
                        output_path
                    ]
                    subprocess.run(cmd_hw, capture_output=True, text=True)
                    if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
                        hw_success = True
                except:
                    pass

            # --- SOFTWARE FALLBACK ---
            if not hw_success:
                print("⚠️ Hardware acceleration unavailable or failed, utilizing optimized CPU mode...")
                if os.path.exists(output_path): os.remove(output_path)
                cmd_sw = [
                    'ffmpeg', '-y', '-i', input_path,
                    '-c:v', 'libx264', '-crf', str(q_val),
                    '-preset', 'ultrafast', '-pix_fmt', 'yuv420p', '-threads', '0',
                    output_path
                ]
                subprocess.run(cmd_sw, capture_output=True, text=True)

            if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
                return output_path
            return "Video compression failed"

        # 3. PDF COMPRESSION (Using Ghostscript)
        if ext == '.pdf':
            # Map intensity to GS settings
            # 0-33: /printer, 34-66: /ebook, 67-100: /screen
            if intensity < 33: gs_setting = '/printer'
            elif intensity < 66: gs_setting = '/ebook'
            else: gs_setting = '/screen'
            
            print(f"📑 Compressing PDF: {filename} with preset {gs_setting}")
            cmd = [
                'gs', '-sDEVICE=pdfwrite', '-dCompatibilityLevel=1.4',
                f'-dPDFSETTINGS={gs_setting}', '-dNOPAUSE', '-dQUIET', '-dBATCH',
                f'-sOutputFile={output_path}', input_path
            ]
            subprocess.run(cmd, capture_output=True, text=True)
            if os.path.exists(output_path): return output_path
            return "PDF compression failed"

    except Exception as e:
        return f"Compression Error: {e}"

    return f"Compression for {ext} not supported yet, sir."

def get_file_size_info(path):
    """Helper to return human-readable file size"""
    if not os.path.exists(path): return "Unknown"
    size = os.path.getsize(path) / 1024
    if size < 1024: return f"{size:.1f} KB"
    return f"{size/1024:.1f} MB"

if __name__ == "__main__":
    # Quick test
    import sys
    if len(sys.argv) > 2:
        # If 3rd arg is 'compress', then compress, else convert
        if len(sys.argv) > 3 and sys.argv[3] == "compress":
            print(compress_file(sys.argv[1], int(sys.argv[2])))
        else:
            print(convert_file(sys.argv[1], sys.argv[2]))
