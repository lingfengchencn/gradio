from pathlib import Path

import numpy as np
import torch
import gradio as gr
from torch import nn
import gdown 

url = 'https://drive.google.com/uc?id=1dsk2JNZLRDjC-0J4wIQX_FcVurPaXaAZ'
output = 'pytorch_model.bin'
gdown.download(url, output, quiet=False)

LABELS = Path('class_names.txt').read_text().splitlines()

model = nn.Sequential(
    nn.Conv2d(1, 32, 3, padding='same'),
    nn.ReLU(),
    nn.MaxPool2d(2),
    nn.Conv2d(32, 64, 3, padding='same'),
    nn.ReLU(),
    nn.MaxPool2d(2),
    nn.Conv2d(64, 128, 3, padding='same'),
    nn.ReLU(),
    nn.MaxPool2d(2),
    nn.Flatten(),
    nn.Linear(1152, 256),
    nn.ReLU(),
    nn.Linear(256, len(LABELS)),
)
state_dict = torch.load('pytorch_model.bin', map_location='cpu')
model.load_state_dict(state_dict, strict=False)
model.eval()

def predict(im):
    if im is None:
        return None
    im = np.asarray(im.resize((28, 28)))
        
    x = torch.tensor(im, dtype=torch.float32).unsqueeze(0).unsqueeze(0) / 255.

    with torch.no_grad():
        out = model(x)

    probabilities = torch.nn.functional.softmax(out[0], dim=0)

    values, indices = torch.topk(probabilities, 5)

    return {LABELS[i]: v.item() for i, v in zip(indices, values)}


interface = gr.Interface(predict, 
                         inputs=gr.Sketchpad(label="Draw Here", brush_radius=5, type="pil", shape=(120, 120)), 
                         outputs=gr.Label(label="Guess"), 
                         live=True)

interface.queue().launch()
