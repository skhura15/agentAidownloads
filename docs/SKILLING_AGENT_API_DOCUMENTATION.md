# Skilling Agent Backend API Documentation

## Contact Center Knowledge-Based Coach - UI Integration Guide

**Version:** 1.0.0  
**Last Updated:** February 2, 2026

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Getting Started](#getting-started)
4. [Authentication](#authentication)
5. [API Base URL](#api-base-url)
6. [REST API Endpoints](#rest-api-endpoints)
   - [List Available Cases](#1-list-available-cases)
   - [Start Simulation Session](#2-start-simulation-session)
   - [Send Chat Message](#3-send-chat-message)
   - [Ask Coach for Help](#4-ask-coach-for-help)
   - [Get Session Status](#5-get-session-status)
   - [End Simulation](#6-end-simulation)
   - [Cleanup Session](#7-cleanup-session)
7. [Data Models](#data-models)
8. [WebSocket Integration](#websocket-integration)
9. [Typical UI Flow](#typical-ui-flow)
10. [Error Handling](#error-handling)
11. [Code Examples](#code-examples)

---

## Overview

The Skilling Agent is a **Contact Center Knowledge-Based Coach** that provides interactive training simulations for customer support agents. It uses a unique "Fourth Wall" architecture where:

- **CustomerSim Agent** - Roleplays as the customer (trainee sees this in the main chat)
- **ShadowCoach Agent** - Silently observes and provides coaching hints (shown in a sidebar)
- **Orchestrator** - Manages the simulation, routing messages appropriately

The trainee (user) practices handling customer scenarios while receiving real-time coaching guidance.

---

## Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                         UI Application                            │
│  ┌────────────────────┐              ┌─────────────────────────┐ │
│  │     Main Chat      │              │    Coach Sidebar        │ │
│  │  (Customer + User) │              │  (Hints & Checkpoints)  │ │
│  └────────────────────┘              └─────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────┐
│                    REST API (/simulation/*)                       │
│                                                                   │
│  POST /simulation/start      → Start new session                 │
│  POST /simulation/{id}/chat  → Send message, get response        │
│  POST /simulation/{id}/ask-coach → Request explicit help         │
│  POST /simulation/{id}/end   → End session, get report           │
│  GET  /simulation/{id}/status → Check session status             │
│  GET  /simulation/cases      → List available training cases     │
└──────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────┐
│              Simulation Orchestrator (Backend)                    │
│  ┌─────────────────┐    ┌──────────────────────────────────────┐ │
│  │   CustomerSim   │    │         ShadowCoach                  │ │
│  │   (Actor)       │    │         (Observer)                   │ │
│  │                 │    │                                      │ │
│  │ - In character  │    │ - Evaluates against rubric           │ │
│  │ - Never breaks  │    │ - Provides hints                     │ │
│  │   fourth wall   │    │ - Tracks checkpoints                 │ │
│  └─────────────────┘    └──────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
```

---

## Getting Started

### Prerequisites

1. **Python 3.10+** installed
2. **Azure OpenAI** API access configured
3. Backend server running

### Starting the Backend Server

```bash
# Navigate to project directory
cd Multi-AI-Agents

# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

### Verify Server is Running

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2026-02-02T10:00:00.000000",
  "version": "1.0.0",
  "services": {
    "config_manager": "healthy",
    "state_manager": "healthy",
    "orchestrator": "healthy",
    "registered_agents": "2"
  }
}
```

---

## Authentication

Currently, the API does not require authentication for local development. For production, implement JWT or API key authentication via middleware.

---

## API Base URL

| Environment | Base URL |
|-------------|----------|
| Local Development | `http://localhost:8000` |
| Production | Configure as needed |

All simulation endpoints are prefixed with `/simulation`.

---

## REST API Endpoints

### 1. List Available Cases

Get all available training cases that can be used to start a simulation.

**Endpoint:** `GET /simulation/cases`

**Response:**

```json
[
  {
    "case_id": "TICKET-101",
    "title": "Angry Customer Demanding Refund",
    "difficulty": "intermediate",
    "primary_skill": "De-escalation",
    "estimated_time": 10,
    "tags": ["refund", "angry-customer", "policy-enforcement"]
  },
  {
    "case_id": "TICKET-102",
    "title": "Billing Dispute Resolution",
    "difficulty": "advanced",
    "primary_skill": "Problem Solving",
    "estimated_time": 15,
    "tags": ["billing", "dispute", "investigation"]
  }
]
```

**TypeScript Interface:**

```typescript
interface CaseListItem {
  case_id: string;
  title: string;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  primary_skill: string;
  estimated_time: number; // minutes
  tags: string[];
}
```

**Usage Example (JavaScript):**

```javascript
const response = await fetch('http://localhost:8000/simulation/cases');
const cases = await response.json();
console.log(cases);
```

---

### 2. Start Simulation Session

Start a new training simulation with a specific case.

**Endpoint:** `POST /simulation/start`

**Request Body:**

```json
{
  "case_id": "TICKET-101",
  "trainee_id": "user-12345"  // Optional
}
```

**Response:**

```json
{
  "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "case_id": "TICKET-101",
  "title": "Angry Customer Demanding Refund",
  "difficulty": "intermediate",
  "primary_skill": "De-escalation",
  "customer_name": "Alex Rivera",
  "opening_message": "I bought a laptop from you guys 45 days ago and it's already broken! The screen just went black. I want my money back RIGHT NOW. This is absolutely ridiculous!",
  "total_checkpoints": 6
}
```

**TypeScript Interfaces:**

```typescript
interface StartSessionRequest {
  case_id: string;
  trainee_id?: string;
}

interface StartSessionResponse {
  session_id: string;
  case_id: string;
  title: string;
  difficulty: string;
  primary_skill: string;
  customer_name: string;
  opening_message: string;  // Display this in the chat immediately
  total_checkpoints: number;
}
```

**Usage Example (JavaScript):**

```javascript
const response = await fetch('http://localhost:8000/simulation/start', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    case_id: 'TICKET-101',
    trainee_id: 'user-12345'
  })
});

const session = await response.json();

// Store session_id for subsequent requests
const sessionId = session.session_id;

// Display the opening message from the customer
displayCustomerMessage(session.customer_name, session.opening_message);
```

---

### 3. Send Chat Message

Send the trainee's message and receive the customer's response along with optional coaching feedback.

**Endpoint:** `POST /simulation/{session_id}/chat`

**Request Body:**

```json
{
  "message": "Hi, I'm really sorry to hear about your laptop. That sounds incredibly frustrating, especially after only 45 days. Let me help you figure out the best solution."
}
```

**Response:**

```json
{
  "customer_response": "Well, I appreciate that, but I still want a refund. This shouldn't have happened in the first place.",
  "coach_feedback": {
    "type": "PRAISE",
    "content": "Great job leading with empathy! The customer's tone is already softening."
  },
  "checkpoint_status": [
    {
      "checkpoint_id": 1,
      "description": "Acknowledge the customer's frustration before anything else",
      "completed": true,
      "completed_at": "2026-02-02T10:05:32.000000",
      "turn_completed": 1
    },
    {
      "checkpoint_id": 2,
      "description": "Express empathy for the situation",
      "completed": true,
      "completed_at": "2026-02-02T10:05:32.000000",
      "turn_completed": 1
    },
    {
      "checkpoint_id": 3,
      "description": "Verify purchase date and explain 30-day return window",
      "completed": false,
      "completed_at": null,
      "turn_completed": null
    }
  ],
  "session_stats": {
    "turn_count": 1,
    "checkpoints_completed": 2,
    "total_checkpoints": 6,
    "hints_received": 1,
    "is_active": true
  }
}
```

**TypeScript Interfaces:**

```typescript
interface ChatRequest {
  message: string;
}

interface CoachFeedback {
  type: 'PRAISE' | 'HINT' | 'WARNING' | 'CHECKPOINT' | 'NONE';
  content: string;
}

interface CheckpointStatus {
  checkpoint_id: number;
  description: string;
  completed: boolean;
  completed_at: string | null;
  turn_completed: number | null;
}

interface SessionStats {
  turn_count: number;
  checkpoints_completed: number;
  total_checkpoints: number;
  hints_received: number;
  is_active: boolean;
}

interface ChatResponse {
  customer_response: string;
  coach_feedback: CoachFeedback | null;
  checkpoint_status: CheckpointStatus[];
  session_stats: SessionStats;
}
```

**Usage Example (JavaScript):**

```javascript
const sessionId = 'a1b2c3d4-e5f6-7890-abcd-ef1234567890';

const response = await fetch(`http://localhost:8000/simulation/${sessionId}/chat`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    message: "Hi, I'm really sorry to hear about your laptop..."
  })
});

const result = await response.json();

// Display customer response in main chat
displayCustomerMessage('Alex Rivera', result.customer_response);

// Display coach feedback in sidebar (if any)
if (result.coach_feedback) {
  displayCoachHint(result.coach_feedback.type, result.coach_feedback.content);
}

// Update checkpoint progress UI
updateCheckpointProgress(result.checkpoint_status);

// Update session stats
updateStatsDisplay(result.session_stats);
```

---

### 4. Ask Coach for Help

Explicitly request coaching guidance (like clicking an "Ask Coach" button).

**Endpoint:** `POST /simulation/{session_id}/ask-coach`

**Request Body:**

```json
{
  "question": "What should I do next?"  // Optional - can be null
}
```

**Response:**

```json
{
  "advice": "The customer mentioned they want a refund, but your policy only allows returns within 30 days. Try acknowledging their loyalty (3 years, 12 purchases) and offer the warranty repair option with expedited service as an alternative."
}
```

**TypeScript Interfaces:**

```typescript
interface AskCoachRequest {
  question?: string | null;
}

interface AskCoachResponse {
  advice: string;
}
```

**Usage Example (JavaScript):**

```javascript
const sessionId = 'a1b2c3d4-e5f6-7890-abcd-ef1234567890';

const response = await fetch(`http://localhost:8000/simulation/${sessionId}/ask-coach`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    question: "How do I handle this refund request?"
  })
});

const result = await response.json();

// Display advice in the coach sidebar
displayCoachAdvice(result.advice);
```

---

### 5. Get Session Status

Check the current status of a simulation session.

**Endpoint:** `GET /simulation/{session_id}/status`

**Response:**

```json
{
  "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "case_id": "TICKET-101",
  "is_active": true,
  "turn_count": 3,
  "checkpoints_completed": 4,
  "total_checkpoints": 6,
  "hints_received": 2,
  "started_at": "2026-02-02T10:00:00.000000",
  "ended_at": null
}
```

**TypeScript Interface:**

```typescript
interface SessionStatus {
  session_id: string;
  case_id: string;
  is_active: boolean;
  turn_count: number;
  checkpoints_completed: number;
  total_checkpoints: number;
  hints_received: number;
  started_at: string;
  ended_at: string | null;
}
```

---

### 6. End Simulation

End the simulation and receive a comprehensive performance report.

**Endpoint:** `POST /simulation/{session_id}/end`

**Response:**

```json
{
  "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "case_title": "Angry Customer Demanding Refund",
  "total_turns": 5,
  "duration_minutes": 8.5,
  "checkpoints_completed": 5,
  "total_checkpoints": 6,
  "completion_percentage": 83.3,
  "hints_received": 2,
  "strengths": [
    "Excellent use of empathy statements",
    "Quick to offer alternative solutions",
    "Maintained professional tone throughout"
  ],
  "opportunities": [
    "Could have acknowledged customer loyalty earlier",
    "Consider offering proactive follow-up"
  ],
  "summary_feedback": "Great job handling this challenging de-escalation scenario! You effectively calmed the customer by leading with empathy and offering concrete alternatives. Focus on recognizing customer loyalty signals for even better rapport."
}
```

**TypeScript Interface:**

```typescript
interface SessionReport {
  session_id: string;
  case_title: string;
  total_turns: number;
  duration_minutes: number;
  checkpoints_completed: number;
  total_checkpoints: number;
  completion_percentage: number;
  hints_received: number;
  strengths: string[];
  opportunities: string[];
  summary_feedback: string;
}
```

**Usage Example (JavaScript):**

```javascript
const sessionId = 'a1b2c3d4-e5f6-7890-abcd-ef1234567890';

const response = await fetch(`http://localhost:8000/simulation/${sessionId}/end`, {
  method: 'POST'
});

const report = await response.json();

// Display the report card
displayReportCard(report);
```

---

### 7. Cleanup Session

Remove a session from server memory (optional, for cleanup).

**Endpoint:** `DELETE /simulation/{session_id}`

**Response:**

```json
{
  "status": "cleaned up",
  "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

---

## Data Models

### Complete TypeScript Types

```typescript
// ============================================================================
// Case Data Models
// ============================================================================

interface CaseListItem {
  case_id: string;
  title: string;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  primary_skill: string;
  estimated_time: number;
  tags: string[];
}

// ============================================================================
// Session Models
// ============================================================================

interface StartSessionRequest {
  case_id: string;
  trainee_id?: string;
}

interface StartSessionResponse {
  session_id: string;
  case_id: string;
  title: string;
  difficulty: string;
  primary_skill: string;
  customer_name: string;
  opening_message: string;
  total_checkpoints: number;
}

interface SessionStatus {
  session_id: string;
  case_id: string;
  is_active: boolean;
  turn_count: number;
  checkpoints_completed: number;
  total_checkpoints: number;
  hints_received: number;
  started_at: string;
  ended_at: string | null;
}

// ============================================================================
// Chat Models
// ============================================================================

interface ChatRequest {
  message: string;
}

interface CoachFeedback {
  type: 'PRAISE' | 'HINT' | 'WARNING' | 'CHECKPOINT' | 'NONE';
  content: string;
}

interface CheckpointStatus {
  checkpoint_id: number;
  description: string;
  completed: boolean;
  completed_at: string | null;
  turn_completed: number | null;
}

interface SessionStats {
  turn_count: number;
  checkpoints_completed: number;
  total_checkpoints: number;
  hints_received: number;
  is_active: boolean;
}

interface ChatResponse {
  customer_response: string;
  coach_feedback: CoachFeedback | null;
  checkpoint_status: CheckpointStatus[];
  session_stats: SessionStats;
}

// ============================================================================
// Coach Models
// ============================================================================

interface AskCoachRequest {
  question?: string | null;
}

interface AskCoachResponse {
  advice: string;
}

// ============================================================================
// Report Models
// ============================================================================

interface SessionReport {
  session_id: string;
  case_title: string;
  total_turns: number;
  duration_minutes: number;
  checkpoints_completed: number;
  total_checkpoints: number;
  completion_percentage: number;
  hints_received: number;
  strengths: string[];
  opportunities: string[];
  summary_feedback: string;
}
```

---

## WebSocket Integration

For real-time streaming responses (optional), WebSocket endpoints are also available:

### Agent WebSocket

**Endpoint:** `ws://localhost:8000/ws/agent/{agent_id}`

**Message Format (Send):**

```json
{
  "message": "User message here",
  "context": {}
}
```

**Message Format (Receive):**

```json
{
  "type": "text|status|complete|error",
  "content": "Response content",
  "metadata": {
    "agent_id": "agent-id"
  }
}
```

### Orchestration WebSocket

**Endpoint:** `ws://localhost:8000/ws/orchestrate`

**Message Format (Send):**

```json
{
  "message": "User message",
  "initial_agent_id": "agent-id",
  "context": {}
}
```

---

## Typical UI Flow

Here's the recommended flow for implementing the UI:

### 1. Case Selection Screen

```javascript
// Load available cases
async function loadCases() {
  const response = await fetch('/simulation/cases');
  const cases = await response.json();
  
  cases.forEach(caseItem => {
    renderCaseCard({
      id: caseItem.case_id,
      title: caseItem.title,
      difficulty: caseItem.difficulty,
      skill: caseItem.primary_skill,
      time: `${caseItem.estimated_time} min`,
      tags: caseItem.tags
    });
  });
}
```

### 2. Start Simulation

```javascript
async function startSimulation(caseId, traineeId) {
  const response = await fetch('/simulation/start', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ case_id: caseId, trainee_id: traineeId })
  });
  
  const session = await response.json();
  
  // Store session ID
  sessionStorage.setItem('simulation_session_id', session.session_id);
  
  // Initialize UI
  initializeChatUI({
    customerName: session.customer_name,
    title: session.title,
    difficulty: session.difficulty,
    totalCheckpoints: session.total_checkpoints
  });
  
  // Display opening message
  addChatMessage('customer', session.customer_name, session.opening_message);
  
  return session;
}
```

### 3. Chat Loop

```javascript
async function sendMessage(userMessage) {
  const sessionId = sessionStorage.getItem('simulation_session_id');
  
  // Show user message immediately
  addChatMessage('user', 'You', userMessage);
  
  // Show loading indicator
  showTypingIndicator();
  
  const response = await fetch(`/simulation/${sessionId}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message: userMessage })
  });
  
  const result = await response.json();
  
  // Hide loading
  hideTypingIndicator();
  
  // Show customer response
  addChatMessage('customer', customerName, result.customer_response);
  
  // Show coach feedback in sidebar (if any)
  if (result.coach_feedback && result.coach_feedback.type !== 'NONE') {
    addCoachHint(result.coach_feedback.type, result.coach_feedback.content);
  }
  
  // Update checkpoint progress
  updateCheckpointList(result.checkpoint_status);
  
  // Update stats bar
  updateStatsBar({
    turn: result.session_stats.turn_count,
    completed: result.session_stats.checkpoints_completed,
    total: result.session_stats.total_checkpoints
  });
  
  // Check if session ended
  if (!result.session_stats.is_active) {
    await endSimulation();
  }
}
```

### 4. Ask Coach Button

```javascript
async function askCoach(question = null) {
  const sessionId = sessionStorage.getItem('simulation_session_id');
  
  const response = await fetch(`/simulation/${sessionId}/ask-coach`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question: question })
  });
  
  const result = await response.json();
  
  addCoachHint('HELP', result.advice);
}
```

### 5. End Simulation & Show Report

```javascript
async function endSimulation() {
  const sessionId = sessionStorage.getItem('simulation_session_id');
  
  const response = await fetch(`/simulation/${sessionId}/end`, {
    method: 'POST'
  });
  
  const report = await response.json();
  
  // Show report modal
  showReportModal({
    title: report.case_title,
    turns: report.total_turns,
    duration: report.duration_minutes,
    score: report.completion_percentage,
    checkpoints: `${report.checkpoints_completed}/${report.total_checkpoints}`,
    hints: report.hints_received,
    strengths: report.strengths,
    opportunities: report.opportunities,
    summary: report.summary_feedback
  });
  
  // Cleanup
  await fetch(`/simulation/${sessionId}`, { method: 'DELETE' });
  sessionStorage.removeItem('simulation_session_id');
}
```

---

## Error Handling

### HTTP Status Codes

| Status | Meaning |
|--------|---------|
| 200 | Success |
| 404 | Session or case not found |
| 500 | Internal server error |
| 503 | Simulation service not initialized |

### Error Response Format

```json
{
  "detail": "Session not found: abc-123"
}
```

### Handling Errors (JavaScript)

```javascript
async function apiCall(url, options = {}) {
  try {
    const response = await fetch(url, options);
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'API request failed');
    }
    
    return await response.json();
  } catch (error) {
    console.error('API Error:', error);
    showErrorToast(error.message);
    throw error;
  }
}
```

---

## Code Examples

### React Hook Example

```typescript
import { useState, useCallback } from 'react';

interface UseSimulationReturn {
  session: StartSessionResponse | null;
  isLoading: boolean;
  error: string | null;
  startSession: (caseId: string) => Promise<void>;
  sendMessage: (message: string) => Promise<ChatResponse>;
  askCoach: (question?: string) => Promise<string>;
  endSession: () => Promise<SessionReport>;
}

export function useSimulation(): UseSimulationReturn {
  const [session, setSession] = useState<StartSessionResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const startSession = useCallback(async (caseId: string) => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch('/simulation/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ case_id: caseId })
      });
      if (!response.ok) throw new Error('Failed to start session');
      const data = await response.json();
      setSession(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const sendMessage = useCallback(async (message: string): Promise<ChatResponse> => {
    if (!session) throw new Error('No active session');
    setIsLoading(true);
    try {
      const response = await fetch(`/simulation/${session.session_id}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message })
      });
      if (!response.ok) throw new Error('Failed to send message');
      return await response.json();
    } finally {
      setIsLoading(false);
    }
  }, [session]);

  const askCoach = useCallback(async (question?: string): Promise<string> => {
    if (!session) throw new Error('No active session');
    const response = await fetch(`/simulation/${session.session_id}/ask-coach`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question })
    });
    const data = await response.json();
    return data.advice;
  }, [session]);

  const endSession = useCallback(async (): Promise<SessionReport> => {
    if (!session) throw new Error('No active session');
    const response = await fetch(`/simulation/${session.session_id}/end`, {
      method: 'POST'
    });
    const report = await response.json();
    setSession(null);
    return report;
  }, [session]);

  return { session, isLoading, error, startSession, sendMessage, askCoach, endSession };
}
```

### API Client Class (TypeScript)

```typescript
class SimulationApiClient {
  private baseUrl: string;
  private sessionId: string | null = null;

  constructor(baseUrl: string = 'http://localhost:8000') {
    this.baseUrl = baseUrl;
  }

  async listCases(): Promise<CaseListItem[]> {
    const response = await fetch(`${this.baseUrl}/simulation/cases`);
    return response.json();
  }

  async startSession(caseId: string, traineeId?: string): Promise<StartSessionResponse> {
    const response = await fetch(`${this.baseUrl}/simulation/start`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ case_id: caseId, trainee_id: traineeId })
    });
    const session = await response.json();
    this.sessionId = session.session_id;
    return session;
  }

  async chat(message: string): Promise<ChatResponse> {
    if (!this.sessionId) throw new Error('No active session');
    const response = await fetch(`${this.baseUrl}/simulation/${this.sessionId}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message })
    });
    return response.json();
  }

  async askCoach(question?: string): Promise<string> {
    if (!this.sessionId) throw new Error('No active session');
    const response = await fetch(`${this.baseUrl}/simulation/${this.sessionId}/ask-coach`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question })
    });
    const data = await response.json();
    return data.advice;
  }

  async getStatus(): Promise<SessionStatus> {
    if (!this.sessionId) throw new Error('No active session');
    const response = await fetch(`${this.baseUrl}/simulation/${this.sessionId}/status`);
    return response.json();
  }

  async endSession(): Promise<SessionReport> {
    if (!this.sessionId) throw new Error('No active session');
    const response = await fetch(`${this.baseUrl}/simulation/${this.sessionId}/end`, {
      method: 'POST'
    });
    const report = await response.json();
    this.sessionId = null;
    return report;
  }

  async cleanup(): Promise<void> {
    if (this.sessionId) {
      await fetch(`${this.baseUrl}/simulation/${this.sessionId}`, {
        method: 'DELETE'
      });
      this.sessionId = null;
    }
  }
}

// Usage
const api = new SimulationApiClient();
const cases = await api.listCases();
const session = await api.startSession('TICKET-101');
const result = await api.chat('Hello, how can I help?');
```

---

## UI Component Recommendations

### Main Chat Panel
- Display customer name with each message
- Use different colors/styles for customer vs trainee messages
- Show typing indicator while waiting for response

### Coach Sidebar
- Display coach hints with appropriate icons based on type:
  - 🎉 PRAISE (green)
  - 💡 HINT (yellow/blue)
  - ⚠️ WARNING (orange)
  - ✅ CHECKPOINT (green checkmark)
- Include "Ask Coach" button

### Progress Tracker
- Show checkpoints as a checklist
- Display completion percentage
- Show turn counter

### Report Card Modal
- Circular progress indicator for completion percentage
- Strengths as green checkmarks
- Opportunities as yellow suggestions
- Summary feedback prominently displayed

---

## Contact & Support

For questions about this API, contact the Skilling Agent development team.

**API Documentation Version:** 1.0.0  
**Backend Version:** 1.0.0  
**Last Updated:** February 2, 2026
