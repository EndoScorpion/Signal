---
name: dom-state-manager
description: "DOM breakup and restore"
---

To enable Claude to safely backup, break up, test, and restore complex DOM structures within your sandbox, you can implement a structured DOM State Manager Skill. This design addresses limitations like the 5MB domain restrictions in localStorage by breaking massive HTML payload states into smaller, indexed fragments before saving them.
------------------------------
## Step 1: Define the DOM State Tool Schema
Add this JSON definition to Claude's tool integration workspace so it knows how to call the backup, testing, and restoration functions.

{
  "name": "manage_dom_state",
  "description": "Backup, chunk/breakup, test, and restore complex sandboxed HTML DOM states using local storage.",
  "input_schema": {
    "type": "object",
    "properties": {
      "action": {
        "type": "string",
        "enum": ["backup_and_chunk", "restore_and_assemble", "verify_dom_integrity"]
      },
      "state_key": {
        "type": "string",
        "description": "The unique reference key for this DOM state configuration (e.g., 'SignalMonitor_V1')."
      },
      "raw_html": {
        "type": "string",
        "description": "The full string payload of the DOM layout to break up and backup. Only required for backup_and_chunk."
      }
    },
    "required": ["action", "state_key"]
  }
}

------------------------------
## Step 2: Build the Core Sandbox Engine
This JavaScript suite implements the four key components of the skill: backing up the live layout, chunking large sets of data, running localized automated testing, and rebuilding the interactive element tree cleanly.
------------------------------
## Step 3: Implement the App UI Orchestrator
This layout embeds the orchestration middleware so that Claude can trigger backups or verify integrity metrics during active development modifications inside your testing sandbox.

// Middleware execution script inside your sandbox frontend applicationasync function handleDomSkillCall(toolCallRequest) {
  const { action, state_key, raw_html } = toolCallRequest.input;
  
  switch(action) {
    case "backup_and_chunk":
      // 1. Test integrity BEFORE committing layout adjustments to storage
      const integrityCheck = DomStateEngine.verifyDomIntegrity(raw_html);
      if (!integrityCheck.success) {
        return `Backup aborted. Integrity checks failed: ${JSON.stringify(integrityCheck.report)}`;
      }
      // 2. Commit safely to disk cache
      const backupResult = DomStateEngine.backupAndChunk(state_key, raw_html);
      return JSON.stringify(backupResult);

    case "restore_and_assemble":
      const restoreResult = DomStateEngine.restoreAndAssemble(state_key);
      if (restoreResult.success) {
        // Safely inject code payload to refresh active rendering workspace context
        document.getElementById('sandbox-render-frame').srcdoc = restoreResult.html;
        return `Success: State [${state_key}] assembled and fully loaded into target iframe runtime display.`;
      }
      return JSON.stringify(restoreResult);

    case "verify_dom_integrity":
      const checkResult = DomStateEngine.verifyDomIntegrity(raw_html);
      return JSON.stringify(checkResult);
  }
}

If you want to tailor this logic further, let me know:

* Do you want to add GZIP-style text compression to decrease space constraints?
* Should the tool automatically roll back to the previous stable backup if a layout integrity test fails?


