import json
import os

PRESETS_PATH = os.path.join(os.path.dirname(__file__), 'presets.json')

# Minimal safe fallback when presets.json is missing or invalid.
DEFAULT_PRESETS = {
    'composition': {
        'quality': ['masterpiece'],
    },
    'action': {
        'action': ['standing'],
    },
    'character': {
        'hair_color': ['black hair'],
    },
    'environment': {
        'location': ['studio'],
    },
    'preset_character': {
        'preset_character': ['original character'],
    },
    'style_preset': {
        'style_preset': ['anime'],
    },
    'nsfw': {
        'intensity': ['suggestive'],
    },
}


def sanitize_options(options):
    """Return cleaned string options while preserving input order."""
    cleaned = []
    if not isinstance(options, list):
        return cleaned

    for value in options:
        text = str(value).strip()
        if not text:
            continue
        cleaned.append(text)
    return cleaned


def ensure_none_option(options):
    """Prepend 'None' and remove duplicates while preserving order."""
    unique = []
    for value in options:
        if value is None:
            continue
        text = str(value).strip()
        if not text or text in unique or text == 'None':
            continue
        unique.append(text)
    return ['None'] + unique


def sanitize_section(section):
    """Return a cleaned ordered mapping of field -> options."""
    if not isinstance(section, dict):
        return {}

    sanitized = {}
    for field, options in section.items():
        field_name = str(field).strip()
        if not field_name:
            continue
        sanitized[field_name] = sanitize_options(options)
    return sanitized


def load_presets():
    """Load presets.json and merge minimal fallbacks for required sections."""
    try:
        with open(PRESETS_PATH, 'r', encoding='utf-8') as handle:
            data = json.load(handle)
    except Exception:
        data = {}

    if not isinstance(data, dict):
        data = {}

    sanitized = {}
    for section_name, section in data.items():
        sanitized_name = str(section_name).strip()
        if not sanitized_name:
            continue
        sanitized[sanitized_name] = sanitize_section(section)

    for section_name, fallback_section in DEFAULT_PRESETS.items():
        if section_name not in sanitized or not sanitized[section_name]:
            sanitized[section_name] = sanitize_section(fallback_section)

    return sanitized


def get_section_fields(section_name):
    """Get the ordered field mapping for one presets section."""
    presets = load_presets()
    section = presets.get(section_name)
    if not isinstance(section, dict) or not section:
        return sanitize_section(DEFAULT_PRESETS.get(section_name, {}))
    return section


def clean_value(value):
    """Normalize values and drop empty or explicit None selections."""
    if value is None:
        return ''

    text = str(value).strip()
    if not text or text == 'None':
        return ''
    return text


def combine_texts(*parts):
    """Join parts with commas while cleaning spacing and empty values."""
    cleaned_parts = []
    for part in parts:
        text = clean_value(part)
        if text:
            cleaned_parts.append(text)

    combined = ', '.join(cleaned_parts)
    while ',,' in combined:
        combined = combined.replace(',,', ',')
    combined = ' '.join(combined.split())
    return combined.strip(' ,')


class SectionNodeBase:
    CATEGORY = 'Prompt'
    RETURN_TYPES = ('STRING',)
    FUNCTION = 'build'
    SECTION = ''
    OUTPUT_NAME = ''

    @classmethod
    def get_section_fields(cls):
        return get_section_fields(cls.SECTION)

    @classmethod
    def INPUT_TYPES(cls):
        required = {}
        for field_name, options in cls.get_section_fields().items():
            required[field_name] = (ensure_none_option(options),)
        required.update(cls.extra_inputs())
        return {'required': required}

    @classmethod
    def extra_inputs(cls):
        return {}

    def build(self, **kwargs):
        combined = self.combine_kwargs(kwargs)
        return self.format_output(combined, kwargs)

    @classmethod
    def combine_kwargs(cls, kwargs):
        parts = []
        for field_name in cls.get_section_fields():
            parts.append(kwargs.get(field_name, ''))
        return combine_texts(*parts)

    def format_output(self, combined, kwargs):
        return (combined,)


class CompositionNode(SectionNodeBase):
    SECTION = 'composition'
    OUTPUT_NAME = 'composition'
    RETURN_NAMES = ('composition',)


class ActionNode(SectionNodeBase):
    SECTION = 'action'
    OUTPUT_NAME = 'action'
    RETURN_NAMES = ('action',)


class CharacterNode(SectionNodeBase):
    SECTION = 'character'
    OUTPUT_NAME = 'character'
    RETURN_NAMES = ('character',)

    def format_output(self, combined, kwargs):
        if not combined:
            return ('',)
        return (combined,)


class EnvironmentNode(SectionNodeBase):
    SECTION = 'environment'
    OUTPUT_NAME = 'environment'
    RETURN_NAMES = ('environment',)


class PresetCharacterNode(SectionNodeBase):
    SECTION = 'preset_character'
    OUTPUT_NAME = 'preset_character'
    RETURN_NAMES = ('preset_character',)

    @classmethod
    def extra_inputs(cls):
        return {
            'weight_style': (
                ['none', 'slight emphasis', 'medium emphasis', 'strong emphasis'],
                {'default': 'none'},
            ),
        }

    def format_output(self, combined, kwargs):
        if not combined:
            return ('',)

        weight_style = str(kwargs.get('weight_style', 'none')).strip().lower()

        if weight_style == 'slight emphasis':
            return (f'({combined})',)
        if weight_style == 'medium emphasis':
            return (f'(({combined}))',)
        if weight_style == 'strong emphasis':
            return (f'((({combined})))',)

        return (combined,)


class StylePresetNode(SectionNodeBase):
    SECTION = 'style_preset'
    OUTPUT_NAME = 'style'
    RETURN_NAMES = ('style',)


class NSFWNode(SectionNodeBase):
    SECTION = 'nsfw'
    OUTPUT_NAME = 'nsfw'
    RETURN_NAMES = ('nsfw',)


class CombinePromptNode:
    CATEGORY = 'Prompt'
    RETURN_TYPES = ('STRING', 'STRING')
    RETURN_NAMES = ('positive_prompt', 'negative_prompt')
    FUNCTION = 'build'

    @classmethod
    def INPUT_TYPES(cls):
        return {
            'required': {
                'composition': ('STRING', {'default': ''}),
                'preset_character': ('STRING', {'default': ''}),
                'character': ('STRING', {'default': ''}),
                'action': ('STRING', {'default': ''}),
                'environment': ('STRING', {'default': ''}),
                'nsfw': ('STRING', {'default': ''}),
                'style_preset': ('STRING', {'default': ''}),
                'positive_prompt_text': ('STRING', {'multiline': True, 'default': ''}),
                'negative_prompt_text': (
                    'STRING',
                    {
                        'multiline': True,
                        'default': 'score_6, score_5, score_4, source_pony, (worst quality:1.2), (low quality:1.2), (normal quality:1.2), lowres, bad anatomy, bad hands, signature, watermarks, ugly, imperfect eyes, skewed eyes, unnatural face, unnatural body, error, extra limb, missing limbs',
                    },
                ),
            }
        }

    def build(
        self,
        composition='',
        preset_character='',
        character='',
        action='',
        environment='',
        nsfw='',
        style_preset='',
        positive_prompt_text='',
        negative_prompt_text='',
    ):
        positive_prompt = combine_texts(
            style_preset,
            composition,
            preset_character,
            character,
            action,
            environment,
            nsfw,
            positive_prompt_text,
        )
        negative_prompt = combine_texts(negative_prompt_text)
        return (positive_prompt, negative_prompt)
