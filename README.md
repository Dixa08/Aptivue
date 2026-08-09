# 🧠 Aptivue

<p align="center">
  <strong>AI-Powered Adaptive Technical Interview Agent</strong>
</p>

<p align="center">
  Aptivue conducts role-aware technical interviews, adapts questions based on
  candidate responses, and generates structured interview feedback.
</p>

<p align="center">
  <a href="https://aptivue.vercel.app">🌐 Live Demo</a> •
  <a href="https://github.com/Dixa08/Aptivue">💻 GitHub</a> •
  <a href="https://github.com/Dixa08/Aptivue/blob/main/PROMPTS.md">🤖 AI Usage Log</a>
</p>

---

## 🎯 Problem

Traditional technical interviews often rely on fixed question lists and
provide the same interview experience to every candidate.

**Aptivue introduces an adaptive interview flow** where the next question is
influenced by:

- Candidate role
- Experience level
- Technical topic
- Previous answers
- Answer quality
- Current topic coverage
- Difficulty level

---

# 📸 Product Preview

## 👤 Candidate Setup

<p align="center">
  <img src="doc/YOUR-CANDIDATE-SCREENSHOT.png" width="850">
</p>

---

## 💬 Adaptive Technical Interview

<p align="center">
  <img src="doc/YOUR-INTERVIEW-SCREENSHOT.png" width="850">
</p>

---

## 📊 Interview Feedback

<p align="center">
  <img src="doc/YOUR-FEEDBACK-SCREENSHOT.png" width="850">
</p>

---

# ✨ Key Features

| Feature | Description |
|---|---|
| 🎯 Role-Aware | Interview questions are aligned with candidate role and experience |
| 🧠 Adaptive | Difficulty changes based on candidate performance |
| 🔄 Non-Repeating | Previously asked questions are tracked |
| 📚 Multi-Topic | Supports multiple technical domains |
| 🤖 AI-Powered | Uses LLM-based question generation |
| 🛡️ Fallback System | Continues with deterministic questions if LLM generation fails |
| 📊 Feedback | Generates strengths, knowledge gaps and next steps |

---

# 🔄 How Aptivue Works

```text
                    👤 Candidate
                         │
                         ▼
                ┌─────────────────┐
                │ Candidate Setup │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │ Interview State │
                └────────┬────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │ Topic + Difficulty   │
              │     Selection        │
              └──────────┬───────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │   Question Generator │
              │     Claude +         │
              │  Fallback Question   │
              │       Bank           │
              └──────────┬───────────┘
                         │
                         ▼
                💬 Interview Question
                         │
                         ▼
                   👤 Answer
                         │
                         ▼
              ┌──────────────────────┐
              │   Answer Evaluation  │
              └──────────┬───────────┘
                         │
                         ▼
                🔄 Update State
                         │
                         ▼
                 Next Question
                         │
                         ▼
                  🏁 Completion
                         │
                         ▼
                📊 Final Feedback
