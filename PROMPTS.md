\# Aptivue — Vibe-Coding Prompt Log



\## Project



Aptivue is an adaptive technical interview agent designed to conduct

role-aware technical interviews, adapt question difficulty based on

candidate responses, and provide structured interview feedback.



\## Development Prompts / Instructions



\### 1. Project Planning

\- Build an AI-powered technical interview agent.

\- Create a clean, professional interview experience with candidate

&#x20; selection, interview questions, answer submission, and final feedback.

\- Make the interview adaptive rather than a fixed questionnaire.



\### 2. Interview Agent

\- Design the interview agent around technical topics, difficulty levels,

&#x20; candidate role, experience, and previous answers.

\- Select the next topic based on curriculum coverage and interview state.

\- Increase or decrease difficulty based on the candidate's answer quality.

\- Keep track of questions already asked during the session.



\### 3. Question Generation

\- Generate one question at a time.

\- Questions should be relevant to the candidate's role and experience.

\- Follow-up questions should use the previous conversation when possible.

\- Avoid repeating questions already asked in the same interview.



\### 4. Fallback Interview System

\- Provide a deterministic fallback question bank when the LLM is

&#x20; unavailable.

\- Include multiple questions for each topic and difficulty level.

\- Randomly select unused questions so separate interviews do not always

&#x20; follow the exact same question wording.

\- Prevent duplicate questions within a single session.



\### 5. Evaluation and Feedback

\- Evaluate candidate answers for relevance, correctness, reasoning,

&#x20; and completeness.

\- Track topic-level performance and knowledge gaps.

\- Generate a final interview summary containing strengths, knowledge

&#x20; gaps, and recommended next steps.



\### 6. UI / Frontend

\- Build a clean technical interview interface.

\- Display interviewer and candidate messages differently.

\- Provide an answer input area and send action.

\- Show an analyzing/loading state while waiting for the backend.

\- Display the final interview feedback after completion.



\### 7. Deployment

\- Deploy the FastAPI backend using Render.

\- Deploy the Vite frontend using Vercel.

\- Keep API credentials in environment variables rather than source code.

\- Verify the production frontend can communicate with the backend.



\### 8. Debugging / Iteration

\- Fix deployment issues involving Python dependencies.

\- Fix frontend CSS/build errors.

\- Fix accidental tracking of local environments and dependencies.

\- Fix repetitive fallback questions by expanding the question bank and

&#x20; tracking previously asked questions.

\- Verify the application with production builds before submission.



\## Development Approach



The project was developed iteratively with AI-assisted coding:

planning → implementation → local testing → debugging → deployment →

production testing → refinement.



The prompts above represent the main development instructions and

requirements used while building and refining Aptivue.

