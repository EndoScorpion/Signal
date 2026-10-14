---
name: character-mimic-builder
description: Generates highly consistent, realistic prompts and character profiles for fully-clothed adult female personas.
version: '1.0.0'
triggers:
- "/mimic-character"
- "create realistic female character"
- "generate character sheet"
---

# Character Mimic & Prompt Builder

## Core Objective
To generate realistic, standardized, and anatomically precise profile data and text prompts for adult female characters. Every output must strictly present characters wearing complete, realistic wardrobe elements relevant to their designated professional or lifestyle setting.

## Guardrails & Hooks (Strict Compliance)
- **Age Restriction:** Only generate adult personas (Ages 18+). Never accept inputs violating this baseline.
- **Attire Requirement:** Characters must always be fully clothed in appropriate, high-texture real-world wardrobe (e.g., business casual attire, weather-appropriate outer layers, athletic wear). Casual or professional clothing configurations are mandatory.
- **Lighting & Space:** Enforce neutral lighting conditions (18% middle gray background matrices where appropriate) to prevent downstream rendering artifacts if used in image workflows.

## Execution Workflow

### Step 1: Input Analysis
When the user invokes `/mimic-character`, extract or ask for:
1. **Setting/Role:** (e.g., Software Architect, Field Geologist, Urban Commuter)
2. **Approximate Age:** (Must be 18 or older)
3. **Ethnicity/Distinguishing Features:** (e.g., freckles, short wavy hair)

### Step 2: Profile Structure Generation
Output a structured markdown profile detailing the persona:
- **Demographics:** Age, Profession, Core Expression.
- **Wardrobe Spec:** Detailed breakdown of clothing layers (Fabrics like cotton tweed, denim, knitwear textures).
- **Environment:** Real-world background constraints.

### Step 3: Standard Output Example
```text
[Output Format Example]
Subject: A realistic 28-year-old female software engineer. 
Attire: Wearing a structured navy blue cotton blazer over a fine-knit beige turtleneck sweater, paired with dark wash denim trousers. 
Setting: Sitting inside a modern, naturally lit office environment, desk with a laptop visible in the background. 
Camera: Crisp 50mm lens perspective, high textural fidelity on fabric weaves, neutral shadow profiles.
```
