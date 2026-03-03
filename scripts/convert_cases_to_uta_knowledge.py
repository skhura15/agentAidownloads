#!/usr/bin/env python3
"""
Convert Cases to UTA Knowledge Base Format

Converts data/cases/*.json into markdown files that can be ingested
into UTA's RAG vector store alongside existing knowledge.

This does NOT replace existing uta_knowledge - it ADDS to it.

Usage:
    python scripts/convert_cases_to_uta_knowledge.py
    
    # Then run ingestion
    python -m examples.uta_ingest_knowledge --clear
"""

import json
import os
from pathlib import Path
from datetime import datetime


ROOT = Path(__file__).parent.parent
CASES_DIR = ROOT / "data" / "cases"
CONFIGS_DIR = ROOT / "data" / "sim_configs"
OUTPUT_DIR = ROOT / "data" / "uta_knowledge" / "skilling_cases"


def md_bullets(items: list) -> str:
    """Format list as markdown bullets."""
    if not items:
        return "- (none)"
    return "\n".join([f"- {x}" for x in items])


def convert_case_to_markdown(case_data: dict, sim_config: dict = None) -> str:
    """Convert a case JSON to markdown format for RAG ingestion."""
    
    tid = case_data.get("ticket_id", "UNKNOWN")
    title = case_data.get("title", "Untitled Case")
    skill = case_data.get("primary_skill", "General")
    difficulty = case_data.get("difficulty", "intermediate")
    est_time = case_data.get("estimated_time_minutes", 10)
    tags = case_data.get("tags", [])
    
    raw = case_data.get("raw_content", {})
    customer_name = raw.get("customer_name", "Customer")
    initial_message = raw.get("initial_message", "")
    context = raw.get("context", "")
    
    annotations = case_data.get("annotations", {})
    sop_steps = annotations.get("correct_sop_steps", [])
    objectives = annotations.get("learning_objectives", [])
    mistakes = annotations.get("common_mistakes", [])
    sticky_notes = annotations.get("sticky_notes", [])
    
    persona = case_data.get("customer_persona_hints", {})
    tone = persona.get("tone", "")
    secret = persona.get("secret_acceptance_condition", "")
    escalation = persona.get("escalation_triggers", [])
    de_escalation = persona.get("de-escalation_triggers", persona.get("de_escalation_triggers", []))
    
    # Build markdown
    md = f"""# SOP-{tid}: {title}

## Case Overview
- **Ticket ID:** {tid}
- **Primary Skill:** {skill}
- **Difficulty:** {difficulty}
- **Estimated Time:** {est_time} minutes
- **Tags:** {", ".join(tags) if tags else "None"}

## Scenario Context
{context}

## Customer Profile
- **Name:** {customer_name}
- **Tone:** {tone}
- **Secret Acceptance Condition:** {secret}

### Customer's Initial Message
> {initial_message}

### Escalation Triggers (what makes customer angrier)
{md_bullets(escalation)}

### De-escalation Triggers (what calms customer)
{md_bullets(de_escalation)}

## Correct SOP Steps (SME Approved)
{md_bullets(sop_steps)}

## Learning Objectives
{md_bullets(objectives)}

## Common Mistakes to Avoid
{md_bullets(mistakes)}

## Coach Notes (Sticky Notes)
{md_bullets(sticky_notes)}
"""
    
    # Add rubric checkpoints if sim_config available
    if sim_config:
        rubric = sim_config.get("coaching_rubric", {})
        checkpoints = rubric.get("checkpoints", [])
        if checkpoints:
            md += "\n## Coaching Checkpoints\n"
            for cp in checkpoints:
                importance = cp.get("importance", "required").upper()
                desc = cp.get("description", "")
                hint = cp.get("hint_if_missed", "")
                md += f"- **[{importance}]** {desc}\n"
                if hint:
                    md += f"  - Hint: {hint}\n"
    
    return md


def main():
    """Main conversion function."""
    
    if not CASES_DIR.exists():
        print(f"❌ Cases directory not found: {CASES_DIR}")
        return
    
    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Load cases
    case_files = sorted(CASES_DIR.glob("*.json"))
    print(f"📂 Found {len(case_files)} case files")
    
    # Load sim configs for additional context
    configs = {}
    for cfg_file in CONFIGS_DIR.glob("config_*.json"):
        try:
            data = json.loads(cfg_file.read_text(encoding="utf-8"))
            case_id = data.get("case_id")
            if case_id:
                configs[case_id] = data
        except Exception as e:
            print(f"⚠️ Failed to load config {cfg_file}: {e}")
    
    # Convert each case
    converted = 0
    for case_file in case_files:
        try:
            case_data = json.loads(case_file.read_text(encoding="utf-8"))
            tid = case_data.get("ticket_id", case_file.stem)
            
            # Get corresponding sim config
            sim_config = configs.get(tid)
            
            # Convert to markdown
            md_content = convert_case_to_markdown(case_data, sim_config)
            
            # Write output file
            output_file = OUTPUT_DIR / f"SOP-{tid}.md"
            output_file.write_text(md_content, encoding="utf-8")
            
            print(f"✅ Converted: {tid} -> {output_file.name}")
            converted += 1
            
        except Exception as e:
            print(f"❌ Failed to convert {case_file}: {e}")
    
    # Create index file
    index_md = f"""# Skilling Cases Knowledge Base

Generated from data/cases on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

This folder contains SOP documents derived from training case scenarios.
Each document includes:
- Correct SOP steps (SME approved)
- Learning objectives
- Common mistakes to avoid
- Customer de-escalation techniques
- Coaching checkpoints

## Available Cases

"""
    for case_file in case_files:
        try:
            case_data = json.loads(case_file.read_text(encoding="utf-8"))
            tid = case_data.get("ticket_id", case_file.stem)
            title = case_data.get("title", "Untitled")
            skill = case_data.get("primary_skill", "General")
            index_md += f"- **SOP-{tid}**: {title} ({skill})\n"
        except:
            pass
    
    (OUTPUT_DIR / "README.md").write_text(index_md, encoding="utf-8")
    
    print(f"\n✅ Converted {converted} cases to {OUTPUT_DIR}")
    print(f"\n📋 Next steps:")
    print(f"   1. Run: python -m examples.uta_ingest_knowledge --clear")
    print(f"   2. Or: python -m examples.uta_ingest_knowledge  (to add without clearing)")


if __name__ == "__main__":
    main()
