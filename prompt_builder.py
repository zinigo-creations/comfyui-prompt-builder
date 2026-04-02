import json
import os

class PromptBuilder:
    """
    A custom ComfyUI node that builds a prompt string by concatenating
    a base prompt, always tags, and selections from dropdowns loaded from presets.json.
    """

    @classmethod
    def INPUT_TYPES(cls):
        """
        Dynamically builds input types based on presets.json.
        Includes base_prompt and always_tags as required multiline strings,
        and dropdowns for each category in the JSON.
        """
        # Path to presets.json relative to this file
        presets_path = os.path.join(os.path.dirname(__file__), 'presets.json')

        # Load presets (with fallback)
        presets = cls.load_presets(presets_path)

        # Start with required inputs
        inputs = {
            "required": {
                "base_prompt": ("STRING", {"multiline": True}),
                "always_tags": ("STRING", {
                    "multiline": True,
                    "default": "score_9, score_8_up, score_7_up, masterpiece, best quality, high quality, ((global illumination, ray tracing)), detailed, sharp focus"
                }),
            }
        }

        # Add dropdowns for each category in presets
        for category, options in presets.items():
            # Ensure "None" is first, and filter out empty strings
            options_with_none = ["None"] + [opt for opt in options if opt.strip()]
            inputs["required"][category] = (options_with_none,)

        return inputs

    @classmethod
    def load_presets(cls, path):
        """
        Loads presets from JSON file.
        If file is missing or invalid, falls back to defaults.
        Sanitizes data: trims whitespace, ignores empty strings.
        """
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Sanitize: ensure each value is a list of strings, trimmed and non-empty
            sanitized = {}
            for key, value in data.items():
                if isinstance(value, list):
                    sanitized[key] = [str(item).strip() for item in value if str(item).strip()]
                else:
                    # If not a list, treat as empty
                    sanitized[key] = []
            return sanitized
        except (FileNotFoundError, json.JSONDecodeError, Exception):
            # Fallback defaults
            return {
                "environment": ["castle", "alleyway"],
                "clothing": ["armor", "hoodie"]
            }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("prompt",)
    FUNCTION = "build_prompt"
    CATEGORY = "Prompt"

    def build_prompt(self, base_prompt, always_tags, **kwargs):
        """
        Builds the final prompt by concatenating:
        1. base_prompt (if not empty)
        2. always_tags (if not empty)
        3. Each selected dropdown value (if not "None" and not empty), in JSON order
        Separated by ", "
        """
        parts = []

        # Add base_prompt if present
        if base_prompt.strip():
            parts.append(base_prompt.strip())

        # Add always_tags if present
        if always_tags.strip():
            parts.append(always_tags.strip())

        # Load presets to get category order
        presets_path = os.path.join(os.path.dirname(__file__), 'presets.json')
        presets = self.load_presets(presets_path)

        # Add each category's selection if not "None"
        for category in presets.keys():
            value = kwargs.get(category, "None")
            if value != "None" and value.strip():
                parts.append(value.strip())

        # Join with ", "
        return (", ".join(parts),)