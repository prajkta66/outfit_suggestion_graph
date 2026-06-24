# Outfit Suggestion Graph - Learn LangGraph Step by Step

This workspace contains a LangGraph example project that suggests outfits
for a given occasion based on the user's wardrobe items.

The graph demonstrates a clear LangGraph pattern:

```text
[Occasion + Wardrobe Items]
              |
              v
    understand_request
              |
      +-------+-------+
      |       |       |
      v       v       v
 match_outfit  suggest  suggest
    _to_occasion  _color_  _accessories_
      |       |       |
      +-------+-------+
              |
              v
        decide_style
           /    \
     casual      formal
       |           |
       v           v
 casual_outfit  formal_outfit
     _plan_        _plan_
              |
             END
```

---

## What This Project Does

A user enters:

- an occasion (e.g. `birthday dinner`, `business meeting`, `weekend brunch`)
- wardrobe items they already own (e.g. `white shirt, black jeans, leather jacket`)

The graph then:

1. Acknowledges the occasion and wardrobe items.
2. Runs three specialist nodes in parallel:
   - match outfit to the occasion
   - suggest color pairings
   - suggest accessories and footwear
3. Uses a decision node to choose whether the look should be casual or formal.
4. Routes to the correct final outfit plan.
5. Prints the final outfit plan and message log.

---

## LangGraph Concepts Covered

| Concept | Where It Appears |
|---|---|
| State | `OutfitState` Pydantic model |
| Nodes | `understand_request`, `match_outfit_to_occasion`, `suggest_color_pairings`, `suggest_accessories`, `decide_style`, `casual_outfit_plan`, `formal_outfit_plan` |
| Parallel execution | Three specialist nodes run after `understand_request` |
| Fan-in | All three specialist suggestions flow into `decide_style` |
| Conditional edges | `route_after_decision` sends the graph to casual or formal outfit planning |
| Final output | `casual_outfit_plan` or `formal_outfit_plan` |
| Message accumulation | `messages: Annotated[list, operator.add]` |

---

## Project Files

```text
outfit_suggestion_graph.py  Main LangGraph outfit suggestion project
architecture.md            Architecture explanation
architecture.drawio        Diagram source file
requirements.txt           Python dependencies
.env.example               Example environment file
.gitignore                 Ignored local files
```

---

## Setup

### 1. Create and activate a virtual environment

```powershell
python -m venv venv
venv\Scripts\activate
```

On macOS/Linux:

```bash
python -m venv venv
source venv/bin/activate
```

### 2. Install dependencies

```powershell
pip install -r requirements.txt
```

### 3. Configure your OpenAI API key

```powershell
copy .env.example .env
```

Edit `.env` and add your API key:

```text
OPENAI_API_KEY=sk-...
```

Never commit your real `.env` file.

### 4. Run the project

```powershell
python outfit_suggestion_graph.py
```

---

## Expected Flow

Example input:

```text
I need an outfit for a summer brunch with friends.
```

The graph will:

1. Acknowledge the occasion and wardrobe items.
2. Match an outfit to the occasion.
3. Suggest color pairings.
4. Recommend accessories and footwear.
5. Decide whether the final look should be casual or formal.
6. Print the final outfit plan.
7. Print the message log showing which nodes executed.

---

## Code Walkthrough

| Step | What Happens | File |
|---|---|---|
| 1 | Define the `OutfitState` model | `outfit_suggestion_graph.py` |
| 2 | Initialize `ChatOpenAI` | `outfit_suggestion_graph.py` |
| 3 | Define graph node functions | `outfit_suggestion_graph.py` |
| 4 | Define `route_after_decision` | `outfit_suggestion_graph.py` |
| 5 | Add nodes and edges to `StateGraph` | `outfit_suggestion_graph.py` |
| 6 | Compile graph as `app` | `outfit_suggestion_graph.py` |
| 7 | Run with `run_outfit_suggestion()` | `outfit_suggestion_graph.py` |

This repository focuses on `outfit_suggestion_graph.py`, which uses specialist nodes for matching outfits, recommending color pairings, suggesting accessories, and routing to a casual or formal outfit plan.

---

## Important Note

This is a learning project focused on outfit suggestion and LangGraph concepts. It is not intended as a general styling service or personal wardrobe consultant.

---

## Key Takeaways

1. State holds the data that travels through the graph.
2. Nodes are normal Python functions that read state and return updates.
3. Parallel execution happens when one node connects to multiple next nodes.
4. Fan-in happens when multiple nodes connect into one later node.
5. Conditional edges let the graph choose the next path at runtime.
