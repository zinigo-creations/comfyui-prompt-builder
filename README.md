# Prompt Builder

Modular ComfyUI custom node package for building SDXL/Pony/Danbooru-style prompts using multiple small nodes.

## Installation

1. Copy `prompt_builder` into `ComfyUI/custom_nodes/`.
2. Restart ComfyUI.

## Nodes

- `Composition`
- `Action`
- `Character`
- `Environment`
- `Preset Character`
- `Style Preset`
- `NSFW`
- `Combine Prompt`

## Basic behavior

- `presets.json` is the source of truth for all section-node dropdown fields and option lists.
- Each inner JSON key becomes one dropdown field, in the same order it appears in the file.
- Each dropdown contains `None` automatically.
- `None` results in no contribution to output.
- Editing a section in `presets.json` changes that node after restarting ComfyUI.
- Section nodes return a single `STRING` output.
- `Combine Prompt` remains manually defined and stitches non-empty parts with commas.

## Node details

### Composition

Uses the `composition` section from `presets.json`.

### Action

Uses the `action` section from `presets.json`.

### Character

Uses the `character` section from `presets.json`.
Includes a `weight` float control. If the combined character text is not empty and `weight != 1.0`, the output is formatted as `(combined_text:weight)`.

### Environment

Uses the `environment` section from `presets.json`.

### Preset Character

Uses the `preset_character` section from `presets.json`.

### Style Preset

Uses the `style_preset` section from `presets.json`.

### NSFW

Uses the `nsfw` section from `presets.json`.

### Combine Prompt

Inputs: `composition`, `preset_character`, `character`, `action`, `environment`, `nsfw`, `style_preset`, `positive_prompt_text`, `negative_prompt_text`.
Outputs: `positive_prompt`, `negative_prompt`.

- `positive_prompt_text` is an editable multiline text box for extra positive prompt text.
- `negative_prompt_text` is an editable multiline text box for the negative prompt.
- `positive_prompt` combines values in this order: `style_preset`, `composition`, `preset_character`, `character`, `action`, `environment`, `nsfw`, `positive_prompt_text`.
- `negative_prompt` passes through the cleaned value of `negative_prompt_text`.
- Empty values, whitespace-only values, and `None` values are ignored.

## Editing `presets.json`

- `presets.json` drives these section nodes: `Composition`, `Action`, `Character`, `Environment`, `Preset Character`, `Style Preset`, and `NSFW`.
- Each top-level section maps to one node.
- Each inner key becomes a dropdown field in that node.
- Each inner array becomes the dropdown options for that field.
- Field order is preserved exactly as written in the JSON file.
- If you add or remove a field in a section, the matching node changes after restarting ComfyUI.
- If a field list is empty, the node still shows that dropdown with `None`.
- If a section is missing or invalid, code falls back to a minimal safe default.
- Restart ComfyUI after editing `presets.json`.

## Example workflow

1. Use builder nodes to create composition/action/character/environment/preset/style/nsfw.
2. Add optional custom text in `positive_prompt_text` and `negative_prompt_text` on `Combine Prompt`.
3. Connect `Combine Prompt positive_prompt` to positive CLIP Text Encode.
4. Connect `Combine Prompt negative_prompt` to negative CLIP Text Encode.

Recommended positive path:
`Composition/Action/Character/Environment/Preset/Style/NSFW -> Combine Prompt -> positive CLIP Text Encode`

Recommended negative path:
`Combine Prompt negative_prompt -> negative CLIP Text Encode`

## Notes

- No ComfyUI internals imported; only Python stdlib.
- Safe fallback is implemented for missing or invalid `presets.json` sections.
- Section nodes read field definitions dynamically from JSON and no longer duplicate the schema in Python.
- All nodes are stable and do not crash on empty field values.
