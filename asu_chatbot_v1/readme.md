# PIASN Hackathon

A writing‑support chatbot designed for Arizona State University (ASU) students. It combines web scraping, Retrieval‑Augmented Generation (RAG) and a simple GUI/CLI to help with citations, proofreading, library info and more.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
  - [Command‑Line Interface](#command‑line-interface)
  - [Graphical Interface](#graphical-interface)
  - [Built‑in Chat Commands](#built‑in-chat-commands)
- [Refreshing the Knowledge Base](#refreshing-the-knowledge-base)
- [Extending the Scraper](#extending-the-scraper)
- [Project Structure](#project-structure)
- [Dependencies](#dependencies)
- [Contributing](#contributing)
- [License](#license)

## Overview

This project implements the **ASU Writing Support Chatbot**, a Python application that:  
1. Scrapes ASU writing‑center web pages for up‑to‑date guidance.  
2. Builds a local vector index over those pages.  
3. Uses a RetrievalQA chain (LangChain + Ollama LLM + FAISS) to answer student queries.  
4. Offers both a CLI (`main.py`) and a GUI (`UI.py`) for interaction.

## Features

- **Web Scraper** (`web_scraper.py`):  
  Fetches raw text from ASU tutoring & library guides.
- **RAG Engine** (`rag_engine.py`):  
  ‑ Builds/loads a FAISS index of scraped docs.  
  ‑ Wraps an Ollama “llama3” model in a RetrievalQA chain with a custom prompt.
- **Chat Utilities** (`bot_utils.py`):  
  Language detection, citation formatting, grammar feedback, paraphrasing, library hours, map links, assignment unpacking, resource triage, and citation‑audit for DOCX uploads.
- **Router** (`router.py`):  
  Directs free‑text or slash‑command inputs to the right handler.
- **Configuration** (`config.py`):  
  Central place to set your `OPENAI_API_KEY` (if needed for some utilities).
- **Interfaces**:  
  ‑ **CLI**: Type `python main.py` for a terminal chat.  
  ‑ **GUI**: Run `python UI.py` for a PyQt5 chat window.

## Prerequisites

- Python 3.8+  
- An OpenAI API key (for certain `bot_utils` functions)  
- `ollama` installed & running if you want to use the local Ollama LLM  
- Internet access to fetch ASU pages

## Installation

1. **Clone the repo**  
   ```bash
   git clone https://github.com/torahoang/PIASN-hackathon.git
   cd PIASN-hackathon/asu_chatbot_v1
