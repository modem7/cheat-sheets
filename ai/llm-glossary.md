# LLM Glossary
Short definitions of terms used across the AI sheets.

> **Verification:** conceptual definitions; no commands.

## Core Terms
TERM | MEANING
---|---
LLM | Large language model: a neural network that predicts the next token
Token | A chunk of text (a word, part of a word or punctuation); the unit of billing and limits. English averages roughly 4 characters per token `(approximate)`
Context window | The maximum tokens (prompt plus output) the model handles in one request
Prompt | The input text; split into system prompt (rules) and user messages
Completion | The model's output
Inference | Running a trained model to get output (as opposed to training)
Parameters | The learned weights; "7B" means seven billion
Embedding | A vector representing text meaning, used for search and clustering
Hallucination | A confident but false output

## Sampling
TERM | MEANING
---|---
Temperature | Randomness; low is focused, high is varied
Top-p (nucleus) | Sample only from the smallest set of tokens whose probability sums to p
Top-k | Sample only from the k most likely tokens
Max tokens | Cap on output length
Stop sequence | Text that ends generation
Seed | Fixes randomness where supported; not a guarantee of identical output

## Usage Patterns
TERM | MEANING
---|---
System prompt | Standing instructions for a conversation
Few-shot | Examples included in the prompt
Chain of thought / extended thinking | The model reasons step by step before answering
Tool use / function calling | The model requests that your code run a function and return the result
Structured output | Output constrained to a JSON schema
Agent | An LLM in a loop that calls tools until a goal is met
RAG | Retrieval-augmented generation: fetch relevant text and add it to the prompt
Prompt caching | Reusing a repeated prompt prefix at lower cost and latency
Batch API | Asynchronous bulk requests at reduced price
Fine-tuning | Further training on your data
LoRA | Small adapter weights for cheap fine-tuning
MCP | Model Context Protocol; see [MCP](mcp.md)
Prompt injection | Untrusted text that tries to override the model's instructions

## Running Models
TERM | MEANING
---|---
Open weights | Downloadable model weights; the licence may still restrict use
Quantisation | Lower-precision weights to save memory; see [quantisation](hugging-face.md#quantisation)
GGUF | Quantised single-file format for llama.cpp and Ollama
VRAM | GPU memory; the usual limit on model size
KV cache | Memory that grows with context length during generation
Offload | Placing some layers on the GPU and the rest on CPU
Tokens per second | Generation speed
MoE | Mixture of experts: only some parameters are active per token
Distillation | Training a small model to imitate a larger one

## See Also
- [Prompting and Context Engineering](prompting-patterns.md)
- [Hugging Face CLI and Model Formats](hugging-face.md)
- [AI](ai.md)
