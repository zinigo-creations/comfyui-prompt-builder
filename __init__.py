from .nodes import (
    CompositionNode,
    ActionNode,
    CharacterNode,
    EnvironmentNode,
    PresetCharacterNode,
    StylePresetNode,
    NSFWNode,
    CombinePromptNode,
)

NODE_CLASS_MAPPINGS = {
    "CompositionNode": CompositionNode,
    "ActionNode": ActionNode,
    "CharacterNode": CharacterNode,
    "EnvironmentNode": EnvironmentNode,
    "PresetCharacterNode": PresetCharacterNode,
    "StylePresetNode": StylePresetNode,
    "NSFWNode": NSFWNode,
    "CombinePromptNode": CombinePromptNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "CompositionNode": "Composition",
    "ActionNode": "Action",
    "CharacterNode": "Character",
    "EnvironmentNode": "Environment",
    "PresetCharacterNode": "Preset Character",
    "StylePresetNode": "Style Preset",
    "NSFWNode": "NSFW",
    "CombinePromptNode": "Combine Prompt",
}
