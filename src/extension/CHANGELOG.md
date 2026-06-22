# moonlight-vscode-theme

## 5.5.1 - 2026-06-22

- Fix the ruler color

## 5.5.0 - 2026-06-21

- Resolved overlapping syntax scopes and removed duplicate scope entries, so functions, parameters, object properties, member variables, tags, and inherited classes now resolve to their intended color
- Remapped symbol icons (autocomplete and Outline) to the Moonlight palette, replacing mismatched icon colors
- Improved contrast for input placeholders, terminal bright-black, the column ruler, and the list focus highlight
- Refined UI chrome with more visible borders and lavender-tinted secondary text
- Added theming for previously unstyled UI: diagnostic squiggles, sticky scroll, input validation, menus, shadows, command center, inline/ghost text, AI chat, test explorer, merge conflicts, tab modified indicators, and charts
- Fixed miscolored UI: amber status-bar warning badge (was blue), debug number/boolean values now match editor syntax, and replaced off-palette leftover colors
- Expanded coverage to newer VS Code colors: markdown alerts, chat bubbles and pills, agent sessions, terminal suggest icons, sticky-scroll gutters, and comment-draft glyphs
- Removed an invalid color key that VS Code would have ignored
- Added a schema sync script (`make schema-check` / `make schema-update`) that keeps schema.json in step with the official VS Code theme-color reference

## 5.4.1 - 2026-06-21

- Changes logo

## 5.4.0 - 2026-03-02

- Changes to json key color

## 5.3.2 - 2025-06-25

- Fixed terminal search match colors

## 5.3.1 - 2025-06-15

- Fixed shell argument color

## 5.3.0 - 2025-06-15

- Code cleanup and organization
- Support for more languages
- New `semanticTokenColors` to match `tokenColors` (might help with languages I didn't manually change)

## 5.2.5 - 2025-06-11

- Add Python Notebook screenshot

## 5.2.4 - 2025-06-11

- Fixing screenshots

## 5.2.3 - 2025-06-11

- Screenshots added to the README.md

## 5.2.2 - 2025-06-11

- Initial release of Moonlight 🌌, a brand new dark and blue theme for VS Code.
- Designed to provide a comfortable, elegant, and focused coding experience with reduced eye strain.
- Features a serene palette of deep blues and complementary dark tones for syntax highlighting and UI elements.

## previous versions]

- Present on the github repo: https://github.com/v-amorim/moonlight-vscode-theme
