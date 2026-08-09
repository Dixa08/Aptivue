# 🧠 Aptivue

### AI-Powered Adaptive Technical Interview Agent

Aptivue conducts **role-aware technical interviews**, adapts questions based on candidate responses, and generates structured interview feedback.

---

## 🎯 Problem

Traditional technical interviews often rely on fixed question lists and provide the same interview experience to every candidate.

**Aptivue introduces an adaptive interview flow** where the next question is influenced by:

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
  <img src="./doc/candidate-selection.png" width="850" alt="Aptivue Candidate Setup">
</p>

---

## 💬 Adaptive Technical Interview

<p align="center">
  <img src="./doc/interview.png" width="850" alt="Aptivue Adaptive Technical Interview">
</p>

---

## 📊 Interview Feedback

<p align="center">
  <img src="./doc/feedback.png" width="850" alt="Aptivue Interview Feedback">
</p>



---

# ✨ Key Features

| Feature | Description |
|---|---|
| 🎯 **Role-Aware** | Interview questions are aligned with candidate role and experience |
| 🧠 **Adaptive** | Difficulty changes based on candidate performance |
| 🔄 **Non-Repeating** | Previously asked questions are tracked |
| 📚 **Multi-Topic** | Supports multiple technical domains |
| 🤖 **AI-Powered** | Uses LLM-based question generation |
| 🛡️ **Fallback System** | Continues with deterministic questions if LLM generation fails |
| 📊 **Feedback** | Generates strengths, knowledge gaps, and next steps |

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
              │  Claude + Fallback   │
              │    Question Bank     │
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


```
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# 📁 Project Structure

```text
Aptivue/
│
├── 📁 frontend/
│   ├── 📁 src/
│   │   ├── 📁 components/
│   │   ├── 📁 data/
│   │   ├── 📁 lib/
│   │   ├── 📁 types/
│   │   ├── 📄 App.tsx
│   │   └── 🎨 index.css
│   │
│   ├── 📄 package.json
│   ├── 📄 vite.config.ts
│   └── 📄 tsconfig.json
│
├── 📁 backend/
│   ├── 🐍 interview_agent.py
│   ├── 🐍 main.py
│   └── 📄 requirements.txt
│
├── 📁 doc/
│   ├── 🖼️ candidate-selection.png
│   ├── 🖼️ interview.png
│   └── 🖼️ feedback.png
│
├── 🤖 PROMPTS.md
├── 📖 README.md
└── 🚫 .gitignore

```

# 🛠️ Technology Stack

### 🎨 Frontend

<p align="center">
  <img src="https://skillicons.dev/icons?i=react,ts,vite,tailwind" alt="Frontend Technologies">
</p>

<p align="center">
  <b>React</b> • <b>TypeScript</b> • <b>Vite</b> • <b>Tailwind CSS</b>
</p>

---

### ⚙️ Backend

<p align="center">
  <img src="https://skillicons.dev/icons?i=python,fastapi" alt="Backend Technologies">
</p>

<p align="center">
  <b>Python</b> • <b>FastAPI</b> • <b>Pydantic</b>
</p>

---

### 🤖 AI

<p align="center">

🤖 <b>Anthropic Claude API</b>

</p>

<p align="center">
Adaptive Question Generation • Answer Evaluation • Interview Orchestration
</p>

---

### 🚀 Deployment & Development

<p align="center">
  <img src="https://skillicons.dev/icons?i=vercel,git,github" alt="Deployment and Development Technologies">
</p>

<p align="center">
  <b>Vercel</b> • <b>Render</b> • <b>Git</b> • <b>GitHub</b>
</p>
