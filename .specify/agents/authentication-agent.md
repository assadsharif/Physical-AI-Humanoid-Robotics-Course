# Authentication & User Management Agent

**Purpose**: Handle user authentication, authorization, and personalized learning features.

**Responsibilities**:
- better-auth integration for sign-up/login
- Session management
- User profile management
- Progress tracking and persistence
- Personalization preferences (language, theme)
- Password reset and account management

**Technologies**:
- better-auth (authentication framework)
- Neon Postgres (user data storage)
- JWT tokens (session management)
- Email service (password reset, notifications)

**Authentication Flows**:
- Sign-up with email verification
- Login with email/password
- Logout and session expiry (24 hours)
- Password reset via email link
- Profile update and preferences

**User Profile Schema**:
- email (unique, verified)
- password_hash (bcrypt)
- name
- language_preference (EN, UR)
- theme_preference (light, dark)
- created_at, last_login
- email_verified_at

**Personalized Features**:
- Progress dashboard (per-module completion %)
- Quiz scores and history
- Chapter bookmarks
- Learning recommendations
- Language preference persistence

**Quality Metrics**:
- Sign-up/login < 30 seconds
- 99.9% authentication uptime
- Secure password hashing (bcrypt)
- GDPR-compliant data handling

**Owner**: Claude Code Agent (to be assigned)

**Status**: In Planning
