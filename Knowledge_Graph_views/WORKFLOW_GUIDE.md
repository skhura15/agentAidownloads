# Knowledge Graph Generation & Update Workflow

## Overview

This guide describes the complete workflow for generating and updating Knowledge Graphs from text documents, merging them with existing graphs, and exporting to Neo4j.

## Architecture

```
Text Files (.txt)
    ↓
[generate_knowledge_graph.py]
    ↓
knowledge_graph_generated.json (Sub-Graph)
    ↓
[merge_knowledge_graphs.py]
    ↓
knowledge_graph.json (Main Graph - Source of Truth)
    ↓
[convert_to_neo4j.py]
    ↓
Neo4j Database (Cypher/CSV/Direct Import)
```

---

## Prerequisites

### Required Files
- **Text documents** in `data/` directory with structured content
- **knowledge_graph.json** - Main knowledge graph (must exist for merge)
- Python 3.8+ with required packages

### File Naming Conventions
Text files must follow naming conventions to auto-detect node types:

| Filename Prefix | Node Type | Example |
|-----------------|-----------|---------|
| `KnownIssue_*` | KnownIssue | `KnownIssue_VoiceTransferDrop.txt` |
| `Runbook_*` | Runbook | `Runbook_VoiceOutage.txt` |
| `UserGuide_*` | UserGuide | `UserGuide_AgentDesktop.txt` |
| `SOP_*` | SOP | `SOP_P1_Escalation.txt` |
| `SPO_*` | SPO | `SPO_CCaaS_Enterprise.txt` |
| `FAQ_*` | FAQ | `FAQ_PresenceReset.txt` |
| `ReleaseNotes_*` | ReleaseNote | `ReleaseNotes_2025W2.txt` |
| `Configuration_*` | Configuration | `Configuration_VoiceChannel.txt` |
| `Infrastructure_*` | Infrastructure | `Infrastructure_ACS.txt` |

### Text File Format
Documents should contain structured information in key-value format:

```text
===============================================
KNOWN ISSUE — Voice call drops during transfer
===============================================

Issue ID: KI-2025-001
Severity: P1
Status: Fix in Progress
Tags: Voice, Transfer, P1, ACS

AFFECTED VERSIONS:
-----------------
2025 Wave 1, 2025 Wave 2

SYMPTOMS:
---------
- Call drops when agent initiates warm transfer
- Customer hears dead air for 3-5 seconds before disconnect
- Transfer failure logged in ACS

ROOT CAUSE:
-----------
Race condition in Azure Communication Services session handoff 
when both agents are in different Azure regions.

WORKAROUND:
-----------
Ensure both agents are in the same Azure region. Use cold transfer 
instead of warm transfer until patch is applied.

ETA FIX: 2026-03-15
```

---

## Workflow Steps

### Step 1: Generate Sub-Graph from Text Files

**Purpose:** Parse all text files in `data/` directory and create a new sub-graph.

**Command:**
```powershell
python generate_knowledge_graph.py
```

**Advanced Options:**
```powershell
# Custom data directory and output file
python generate_knowledge_graph.py --data-dir ./my_data --output my_graph.json
```

**What it does:**
1. Scans `data/` directory for `.txt` files
2. Detects node type from filename prefix
3. Extracts:
   - Node ID (from content or generates from filename)
   - Label/Title
   - Key-value properties
   - Tags (explicit and inferred from keywords)
   - Sections (symptoms, workaround, etc.)
4. Infers edges between nodes based on ID references
5. Outputs: `knowledge_graph_generated.json`

**Output Example:**
```
📄 Found: 23 text files
   Parsing: KnownIssue_VoiceTransferDrop.txt... ✓ [KnownIssue] KI-001
   Parsing: Runbook_VoiceOutage.txt... ✓ [Runbook] RB-001
   ...
📌 Adding 1 hardcoded nodes...
🔗 Inferring edges...
   ✓ 0 edges created

✅ Knowledge Graph saved: knowledge_graph_generated.json
   📊 Nodes: 24
   🔗 Edges: 0
```

---

### Step 2: Preview Changes (Dry-Run)

**Purpose:** See what will change before actually merging.

**Command:**
```powershell
python merge_knowledge_graphs.py --dry-run
```

**Output Example:**
```
📖 Load target graph: knowledge_graph.json
   ✓ Target: 49 Nodes, 81 Edges
📖 Load source graph: knowledge_graph_generated.json
   ✓ Source: 24 Nodes, 0 Edges

🔄 Merge nodes...
   ✅ Added: KI-001 (KnownIssue) - Voice call drops during transfer
   ✅ Added: RB-001 (Runbook) - Voice Channel Outage Recovery
   ✏️  Updated: PROD-001 (Product) - MS Dynamics 365 Contact Center
   ...

🔍 DRY RUN - No changes saved

📊 MERGE SUMMARY
Nodes:
  ✅ Added:     22
  ✏️  Updated:   2
  ⏭️  Unchanged: 0

Edges:
  ✅ Added:     0
  ⏭️  Duplicate: 0
```

---

### Step 3: Merge Sub-Graph into Main Graph

**Purpose:** Merge the generated sub-graph into the main knowledge graph.

**Command:**
```powershell
python merge_knowledge_graphs.py
```

**Advanced Options:**
```powershell
# Custom source and target files
python merge_knowledge_graphs.py --source my_graph.json --target main_graph.json
```

**What it does:**
1. Loads both graphs
2. **Adds new nodes** not present in main graph
3. **Updates existing nodes** if properties/tags changed
4. **Merges edges** (deduplicates)
5. **Updates metadata** (timestamps, merge history)
6. **Creates automatic backup** (`knowledge_graph_backup_YYYYMMDD_HHMMSS.json`)
7. Saves merged graph to `knowledge_graph.json`

**Merge Strategy:**
- **Nodes:** New nodes added, existing nodes updated if different
- **Properties:** Source properties overwrite target properties
- **Tags:** Union of both tag sets
- **Edges:** Deduplicated by (source, target, type) tuple

**Output:**
```
💾 Create backup: knowledge_graph_backup_20260306_142530.json
💾 Save merged graph: knowledge_graph.json

✅ Merge completed successfully!
```

---

### Step 4: Export to Neo4j

#### Option A: Generate Cypher Queries (Recommended)

**Purpose:** Create idempotent Cypher queries for Neo4j import.

**Command:**
```powershell
# Full import with MERGE (idempotent)
python convert_to_neo4j.py --output cypher --use-merge
```

**Output:**
- `neo4j_output/import.cypher` - Complete import script with:
  - Constraints (unique IDs)
  - Indexes (on labels)
  - MERGE statements for nodes
  - MERGE statements for relationships

**Execute in Neo4j:**
```bash
# Method 1: cypher-shell
cat neo4j_output/import.cypher | cypher-shell -u neo4j -p password

# Method 2: Neo4j Browser
# Copy content of import.cypher and paste into Neo4j Browser
```

---

#### Option B: Delta Update (Incremental)

**Purpose:** Generate only queries for changes since last export.

**Command:**
```powershell
python convert_to_neo4j.py --output delta --previous knowledge_graph_backup.json
```

**What it does:**
1. Compares current graph with previous version
2. Identifies:
   - New nodes to CREATE
   - Updated nodes to UPDATE
   - Deleted nodes to DELETE
   - New edges to MERGE
   - Deleted edges to DELETE

**Output:**
- `neo4j_output/delta_update.cypher` - Incremental update script

**Example Delta Output:**
```
📊 Delta analysis:
   ➕ New Nodes:      3
   ✏️  Updated Nodes:   1
   ❌ Deleted Nodes:   0
   ➕ New Edges:      5
   ❌ Deleted Edges:   0
```

---

#### Option C: CSV Export

**Purpose:** Generate CSV files for bulk import (faster for large graphs).

**Command:**
```powershell
python convert_to_neo4j.py --output csv
```

**Output:**
- `neo4j_output/nodes.csv` - All nodes with properties
- `neo4j_output/edges.csv` - All relationships
- `neo4j_output/load_csv.cypher` - LOAD CSV import script

**Import to Neo4j:**
```bash
# Copy CSV files to Neo4j import directory
cp neo4j_output/*.csv $NEO4J_HOME/import/

# Execute in Neo4j Browser or cypher-shell
cat neo4j_output/load_csv.cypher | cypher-shell -u neo4j -p password
```

---

#### Option D: Direct Import (Requires neo4j Python Package)

**Purpose:** Import directly to Neo4j database via Python driver.

**Prerequisites:**
```powershell
pip install neo4j
```

**Command:**
```powershell
python convert_to_neo4j.py --output direct --neo4j-uri bolt://localhost:7687 --neo4j-user neo4j --neo4j-password yourpassword
```

---

## Complete Workflow Examples

### Scenario 1: Initial Knowledge Graph Creation

```powershell
# Step 1: Add text files to data/ directory
# (Manually create or copy .txt files)

# Step 2: Generate initial graph from text files
python generate_knowledge_graph.py

# Step 3: Review generated graph
# (Open knowledge_graph_generated.json)

# Step 4: If this is the first time, rename to main graph
mv knowledge_graph_generated.json knowledge_graph.json

# Step 5: Export to Neo4j
python convert_to_neo4j.py --output cypher --use-merge
```

---

### Scenario 2: Adding New Documents (Incremental Update)

```powershell
# Step 1: Add new text files to data/ directory
# Example: Added KnownIssue_NewBug.txt, Runbook_NewProcedure.txt

# Step 2: Generate sub-graph from ALL text files
python generate_knowledge_graph.py

# Step 3: Preview merge (dry-run)
python merge_knowledge_graphs.py --dry-run

# Step 4: Merge into main graph
python merge_knowledge_graphs.py

# Step 5: Export delta changes to Neo4j
python convert_to_neo4j.py --output delta --previous knowledge_graph_backup_20260306_142530.json

# Step 6: Apply delta to Neo4j
cat neo4j_output/delta_update.cypher | cypher-shell -u neo4j -p password
```

---

### Scenario 3: Updating Existing Documents

```powershell
# Step 1: Edit existing text files in data/
# Example: Updated KnownIssue_VoiceTransferDrop.txt with new status

# Step 2: Regenerate graph
python generate_knowledge_graph.py

# Step 3: Merge (this will update existing nodes)
python merge_knowledge_graphs.py

# Step 4: Export full graph with MERGE (idempotent - no duplicates)
python convert_to_neo4j.py --output cypher --use-merge
cat neo4j_output/import.cypher | cypher-shell -u neo4j -p password
```

---

### Scenario 4: Performance Testing (Large Graphs)

```powershell
# Benchmark: Full rebuild vs. merge
python benchmark_merge.py

# Example output:
# Full rebuild:  123.45 seconds (1000+ nodes)
# Merge update:  0.02 seconds (10 new nodes)
# Speedup: 6172x faster
```

---

## File Structure

```
Knowledge_Graph_views/
├── data/                          # Text documents (input)
│   ├── KnownIssue_*.txt
│   ├── Runbook_*.txt
│   ├── UserGuide_*.txt
│   └── ...
│
├── knowledge_graph.json           # Main graph (source of truth)
├── knowledge_graph_generated.json # Generated sub-graph
├── knowledge_graph_backup_*.json  # Automatic backups
│
├── generate_knowledge_graph.py    # Text → JSON converter
├── merge_knowledge_graphs.py      # Graph merger
├── convert_to_neo4j.py            # Neo4j exporter
├── benchmark_merge.py             # Performance tester
│
├── neo4j_output/                  # Neo4j exports
│   ├── import.cypher              # Full import script
│   ├── delta_update.cypher        # Incremental update
│   ├── nodes.csv                  # Bulk CSV export
│   ├── edges.csv
│   └── load_csv.cypher
│
└── WORKFLOW_GUIDE.md              # This file
```

---

## Best Practices

### 1. Always Use Dry-Run First
```powershell
python merge_knowledge_graphs.py --dry-run
```
Review changes before committing to avoid unintended updates.

### 2. Keep Backups
Automatic backups are created during merge, but you can also manually backup:
```powershell
cp knowledge_graph.json knowledge_graph_manual_backup.json
```

### 3. Use Delta Updates for Neo4j
For incremental updates, delta mode is much faster:
```powershell
python convert_to_neo4j.py --output delta --previous knowledge_graph_backup_YYYYMMDD.json
```

### 4. Version Control
Commit `knowledge_graph.json` to Git after significant changes:
```bash
git add knowledge_graph.json
git commit -m "Added 5 new known issues and 3 runbooks"
```

### 5. Validate Text Files
Ensure text files follow the naming convention and structured format for best parsing results.

### 6. Review Merge History
Check metadata in `knowledge_graph.json`:
```json
"metadata": {
  "merge_history": [
    {
      "date": "2026-03-06 14:25:30",
      "source": "knowledge_graph_generated.json",
      "nodes_added": 22,
      "nodes_updated": 2,
      "edges_added": 0
    }
  ]
}
```

---

## Troubleshooting

### Issue: Node type not detected
**Symptom:** `⚠ Could not detect node type for: MyFile.txt`

**Solution:** Ensure filename starts with supported prefix:
```
❌ MyKnownIssue.txt
✅ KnownIssue_MyIssue.txt
```

---

### Issue: Duplicate nodes in Neo4j
**Symptom:** Multiple nodes with same ID

**Solution:** Always use `--use-merge` flag:
```powershell
python convert_to_neo4j.py --output cypher --use-merge
```

---

### Issue: Edges not created
**Symptom:** Nodes exist but no relationships

**Solution:** 
1. Ensure text files reference other node IDs (e.g., `KI-001`, `RB-002`)
2. Check edge inference rules in `generate_knowledge_graph.py`
3. Manually add edges to JSON if needed

---

### Issue: Merge overwrites manual changes
**Symptom:** Manual edits to `knowledge_graph.json` are lost

**Solution:**
- Edit text files instead of JSON
- Or exclude specific nodes from merge (modify `merge_knowledge_graphs.py`)

---

## Performance Metrics

Based on real-world testing:

| Operation | Small Graph (50 nodes) | Large Graph (1000 nodes) |
|-----------|------------------------|--------------------------|
| Generate | 2 seconds | 15 seconds |
| Merge (10 new nodes) | 0.02 seconds | 0.05 seconds |
| Full Rebuild | 2 seconds | 123 seconds |
| **Speedup (Merge vs Rebuild)** | **100x** | **2460x** |
| Neo4j Export (Cypher) | 1 second | 8 seconds |
| Neo4j Export (Delta) | 0.5 seconds | 2 seconds |

**Recommendation:** Use merge workflow for production - it's **100-6000x faster** than full rebuilds.

---

## Advanced Topics

### Custom Node Types
To add new node types, edit `generate_knowledge_graph.py`:

```python
NODE_TYPE_MAPPING = {
    "KnownIssue": "KnownIssue",
    "MyCustomType": "CustomNode",  # Add this
}

ALL_NODE_TYPES = [
    "Product", "Service", "CustomNode",  # Add this
]
```

### Custom Edge Rules
To add edge inference rules, edit `_determine_edge_type()` in `generate_knowledge_graph.py`:

```python
edge_rules = {
    ("CustomNode", "Service"): "USES_SERVICE",
}
```

### Filtering Nodes
To exclude certain nodes from merge, modify `merge_knowledge_graphs.py`:

```python
# Skip nodes with specific IDs
if source_node['id'] in ['SKIP-001', 'TEMP-002']:
    continue
```

---

## Integration with AI Agents

The generated knowledge graph is optimized for AI agent consumption:

```json
"ai_agent_instructions": {
  "purpose": "When a support ticket arrives...",
  "resolution_workflow": [
    "1. PARSE: Extract product, service, error messages",
    "2. IDENTIFY SERVICE: Map symptoms to affected service",
    "3. CHECK KNOWN ISSUES: Search matching symptoms",
    ...
  ]
}
```

AI agents can traverse the graph to find optimal resolution paths.

---

## Summary

| Step | Command | Input | Output |
|------|---------|-------|--------|
| 1. Generate | `python generate_knowledge_graph.py` | Text files | `knowledge_graph_generated.json` |
| 2. Merge | `python merge_knowledge_graphs.py` | Generated + Main graph | Updated `knowledge_graph.json` |
| 3. Export | `python convert_to_neo4j.py --output cypher` | Main graph | `neo4j_output/import.cypher` |

**Total Time:** ~5 seconds for typical updates

---

## Support

For issues or questions:
1. Check `logs/` directory for error details
2. Review merge history in metadata
3. Use `--dry-run` to preview changes
4. Consult source code comments (now in English!)

---

**Last Updated:** March 6, 2026  
**Version:** 2.0.0  
**Author:** Knowledge Graph Generator Team
