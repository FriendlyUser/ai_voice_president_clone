# Import gradio and other libraries
import gradio as gr
import torch
import torchaudio
import torch.nn as nn
import torch.nn.functional as F

from tortoise.api import TextToSpeech
from tortoise.utils.audio import load_audio, load_voice, load_voices

# Initialize the text-to-speech model
tts = TextToSpeech()

# Define a function that takes text and voice name as inputs and returns audio as output
def tts_function(text, voice_name):
  audio_folder = f"audio/{voice_name}"
  # Load the voice samples and conditioning latents from the voice folder
  voice_samples, conditioning_latents = load_voice(audio_folder)
  # reference_clips = [utils.audio.load_audio(p, 22050) for p in clips_paths]
  # Generate the audio with the preset mode "high_quality"
  gen = tts.tts_with_preset(text, voice_samples=voice_samples, conditioning_latents=conditioning_latents,
                            preset="high_quality")
  # Return the audio tensor as numpy array
  return gen.squeeze(0).cpu().numpy()

# Define the input components: a text box and a dropdown menu for voice name selection
text_input = gr.inputs.Textbox(lines=2, label="Text")
voice_input = gr.inputs.Dropdown(["trump"], label="Voice Name")

# Define the output component: an audio player
audio_output = gr.outputs.Audio(type="numpy", label="Audio")

# Create the gradio interface with title and description
iface = gr.Interface(fn=tts_function,
                     inputs=[text_input, voice_input],
                     outputs=audio_output,
                     title="Tortoise TTS Demo",
                     description="A demo of text-to-speech synthesis using tortoise-tts library.")

# Launch the interface in a new tab or inline mode (change False to True for inline mode)
iface.launch(share=True, inbrowser=False)