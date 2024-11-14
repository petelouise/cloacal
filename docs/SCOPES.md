# Cloacal TextMate Grammar Scopes

This document explains the TextMate scopes used in the Cloacal language grammar.

## Name Box Section
```json
{
    "name": "meta.name-box.cloacal",          // Container for the entire name box
    "beginCaptures": {
        "1": { "name": "punctuation.definition.heading.cloacal" }  // The +---+ border
    },
    "patterns": [{
        "1": { "name": "entity.name.section.cloacal" }  // The actual name between pipes
    }]
}
```

## Key-Value Lines
```json
{
    "name": "meta.key-value.cloacal",         // Container for key-value pairs
    "captures": {
        "1": { "name": "entity.name.tag.cloacal" },        // The key (e.g., "age", "species")
        "2": { "name": "punctuation.separator.cloacal" },   // The separator (---)
        "3": { "name": "string.unquoted.value.cloacal" }   // The value after the separator
    }
}
```

## Block Headers
```json
{
    "name": "meta.block-header.cloacal",      // Container for block headers
    "captures": {
        "1": { "name": "keyword.control.cloacal" }  // The header word (e.g., "description")
    }
}
```

## List Items
```json
{
    "name": "markup.list.cloacal",            // Container for list items
    "captures": {
        "1": { "name": "keyword.control.cloacal" },         // The > marker
        "2": { "name": "string.unquoted.list-item.cloacal" } // The list item text
    }
}
```

## Block Content
```json
{
    "name": "meta.block-content.cloacal",     // Container for indented block content
    "patterns": [{
        "name": "string.unquoted.block-content.cloacal"  // The actual content text
    }]
}
```

## Common TextMate Scope Patterns

The scopes were chosen to match common TextMate patterns:

- `entity.name.tag`: Used for key identifiers, commonly colored distinctly in themes
- `punctuation.separator`: Used for separators like the dashes
- `keyword.control`: Used for significant markers and control elements
- `string.unquoted`: Used for general text content
- `markup.list`: Used for list-related structures
- `meta.*`: Used as containers to group related elements

These scopes are widely supported by VSCode themes and should provide consistent coloring across different theme choices.
