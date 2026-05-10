---
title: SHL Talent Assessment Agent
emoji: 👁
colorFrom: pink
colorTo: yellow
sdk: docker
app_port: 7860
pinned: false
---

# SHL Assessment Agent

A conversational AI agent that helps hiring managers find the right
SHL assessments through dialogue.

## What it does

- Ask it "I need to hire a Java developer" and it recommends assessments
- It asks ONE clarifying question if your request is too vague
- Update your requirements mid-conversation and it updates the list
- Ask it to compare two assessments and it answers from real catalog data
- It refuses off-topic questions (salary, legal, etc.)

## Live API

Base URL: https://deepak041-shl-talent-assessment-agent.hf.space

### Health check
GET /health
Returns: {"status": "ok"}

### Chat
POST /chat
Body:
{
  "messages": [
    {"role": "user", "content": "I am hiring a senior Java developer"}
  ]
}

Response:
{
  "reply": "Here are assessments for a senior Java developer.",
  "recommendations": [
    {
      "name": "Core Java (Advanced Level) (New)",
      "url": "https://www.shl.com/products/product-catalog/view/core-java-advanced-level-new/",
      "test_type": "K"
    }
  ],
  "end_of_conversation": false
}

## Run locally

### 1. Clone the repo
```bash
git clone https://huggingface.co/spaces/Deepak041/SHL-Talent-Assessment-Agent
cd SHL-Talent-Assessment-Agent
```

### 2. Create virtual environment
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Add your API key
Create a `.env` file: