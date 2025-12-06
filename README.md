# Reasoning Agent - CSE 476 Final Project

**GitHub Repository:** https://github.com/A-Wattamwar/CSE476_FinalProject_InferenceTime.git

## How the Agent Works

### Three Core Components

1. **Question Classifier** (`answer_parser.py`, `classify_question()` function, lines 4-24)
   - Uses an LLM call to classify questions into types: math, coding, planning, future, general
   - Enables type-specific prompting and answer extraction

2. **Inference Techniques** (4 techniques implemented):
   - **Self-Consistency** (`technique1_self_consistency.py`, `self_consistency()`, lines 5-32): Generates 3 samples with varying temperatures, uses majority voting to select the most common answer
   - **Chain-of-Thought with Verification** (`technique2_cot_verify.py`, `cot_with_verification()`, lines 4-27): Step-by-step reasoning followed by a verification LLM call
   - **Iterative Refinement** (`technique3_refinement.py`, `iterative_refinement()`, lines 4-37): Generate answer, critique it, refine based on feedback
   - **PAL (Program-Aided Language)** (`technique4_pal.py`, `pal_solve()`, lines 4-30): For math problems, generates Python code and executes it locally for accurate computation

3. **Answer Orchestrator** (`agent.py`, `solve()` function)
   - Routes each question to the technique best suited to its type, with a second technique as a backup / tie-breaker:
     | Question type | Primary technique | Backup |
     |---|---|---|
     | math | PAL | Self-Consistency |
     | coding | Iterative Refinement | CoT + Verification |
     | planning | Iterative Refinement | Self-Consistency |
     | future | CoT + Verification | Self-Consistency |
     | general (common sense) | Self-Consistency | CoT + Verification |
   - For coding/planning, returns the highest-confidence answer
   - For math/general/future, combines answers using confidence-weighted voting and returns the original-cased representative answer (preserves proper nouns like "Arthur's Magazine")

### Additional Highlights

- Type-specific prompts for each question category
- Type-specific answer extraction (`answer_parser.py`, `extract_answer()` and helper functions)
- PAL technique improves math accuracy through code execution
- Under 20 API calls per question

## Setup and Installation

1. **Clone the repository:**
```bash
git clone https://github.com/A-Wattamwar/CSE476_FinalProject_InferenceTime.git
cd CSE476_FinalProject_InferenceTime
```

## Requirements

- An OpenAI API key (the agent calls the OpenAI Chat Completions API)

- Python Requests

```bash
pip3 install requests
```

If that fails on macOS (system-managed Python protects certain packages), use:

```bash
pip3 install --break-system-packages requests
```

### Configure the API

The agent reads its endpoint, model, and key from environment variables
(`api.py`). Defaults point at OpenAI's API with `gpt-4o-mini`. Set your key
before running:

```bash
export OPENAI_API_KEY='sk-...your-key...'
# optional overrides:
export MODEL_NAME='gpt-4o-mini'          # or gpt-4o for a stronger model
export API_BASE='https://api.openai.com/v1'
```

> Note: avoid the `o1`/`o3`/`gpt-5` reasoning models here — they reject the
> `temperature` parameter that `api.py` sends.

## How to Run on a New Test Case

**Option 1: Test a single question in Python**
```python
import sys
sys.path.insert(0, "path/to/agent")
from agent import solve

# Math question
print(solve("What is 25 * 4?"))  # 100

# General question
print(solve("What is the capital of France?"))  # paris

# Coding question
print(solve("Write code to add two numbers"))
```

**Option 2: From command line**
```bash
cd agent
python3 -c "from agent import solve; print(solve('Your question here'))"
```

**Option 3: Run on full test dataset**
```bash
cd given/cse476_final_project_submission
python3 generate_answer_template.py
```

This generates `cse_476_final_project_answers.json` for submission.

## Demo

Run the demo script to test all four techniques individually, then watch the
full agent route questions on its own:

```bash
export OPENAI_API_KEY='sk-...your-key...'
cd agent
python3 demo.py
```

Each technique is exercised directly with a question that shows it at its best:

| # | Technique | Demo question | Expected answer |
|---|---|---|---|
| 1 | **PAL** (Program-Aided Language) | "A bakery sells muffins for \$3 each and cookies for \$2 each. If I buy 7 muffins and 5 cookies, how much do I spend in total?" | `31` — generates `answer = 7*3 + 5*2` and executes it (confidence 0.95) |
| 2 | **Self-Consistency** | "Which planet in our solar system is known as the Red Planet?" | `Mars` — majority vote across 3 samples |
| 3 | **Iterative Refinement** | "What is the capital city of Australia?" | `Canberra` — draft, self-critique, then refine |
| 4 | **Chain-of-Thought + Verification** | "Tom is older than Jane. Jane is older than Sam. Who is the youngest of the three?" | `Sam` — reasons step by step, then a verification call confirms it |

The script then calls `solve()` on a math and a coding question to show the
classifier routing each to the right technique automatically.

You can also run any single question directly:

```bash
cd agent
python3 -c "from agent import solve; print(solve('What is 25 * 4?'))"  # 100
```

## Development & Evaluation

### How I Built It

1. Started with the API wrapper (`api.py`), this was pre-given in final_project_tutorial.ipynb file.
2. Built the question classifier to route questions to the right technique
3. Implemented each technique in separate files: Self-Consistency first, then CoT, then Iterative Refinement, then PAL
4. Created answer extractors for different question types (math needs numbers, coding needs code blocks, etc.)
5. Added confidence scores to each technique so I could combine their results
6. Added safety checks in PAL to skip code with loops (was causing hangs)

### How I Tested It

- Used the dev dataset (`cse476_final_project_dev_data.json`) to test
- Ran sample questions from each category and checked outputs, check out test_agent.py
- Fixed common issues like empty answers, answers with too much explanation
- Kept tweaking prompts to get cleaner outputs
- Used 3 samples for self-consistency to balance speed vs accuracy

## Project Structure

```
agent.py                        # Main orchestrator - solve() function
answer_parser.py                # Question classifier + answer extraction
api.py                          # API wrapper for LLM calls
technique1_self_consistency.py  # Self-consistency with majority voting
technique2_cot_verify.py        # Chain-of-thought with verification
technique3_refinement.py        # Iterative refinement
technique4_pal.py               # Program-aided language for math
demo.py                         # Demo script - one question per technique
README.md                       # This file
```

## Author

**Ayush Sachin Wattamwar**

This project was developed as a final project for a course at Arizona State University. 

CSE476 - Introduction to Natural Language Processing.
