# Config Generator Implementation Plan

## 1. Goal

Add a static Config generator deployed through GitHub Pages. It only generates
`DOUYIN_CONFIG`; it does not process cookies and does not change the existing
Python sending workflow.

## 2. Configuration Compatibility

Use `app/config.py` as the source of truth for the frontend data model and
validation rules.

Supported configuration structures:

- Basic format: `friends + messages`
- Advanced format: `targets`
- Message types: `text`, `sticker` / `douyin_sticker`, and `random`
- Sticker mapping: `label`, `category`, and `fallback_index`
- `task_id`
- `timezone`
- `send_interval_seconds`
- `continue_on_error`
- `prevent_duplicates`
- `target_open_retries`
- `target_open_timeout_seconds`

The first version will not provide a visual image-message editor. Existing
image configurations can still be retained and edited in raw JSON mode.

## 3. File Structure

```text
web/
|-- index.html
|-- styles.css
|-- config-core.js
`-- app.js

tests/web/
`-- config-core.test.js

.github/workflows/
`-- pages.yml
```

Responsibilities:

- `index.html`: page structure and accessible form labels
- `styles.css`: responsive utility interface
- `config-core.js`: configuration conversion, validation, import, and export
- `app.js`: form interaction and DOM rendering
- `config-core.test.js`: dependency-free tests for core configuration logic
- `pages.yml`: automated GitHub Pages deployment

No React, Vue, Tailwind, package manager, or build system will be introduced.

## 4. Basic Mode

The basic mode will provide:

- Batch friend-name input
- Add, remove, and reorder messages
- Text-message editing
- Native sticker selection
- Sticker name, category, and fallback index
- Minimum and maximum sending intervals
- Duplicate-prevention toggle
- Continue-on-error toggle
- Target-open retry count and timeout

Basic mode generates the `friends + messages` format.

## 5. Advanced Mode

The advanced mode will provide:

- Per-friend message configuration
- Add, remove, and reorder targets
- Per-target text, sticker, and random messages
- `random.choices` editing
- Basic-mode to `targets` conversion
- Raw JSON editing synchronized with the visual form

Advanced mode generates the `targets` format.

## 6. Import

Supported import methods:

- Select an existing `config.json`
- Drag and drop a JSON file
- Paste JSON text
- Automatically detect basic or advanced format
- Validate before replacing the current form
- Warn about unsupported or unknown fields
- Never silently discard unsupported fields
- Keep the current form unchanged when import validation fails

## 7. Validation

Validation will mirror the Python configuration parser:

- Friend or target lists cannot be empty
- Friend names cannot be empty
- Message lists cannot be empty
- Text content cannot be empty
- Referenced stickers must have mappings
- `fallback_index` must be a non-negative integer
- Sending intervals must satisfy `0 <= min <= max`
- Retry counts must be non-negative integers
- Timeout values must be greater than zero
- Boolean settings must use boolean values
- Random choices cannot be empty
- Random messages cannot contain nested random messages

Errors will include precise paths, for example:

```text
targets[1].messages[0].value cannot be empty
```

Duplicate friend names produce warnings but do not block export, allowing test
and stress configurations.

## 8. Preview and Export

The interface will show formatted JSON in real time and provide:

- Copy JSON
- Download `config.json`
- Reset configuration
- Import configuration
- Current format indicator
- Friend and message counts

Downloads are disabled when errors exist. Warnings do not block export.

Generated JSON can be pasted directly into the GitHub Secret:

```text
DOUYIN_CONFIG
```

## 9. Privacy

- All processing happens in the browser
- No configuration data is uploaded
- No analytics or external tracking is included
- Configuration is not saved to `localStorage`
- Refreshing or closing the page clears the current data
- The page does not process cookies
- Cookie values are rejected if entered into configuration fields

## 10. Interface Design

Desktop layout:

```text
Top toolbar and Basic/Advanced mode switch

Configuration form | JSON preview and validation
```

Mobile layout:

```text
Toolbar
Configuration form
JSON preview
Copy and download actions
```

Design requirements:

- Compact, quiet, utility-focused interface
- No marketing landing page or hero section
- No external fonts
- No horizontal scrolling from 375px to 1440px
- Visible labels and inline validation errors
- Full keyboard operation
- Minimum 44px interactive targets
- Visible focus states
- System light and dark mode support

## 11. GitHub Pages Deployment

The Pages workflow will:

- Run when `web/**` changes on `main`
- Upload `web/` as the Pages artifact
- Deploy using the official `deploy-pages` action
- Require no server or database

Expected URL:

```text
https://unmev.github.io/douyin-auto-fire/
```

The repository must enable GitHub Actions as its Pages source once:

```text
Settings -> Pages -> Source -> GitHub Actions
```

## 12. Testing

Automated tests will cover:

- Basic configuration generation
- Advanced configuration generation
- Basic and advanced format conversion
- Importing existing configurations
- Text-only messages
- Sticker-only messages
- Text and sticker combinations
- Random messages
- Invalid fields and values
- Preservation of unsupported fields
- Downloaded JSON content

Page verification will cover:

- 375x812 mobile viewport
- 768x1024 tablet viewport
- 1440x900 desktop viewport
- Import, copy, and download workflows
- Keyboard navigation
- Dark mode
- Browser console errors

Generated JSON will also be passed to the Python `load_task()` parser to verify
compatibility without executing a real message send.

## 13. Acceptance Criteria

- Users do not need to write JSON manually
- Basic and advanced configurations can be generated
- Existing configurations can be imported
- Downloaded files are accepted by the Python application
- Generated JSON can be copied directly into `DOUYIN_CONFIG`
- No backend, cookie handling, or data upload is introduced
- GitHub Pages deploys automatically
- The interface works on mobile and desktop
