import base64
import sys
import os

# usage: python make_base64.py path/to/audio.wav
input_audio = sys.argv[1]
output_txt = "audio_base64.txt"

if not os.path.exists(input_audio):
    raise FileNotFoundError(f"File not found: {input_audio}")

with open(input_audio, "rb") as f:
    encoded = base64.b64encode(f.read()).decode("utf-8")

with open(output_txt, "w", encoding="utf-8") as f:
    f.write(encoded)

print("✅ Base64 generated successfully")
print("📄 Saved to audio_base64.txt")


# import base64

# input_mp3 = "dataset/human/telugu/telugu1.mp3"   # your original mp3
# output_txt = "audio_base64.txt"

# with open(input_mp3, "rb") as f:
#     b64 = base64.b64encode(f.read()).decode("utf-8")

# with open(output_txt, "w", encoding="utf-8") as f:
#     f.write(b64)

# print("Base64 generated successfully")
