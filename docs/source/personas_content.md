# Persona Configuration & Discovery

This project uses a file-based discovery system for LLM personas. To add a new persona, you must follow the naming convention to ensure the `LLMClient` and test suite can communicate correctly.

## Naming Convention

Personas are defined in the `data/personas/` directory as `.yaml` files. The system performs a **Snake Case to Title Case** transformation for internal registration.


| File Name (`.yaml`) | Internal Persona Name | Test Parameter  |
| :-------------------- | :---------------------- | :---------------- |
| `architect.yaml`    | `Architect`           | `"Architect"`   |
| `tech_lead.yaml`    | `Tech Lead`           | `"Tech Lead"`   |
| `modeling_ds.yaml`  | `Modeling Ds`         | `"Modeling Ds"` |

### Rule of Thumb

1. **Filename**: Always use `lowercase_with_underscores.yaml`.
2. **Transformation**: The system replaces underscores with spaces and capitalizes every word (`.title()`).
3. **Tests**: Your `@pytest.mark.parametrize` must match the **Internal Persona Name** (case-insensitive).

## Schema Requirements

Every persona file must contain a `system_prompt` key. Multi-line strings must use the YAML pipe `|` operator with proper 2-space indentation:

```yaml
persona_name: "Lead Scientist"
system_prompt: |
  Role: {persona_name}
  Context: {context}
  Stats: {stats}
```
