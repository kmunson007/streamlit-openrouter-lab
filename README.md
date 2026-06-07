# Streamlit OpenRouter Lab

A small Streamlit AI assistant that uses OpenRouter auto-routing through the OpenAI-compatible Python SDK.

## What It Does

This app demonstrates how to build a lightweight local AI workbench with:

- Streamlit web UI
- OpenRouter integration
- `openrouter/auto` model routing
- Cost/quality tradeoff slider
- Copy buttons for the question and response
- Scrollable response box for long answers
- Visibility into the actual model selected by OpenRouter

## Architecture

```text
User
  ↓
Streamlit UI
  ↓
OpenAI Python SDK
  ↓
OpenRouter API endpoint
  ↓
OpenRouter auto-router
  ↓
Selected model provider
  ↓
Model response

