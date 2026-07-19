"""Central semantic labels and patterns used by the runtime v7 pipeline."""

CONTENT_LABEL_REALISTIC_STORY = "gerçekçi öykü"
CONTENT_LABEL_VALUES_EDUCATION = "değerler eğitimi"
GENERIC_STATE_CHANGE_EFFECT = "durum değişimi"

# Historical exploration phrases are domain patterns, not generic event rules.
# Values and ordering intentionally preserve the existing deterministic behavior.
HISTORICAL_EXPLORATION_PATTERNS = {
    "new_world_graph_markers": ("yeni dünya",),
    "new_world_goal_markers": ("yeni dünya",),
    "new_world_objects": (
        ("yeni bir dünya", "Yeni bir dünya"),
        ("yeni dünya", "Yeni dünya"),
    ),
    "new_world_action_markers": (
        "yeni bir dünya keşfettik",
        "yeni bir dünya keşfetti",
    ),
    "new_world_action": "yeni bir dünya keşfetti",
    "atlas_ocean_locations": (("atlas okyanusu", "Atlas Okyanusu"),),
}
