# 🛡️ Sovereign AI Workbench

### Secure • Local • Private • Offline AI Assistant

Sovereign AI Workbench is a **fully local AI-powered workspace** designed for organizations that handle sensitive and confidential information.

The system enables users to interact with multiple local AI models, analyze documents and images, generate code, execute programs inside isolated Docker containers, perform Retrieval-Augmented Generation (RAG), and generate office documents — **without sending sensitive data to external cloud AI services**.

Built as a project for **Smart India Hackathon (SIH) 2026**.

---

# 🚀 Features

## 🤖 Local Multi-Model AI Routing

The system automatically selects the appropriate local model depending on the task.

| Task | Model |
|---|---|
| General conversation | `qwen2.5:3b` |
| Programming and debugging | `qwen2.5-coder:3b` |
| Images, PDFs and OCR | `qwen2.5vl:7b` |

Examples:

```text
"What is Retrieval Augmented Generation?"
→ General Model

"Write a Java program for Binary Search"
→ Coding Model

"Analyze this image"
→ Vision Model
