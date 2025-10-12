# Testing the Feedback System

## Test Case: "Narendra Modi is PM of India"

### Step 1: Initial Query
**Input:** "Narendra Modi is PM of India"

**Expected Result:** 
- AI might classify as "Misleading" (60% confidence) because it's technically true but the phrasing might be ambiguous
- Shows feedback buttons with 4 classification options + "AI is Correct" button

### Step 2: User Provides Feedback
**User Action:** Clicks "✓ True" button

**System Action:**
1. Sends feedback to `/feedback` endpoint
2. Stores in `knowledge_base.json`:
   ```json
   {
     "claim": "Narendra Modi is PM of India",
     "classification": "True",
     "confidence": 0.95,
     "user_provided": true,
     "timestamp": "...",
     "feedback_count": 1
   }
   ```
3. Shows confirmation: "✓ Saved as TRUE. Future similar queries will use this classification."

### Step 3: Test with Same Query Again
**Input:** "Narendra Modi is PM of India" (or similar like "Is Narendra Modi PM of India?")

**Expected Result:**
```
✅ True

Based on previous user feedback, this claim is classified as True.

📚 From Knowledge Base - Was this helpful?

Sources:
1. User Knowledge Base - Learned from user feedback (confidence: 1 feedback(s))

[Feedback buttons shown]
```

### Step 4: Test with Similar Query
**Input:** "Is Narendra Modi the prime minister of India?"

**Expected Result:**
- Should match with 70%+ similarity
- Returns "True" classification from knowledge base
- Shows it's from user knowledge base

## All Feedback Options

### Option 1: ✓ True
- Sets classification as True
- Confidence: 0.95
- Use when: Claim is factually correct

### Option 2: ✗ False
- Sets classification as False
- Confidence: 0.95
- Use when: Claim is factually incorrect

### Option 3: ⚠️ Misleading
- Sets classification as Misleading
- Confidence: 0.95
- Use when: Claim is partially true but lacks context

### Option 4: ❓ Unverifiable
- Sets classification as Unverifiable
- Confidence: 0.95
- Use when: Cannot be verified with available sources

### Option 5: 👍 AI Classification is Correct
- Confirms AI's current classification
- Confidence: 0.90
- Use when: AI got it right

## Testing in Browser

1. **Open:** http://localhost:5001
2. **Enter claim:** "Narendra Modi is PM of India"
3. **Wait for result** (may show as Misleading)
4. **Click:** "✓ True" button
5. **See confirmation:** Message appears
6. **Test again:** Enter the same claim
7. **Verify:** Should now show "True" from Knowledge Base

## Command Line Testing

```bash
# Test 1: Submit feedback
curl -X POST http://localhost:5001/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "claim": "Narendra Modi is PM of India",
    "classification": "Misleading",
    "feedback_type": "set_true"
  }'

# Test 2: Query again to see learned result
curl -X POST http://localhost:5001/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Narendra Modi is PM of India"}'

# Test 3: Similar query
curl -X POST http://localhost:5001/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Is Narendra Modi the prime minister of India"}'
```

## Expected Behavior

✅ **First time:** AI classification (may vary)
✅ **After feedback:** User's chosen classification
✅ **Similar queries:** Matches and uses learned classification
✅ **Shows source:** "User Knowledge Base"
✅ **Persistent:** Survives server restarts (stored in JSON)

