"""
ComfyUI Bridge for AI Assistant - Working Version
"""

import requests
import random
import time
import os

class ComfyUIBridge:
    def __init__(self, server_url="http://127.0.0.1:8188"):
        self.server_url = server_url
        
    def is_running(self):
        try:
            response = requests.get(f"{self.server_url}/system_stats", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def generate_image(self, prompt, steps=20, width=512, height=512):
        if not self.is_running():
            return None, "❌ ComfyUI not running. Start with: cd ~/ComfyUI && python main.py"
        
        workflow = {
            "3": {
                "class_type": "KSampler",
                "inputs": {
                    "seed": random.randint(1, 999999),
                    "steps": steps,
                    "cfg": 7.5,
                    "sampler_name": "euler",
                    "scheduler": "normal",
                    "denoise": 1,
                    "model": ["4", 0],
                    "positive": ["6", 0],
                    "negative": ["7", 0],
                    "latent_image": ["5", 0]
                }
            },
            "4": {
                "class_type": "CheckpointLoaderSimple",
                "inputs": {"ckpt_name": "v1-5-pruned-emaonly.safetensors"}
            },
            "5": {
                "class_type": "EmptyLatentImage",
                "inputs": {"width": width, "height": height, "batch_size": 1}
            },
            "6": {
                "class_type": "CLIPTextEncode",
                "inputs": {"text": prompt, "clip": ["4", 1]}
            },
            "7": {
                "class_type": "CLIPTextEncode",
                "inputs": {"text": "blurry, bad quality, distorted, ugly", "clip": ["4", 1]}
            },
            "8": {
                "class_type": "VAEDecode",
                "inputs": {"samples": ["3", 0], "vae": ["4", 2]}
            },
            "9": {
                "class_type": "SaveImage",
                "inputs": {"filename_prefix": "AI_Gen", "images": ["8", 0]}
            }
        }
        
        try:
            response = requests.post(f"{self.server_url}/prompt", json={"prompt": workflow}, timeout=30)
            if response.status_code == 200:
                return None, f"✅ Generating: '{prompt[:50]}...'\\n📁 Image will appear in ~/ComfyUI/output/"
            return None, f"❌ Error: {response.status_code}"
        except Exception as e:
            return None, f"❌ Error: {e}"

bridge = ComfyUIBridge()

def generate_image(prompt, **kwargs):
    return bridge.generate_image(prompt, **kwargs)

def is_available():
    return bridge.is_running()

print(f"✅ ComfyUI Bridge - Status: {'Connected' if is_available() else 'Disconnected'}")
