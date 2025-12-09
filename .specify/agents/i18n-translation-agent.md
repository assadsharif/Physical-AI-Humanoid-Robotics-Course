# Internationalization (i18n) & Translation Agent

**Purpose**: Implement multi-language support with Urdu translation and content versioning.

**Responsibilities**:
- i18n infrastructure setup
- Content translation management (English → Urdu)
- Translation versioning and tracking
- Language preference persistence
- Content metadata for translations

**Technologies**:
- i18next (internationalization framework)
- Neon Postgres (translation storage)
- Markdown translation tooling
- Language detection

**Supported Languages**:
- English (EN) - default
- Urdu (UR) - primary translation

**Translation Scope**:
- Explanatory text (100%)
- Code comments (100%)
- Diagram labels (100%)
- Exercise descriptions (100%)
- Quiz questions and answers (100%)

**Translation Schema**:
```
translations:
  - id: UUID
  - chapter_id: FK
  - language: EN | UR
  - translated_content: markdown
  - translator_id: FK (user)
  - verified_at: timestamp
  - version: semver (1.0.0, 1.0.1, etc.)
  - created_at, updated_at
```

**Features**:
- Language toggle button (top-right corner)
- Per-chapter translation status indicator
- Translation completeness tracking
- Fallback to English if translation unavailable
- Language preference in user profile

**Quality Metrics**:
- Translation completeness: All chapters ≥ 80% translated within 2 weeks
- Translation accuracy: Native speaker review required
- Load time impact < 100ms for language switching
- Support RTL (right-to-left) for Urdu rendering

**Translator Workflow**:
1. Translator selects chapter to translate
2. System shows side-by-side English/Urdu
3. Translator completes translation
4. Reviewer verifies accuracy
5. Translation is published

**Owner**: Claude Code Agent (to be assigned)

**Status**: In Planning
