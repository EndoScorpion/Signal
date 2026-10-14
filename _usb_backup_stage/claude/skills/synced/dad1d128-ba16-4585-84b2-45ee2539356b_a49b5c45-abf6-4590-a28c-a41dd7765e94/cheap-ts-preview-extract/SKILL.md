---
name: cheap-ts-preview-extract
description: >
  LOW COST (~400 tokens). Bash/Python extraction commands to pull toolbar,
  panel template, CSS, and copyright from an uploaded Trade Signals HTML file.
  Load this AFTER cheap-ts-preview-rules when building a preview from an
  actual uploaded file (not from memory).
---
## Extract commands

```python
with open('/mnt/user-data/uploads/<filename>.html','r') as f:
    c = f.read()

# Copyright
cp_start = c.find('<div class="copyright">')
print(c[cp_start:c.find('</div>',cp_start)+6])

# Toolbar buttons
t1 = c.find('<div id="toolbar">')
print(c[t1:t1+900])

# Snapshot bar
s1 = c.find('<div id="snapshotBar"')
print(c[s1:s1+600])

# Panel template (chart controls + indicator row)
idx = c.find('innerHTML = `\n    <div class="panel-head"')
print(c[idx:idx+3000])

# CSS vars
css_start = c.find('<style>')
print(c[css_start:css_start+2000])
```

## Key selectors
| Section | Marker |
|---|---|
| Toolbar | `id="toolbar"` |
| Snapshot bar | `id="snapshotBar"` |
| Panel template | `` innerHTML = ` `` |
| Chart controls | `.chart-controls` in template |
| Indicator row | `.indicator-row` in template |
| CSS | `<style>` block |
| Copyright | `.copyright` div |

Never load the full 1MB+ file into context — slice only these sections.
