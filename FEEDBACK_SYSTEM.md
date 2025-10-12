# User Feedback and Learning System

## Overview

The AI Fact-Check Chatbot now includes a comprehensive user feedback and learning system that allows the bot to learn from user corrections and build a knowledge base over time.

## Features

### 1. **Feedback Buttons**
Every fact-check result now includes interactive feedback buttons:
- ✓ **Correct** - Confirms the AI's classification is accurate
- ✗ **Incorrect** - Indicates the AI's classification is wrong
- **Submit Answer** - Allows users to provide their own answer when information is unavailable

### 2. **Knowledge Base Priority**
The system checks sources in the following order:
1. **User Knowledge Base** (stored in `knowledge_base.json`) - First priority
2. **Wikipedia API** - Second priority
3. **Google Search** - Third priority

### 3. **Learning from Feedback**

#### When User Agrees (Correct)
- Stores the claim and classification with high confidence (0.9)
- Future similar queries will use this learned information

#### When User Disagrees (Incorrect)
- Stores the opposite classification with medium confidence (0.7)
- For example, if AI says "True" and user marks incorrect, it learns "False"

#### When User Provides Answer
- Stores the claim with user's explanation
- Highest confidence (0.95) since it's direct user input
- The system attempts to infer classification from the answer

### 4. **Smart Claim Matching**
Uses Jaccard similarity algorithm to match similar claims:
- Normalizes text (lowercase, removes punctuation)
- Calculates word overlap ratio
- Threshold of 70% similarity for matching
- Updates existing entries instead of creating duplicates

## Usage Example

### Scenario 1: Unverifiable Claim
**User Query:** "iPhone is owned by Samsung"

**System Response:**
```
❓ Unverifiable

No relevant information found in Wikipedia or Google to verify this claim. 
Please provide your answer if you know the correct information.

[Text area for user answer]
[Submit Answer Button]
```

**User Action:** Types "False, iPhone is owned by Apple Inc."

**Result:** 
- Stored in knowledge_base.json
- Next time someone asks "iPhone is owned by Samsung" or similar, it will respond based on this learned information

### Scenario 2: Subsequent Query
**User Query:** "Is iPhone owned by Samsung?"

**System Response:**
```
❌ False

Based on previous user feedback, this claim is classified as False.

📚 From Knowledge Base - Was this helpful?
[✓ Correct] [✗ Incorrect]

Sources:
1. User Knowledge Base - Learned from user feedback
```

## Knowledge Base Structure

The system maintains a JSON file (`knowledge_base.json`) with the following structure:

```json
{
  "facts": [
    {
      "claim": "iPhone is owned by Samsung",
      "classification": "False",
      "user_provided": true,
      "confidence": 0.95,
      "timestamp": "2025-10-12T20:00:00",
      "feedback_count": 1,
      "positive_feedback": 1,
      "explanation": "False, iPhone is owned by Apple Inc.",
      "user_explanation": "False, iPhone is owned by Apple Inc."
    }
  ],
  "metadata": {
    "created": "2025-10-12T20:00:00",
    "version": "1.0"
  }
}
```

## API Endpoints

### POST /chat
Fact-checks a claim and returns results with feedback options.

**Request:**
```json
{
  "message": "iPhone is owned by Samsung"
}
```

**Response:**
```json
{
  "message": "Formatted message with markdown",
  "classification": "Unverifiable",
  "confidence": 0.0,
  "sources": [],
  "needs_feedback": true,
  "needs_user_input": true,
  "original_claim": "iPhone is owned by Samsung",
  "from_knowledge_base": false
}
```

### POST /feedback
Submits user feedback on a fact-check result.

**Request:**
```json
{
  "claim": "iPhone is owned by Samsung",
  "classification": "Unverifiable",
  "feedback_type": "user_answer",
  "user_answer": "False, iPhone is owned by Apple Inc."
}
```

**Feedback Types:**
- `"correct"` - User confirms the classification is correct
- `"incorrect"` - User says the classification is wrong
- `"user_answer"` - User provides their own answer

**Response:**
```json
{
  "success": true,
  "message": "Thank you! Your answer has been saved: 'False, iPhone is owned by Apple Inc.'. This will be used for future similar queries.",
  "timestamp": "2025-10-12T20:00:00"
}
```

## Technical Details

### Similarity Matching
- Uses **Jaccard similarity** coefficient
- Normalizes claims by:
  - Converting to lowercase
  - Removing punctuation
  - Normalizing whitespace
- Minimum similarity threshold: 0.7 (70%)

### Confidence Levels
- **0.95** - User-provided answers with explanations
- **0.90** - User confirms AI's classification
- **0.70** - User disagrees with AI's classification
- Variable - AI-generated classifications (0.0 - 1.0)

### Feedback Tracking
Each fact entry tracks:
- `feedback_count` - Total number of feedbacks
- `positive_feedback` - Number of "correct" feedbacks
- `last_updated` - Timestamp of last update
- Updates classification when new feedback has higher confidence

## Benefits

1. **Continuous Learning**: The bot gets smarter with each interaction
2. **Local Knowledge**: Builds a knowledge base specific to your use case
3. **Reduced API Calls**: Answers from knowledge base are instant
4. **User Trust**: Shows when answers come from community knowledge
5. **Accuracy Improvement**: Multiple confirmations increase confidence

## Files

- **knowledge_base.json** - Stores learned facts (created automatically)
- **cache.json** - Temporary cache for API responses (24-hour validity)
- **factcheck.py** - Core fact-checking logic with knowledge base integration
- **app.py** - Flask endpoints for chat and feedback
- **templates/index.html** - Frontend with interactive feedback UI

## Future Enhancements

- Export/import knowledge base for sharing
- Admin interface to review and moderate entries
- Confidence decay over time for outdated information
- Source attribution for user-contributed facts
- Multi-user voting system for consensus

