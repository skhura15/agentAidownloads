# Knowledge Graph Generator - Guide

## Overview

The `generate_knowledge_graph.py` script automatically generates a `knowledge_graph.json` file from structured text files in the `data/` directory.

## Usage

### Basic Usage
```bash
python generate_knowledge_graph.py
```

### With Options
```bash
# Custom Data Directory
python generate_knowledge_graph.py --data-dir ./my_data

# Custom Output File
python generate_knowledge_graph.py --output my_graph.json

# Both Options
python generate_knowledge_graph.py --data-dir ./my_data --output my_graph.json
```

## Adding New Text Files

### 1. Filename Convention

The filename must start with a node type prefix:

| Prefix | Node Type | Example |
|--------|----------|----------|
| `KnownIssue_` | KnownIssue | `KnownIssue_VoiceTransferDrop.txt` |
| `Runbook_` | Runbook | `Runbook_VoiceOutage.txt` |
| `UserGuide_` | UserGuide | `UserGuide_AgentDesktop.txt` |
| `SOP_` | SOP | `SOP_P1_Escalation.txt` |
| `SPO_` | SPO | `SPO_CCaaS_Enterprise.txt` |
| `FAQ_` | FAQ | `FAQ_QM_Drift.txt` |
| `ReleaseNotes_` | ReleaseNote | `ReleaseNotes_2025W2.txt` |
| `Configuration_` | Configuration | `Configuration_ACS.txt` |
| `Infrastructure_` | Infrastructure | `Infrastructure_Azure.txt` |

### 2. Text File Format

Each text file should contain structured information. The script recognizes:

#### Header with Title
```
================================================================================
KNOWN ISSUE — KI-2025-001
Voice Call Drops During Warm Transfer
================================================================================
```

#### Key-Value Pairs
```
Issue ID     : KI-2025-001
Severity     : P1 (Critical)
Status       : Fix in Progress
ETA Fix      : March 15, 2026
```

These are automatically extracted as `properties`.

#### Sections
```
SYMPTOMS:
---------
1. Agent initiates a warm transfer
2. Customer hears dead air
3. Call disconnects

ROOT CAUSE:
-----------
Race condition in Azure Communication Services...
```

Important sections (SYMPTOMS, WORKAROUND, etc.) are automatically extracted.

#### Tags (optional)
```
Tags: Voice, ACS, Transfer, P1
```

If not present, tags are generated from keywords in the text.

### 3. Example: Adding a New Known Issue

**File:** `data/KnownIssue_ChatLatency.txt`

```
================================================================================
KNOWN ISSUE — KI-2026-010
Chat Messages Delayed in High Load
================================================================================

Issue ID     : KI-2026-010
Severity     : P2
Status       : Investigation in Progress
Reported     : March 1, 2026
Affected     : 2025 Wave 2

SYMPTOMS:
---------
1. Chat messages from customer arrive with 5-10 second delay
2. Agent sees typing indicator but message appears later
3. Occurs during peak hours (10 AM - 2 PM)
4. Affects approximately 15% of chat sessions

ROOT CAUSE:
-----------
WebSocket connection pool exhaustion when customer chat volume 
exceeds 1000 concurrent sessions per region.

WORKAROUND:
-----------
Option 1: Scale out chat service instances
  1. Azure Portal > App Service
  2. Scale to additional instances
  3. Monitor connection pool metrics

Option 2: Enable connection pooling optimization
  1. Admin Center > Settings
  2. Enable "Chat Connection Pooling"
  3. Set pool size to 2000

Tags: Chat, WebSocket, Latency, P2
```

### 4. Example: Adding a New Runbook

**File:** `data/Runbook_ChatRecovery.txt`

```
================================================================================
RUNBOOK — RB-CHAT-001
Chat Service Recovery
================================================================================

Runbook ID        : RB-CHAT-001
Category          : Incident Recovery
Estimated Time    : 20 minutes
Owner             : Digital Messaging Team

STEP 1: CHECK SERVICE HEALTH
-----------------------------
1. Navigate to Admin Center > Service Health
2. Check Digital Messaging status
3. Review recent incidents

STEP 2: RESTART CHAT SERVICE
-----------------------------
1. Admin Center > Channels > Chat
2. Click "Restart Service"
3. Wait 2-3 minutes for restart

STEP 3: VERIFY FUNCTIONALITY
-----------------------------
1. Open test chat widget
2. Send test message
3. Verify message delivery

Tags: Chat, Recovery, Runbook
```

## Automatic Processing

After adding new text files:

1. **Save** the file in the `data/` directory
2. **Execute**: `python generate_knowledge_graph.py`
3. **Result**: The new `knowledge_graph_generated.json` contains all nodes

## What is Automatically Extracted?

### For All Node Types
- ✅ **ID**: From content or generated from filename
- ✅ **Label**: Title from the document
- ✅ **Properties**: All key-value pairs
- ✅ **Tags**: Explicit tags or generated from keywords
- ✅ **Document Path**: Automatically as `data/[filename].txt`

### For KnownIssue
- ✅ **Severity**: P0-P4
- ✅ **Status**: Investigation, Fix in Progress, etc.
- ✅ **Symptoms**: From SYMPTOMS section
- ✅ **Workaround**: From WORKAROUND section

### For Runbook
- ✅ **Category**: Incident Recovery, Configuration, etc.
- ✅ **Estimated Time**: From "Estimated Time" field

### For UserGuide
- ✅ **Audience**: Target Audience from properties

## Edge Generation

Edges are automatically inferred when:
- A node references the ID of another node in its properties
- The edge type is determined based on node types

Example:
```
# In KnownIssue_VoiceTransferDrop.txt:
Fix Planned: See RB-VOICE-001 for recovery steps

# Automatically generates:
{
  "source": "KI-2025-001",
  "target": "RB-VOICE-001",
  "type": "RELATED_TO"
}
```

## Advanced Configuration

### Adding Hardcoded Nodes

Edit `generate_knowledge_graph.py` → function `add_hardcoded_nodes()`:

```python
def add_hardcoded_nodes(self) -> None:
    hardcoded_nodes = [
        {
            "id": "SVC-001",
            "type": "Service",
            "label": "Omnichannel Voice",
            "properties": {
                "service_id": "CCaaS-VOICE",
                "description": "Voice service with ACS integration"
            },
            "tags": ["Voice", "ACS"]
        },
        # More nodes...
    ]
    self.nodes.extend(hardcoded_nodes)
```

### Adding New Node Types

Edit `generate_knowledge_graph.py` → `NODE_TYPE_MAPPING`:

```python
NODE_TYPE_MAPPING = {
    "KnownIssue": "KnownIssue",
    "Runbook": "Runbook",
    # ... existing ...
    "NewType": "NewType",  # Newly added
}
```

## Tips for Best Results

1. **Consistent Formatting**: Use uniform headers and sections
2. **Clear IDs**: Use unique IDs in format `XX-XXXX-XXX`
3. **Referencing**: Mention other IDs in text for automatic edges
4. **Tags**: Add relevant tags for better filtering
5. **Sections**: Use ALL-CAPS headings for important sections

## Troubleshooting

### "Could not detect node type"
→ Filename must start with a valid prefix (see table above)

### "No .txt files found"
→ Check if `data/` directory exists and contains .txt files

### "Properties empty"
→ Add key-value pairs in format `Key : Value`

### "No edges generated"
→ Reference IDs of other nodes in your text files

## Example Workflow

```bash
# 1. Create new text file
echo "Creating new Known Issue..."
notepad data/KnownIssue_NewProblem.txt

# 2. Generate knowledge graph
python generate_knowledge_graph.py

# 3. Check result
cat knowledge_graph_generated.json

# 4. Optional: Compare with original
code --diff knowledge_graph.json knowledge_graph_generated.json
```

## Output

The script generates:
- `knowledge_graph_generated.json` - The complete Knowledge Graph JSON
- Console output with details about parsed nodes

## Further Development

To extend the script:
1. **Better NLP**: Integrate spaCy or NLTK for text analysis
2. **Advanced Edge Inference**: Machine learning for relationship detection
3. **Validation**: Schema validation against knowledge_graph.json
4. **Visualization**: Graph visualization directly from the script

## Support

For questions or issues:
1. Check this README
2. Look at example text files in the `data/` directory
3. Run the script with `--help`: `python generate_knowledge_graph.py --help`
