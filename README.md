# 🧠 Aptivue

### AI-Powered Adaptive Technical Interview Agent

Aptivue is an **AI-powered technical interview platform** that conducts role-aware interviews, adapts questions based on candidate performance, and generates structured feedback at the end of the interview.

Instead of following a fixed questionnaire, Aptivue maintains an interview state and dynamically selects **topics, difficulty levels, follow-up questions, and evaluation criteria** based on the candidate's responses.

---

## 🚀 Live Demo

🌐 **Live Application:**  
https://aptivue.vercel.app

📦 **Source Code:**  
https://github.com/Dixa08/Aptivue

🤖 **AI Usage Log:**  
https://github.com/Dixa08/Aptivue/blob/main/PROMPTS.md

---

## 🎯 Problem

Traditional technical interviews often rely on:

- Fixed question lists
- The same difficulty for every candidate
- Limited adaptation to candidate responses
- Manual evaluation
- Inconsistent interview feedback

This makes it difficult to conduct interviews that are **personalized, consistent, and scalable**.

### Aptivue solves this by providing an adaptive interview experience.

The system considers:

- Candidate role
- Experience level
- Technical topics
- Previous answers
- Answer quality
- Current topic coverage
- Interview difficulty

and uses these signals to determine what should be asked next.

---

## ✨ Key Features

### 🎯 Role-Aware Interviews

Interviews are tailored according to the candidate's:

- Job role
- Experience
- Technical curriculum

---

### 🧠 Adaptive Questioning

The interview agent dynamically adjusts the interview based on candidate performance.

A strong answer can lead to a deeper question, while a weak answer can trigger a simpler conceptual or application-based question.

```text
Candidate Answer
       ↓
Answer Evaluation
       ↓
Update Interview State
       ↓
Determine Topic
       ↓
Determine Difficulty
       ↓
Generate Next Question
