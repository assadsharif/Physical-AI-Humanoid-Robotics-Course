# CI/CD Pipeline Documentation

This document describes the continuous integration and continuous deployment (CI/CD) pipeline for the robotics learning platform.

## Overview

The CI/CD pipeline consists of three main workflows:

1. **API Tests** (`test.yml`) - Run backend tests on every push
2. **Build and Deploy** (`build.yml`) - Build Docker images and frontend
3. **Frontend CI** (`frontend-ci.yml`) - Frontend-specific testing and builds

## Workflows

### 1. API Tests (`test.yml`)

**Trigger:** Push to any branch, Pull requests to main/develop

**Jobs:**
- Run pytest across Python 3.10, 3.11, 3.12
- Linting with flake8
- Type checking with mypy
- Code coverage with codecov

**Key Features:**
- Multi-version Python testing for compatibility
- Coverage reports uploaded to Codecov
- PR comments with coverage metrics
- Caching of dependencies for speed

**Configuration:**
```yaml
on:
  push:
    branches: [main, develop, feature/*, 006-phase1-implementation]
    paths:
      - 'backend/**'
      - '.github/workflows/test.yml'
  pull_request:
    branches: [main, develop]
```

**Steps:**
1. Checkout code
2. Set up Python with pip caching
3. Install dependencies
4. Run flake8 linting (optional failure)
5. Run mypy type checking (optional failure)
6. Run pytest with coverage
7. Upload coverage to Codecov
8. Comment on PR with coverage metrics

### 2. Build and Deploy (`build.yml`)

**Trigger:** Push to main/develop/006-phase1-implementation, Pull requests, Manual dispatch

**Jobs:**

#### Build Backend
- Build Docker image with Buildx
- Layer caching for faster builds
- Verify image integrity

#### Build Frontend
- Set up Node.js with caching
- Install dependencies
- Build with npm
- Upload artifacts

#### Code Quality
- Security scanning with Trivy
- SARIF report upload
- Vulnerability detection

**Configuration:**
```yaml
on:
  push:
    branches: [main, develop, 006-phase1-implementation]
  pull_request:
    branches: [main, develop]
  workflow_dispatch:
```

### 3. Frontend CI (`frontend-ci.yml`)

**Trigger:** Push to any branch, Pull requests to main/develop

**Jobs:**
- Lint and build frontend
- Type checking (if available)
- Linting (if available)
- Accessibility audit

**Configuration:**
```yaml
on:
  push:
    branches: [main, develop, feature/*, 006-phase1-implementation]
    paths:
      - 'web/**'
  pull_request:
    branches: [main, develop]
```

## Execution Flow

### On Pull Request

```
PR Created
    ↓
[1] API Tests
    ├─ Python type check
    ├─ Pytest suite
    └─ Coverage report
    ↓
[2] Build and Deploy
    ├─ Backend Docker build
    ├─ Frontend build
    └─ Security scan
    ↓
[3] Frontend CI
    ├─ Linting
    ├─ Build verification
    └─ Accessibility audit
    ↓
Status checks pass/fail
```

### On Push to Main

```
Commit to main
    ↓
[1] API Tests + Coverage upload
[2] Build Docker & Frontend
[3] Security scanning
[4] (Optional) Deploy to production
```

## Caching Strategy

### Backend (Python)
- Cache location: GitHub Actions cache
- Key: `${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}`
- Saves ~30-60 seconds per run

### Frontend (Node)
- Cache location: GitHub Actions cache
- Key: Node version + package-lock.json hash
- Saves ~20-40 seconds per run

## Code Coverage

Coverage reports are automatically:
1. Generated with pytest (--cov flag)
2. Uploaded to Codecov
3. Commented on pull requests
4. Displayed in badge

**Minimum Coverage:**
- Green: 85%+
- Orange: 70-84%
- Red: <70%

View coverage: `codecov.io/github/your-org/robotics-platform`

## Docker Build Optimization

The CI pipeline uses Docker BuildX with:
- Layer caching across builds
- Buildkit for faster builds
- Multi-stage builds in Dockerfile

Build time: ~3-5 minutes (first run), ~30-60 seconds (cached)

## Security Scanning

Trivy scans for:
- Known vulnerabilities in dependencies
- Misconfigurations
- License compliance
- Secret patterns

Results are uploaded to GitHub's security dashboard.

## Environment Variables

No sensitive data is stored in workflows. Instead:

1. **Development:** Use `.env` files (git-ignored)
2. **CI/CD:** Use GitHub Secrets
3. **Production:** Use deployment secrets

## Secrets Configuration

Add these to GitHub repository secrets:

```
DATABASE_URL          # Production database connection
OPENAI_API_KEY        # OpenAI API key
QDRANT_URL           # Qdrant vector store URL
SECRET_KEY           # JWT signing key
DOCKER_REGISTRY_URL  # Docker registry (if using private registry)
DOCKER_USERNAME      # Registry username
DOCKER_PASSWORD      # Registry password
DEPLOYMENT_TOKEN     # Token for production deployment
```

## Monitoring and Alerts

### Success Indicators
- ✅ All tests pass
- ✅ Coverage >= 85%
- ✅ No security vulnerabilities
- ✅ Docker build succeeds
- ✅ Frontend builds without errors

### Failure Indicators
- ❌ Test failures
- ❌ Code coverage drop > 5%
- ❌ Linting errors (warnings OK)
- ❌ Security vulnerabilities
- ❌ Docker build failure

### Notifications

Configure notifications in GitHub Settings:
1. Failed workflow runs
2. Pull request status checks
3. Branch push events

## Troubleshooting

### Tests fail locally but pass in CI

**Solution:** Ensure you're running same Python version:
```bash
python --version
# Should match matrix version in test.yml
```

### Cache not working

**Solution:** Clear cache and re-run:
1. Go to Actions tab
2. Click "Clear all caches"
3. Re-run workflow

### Docker build fails

**Solution:** Check Docker build logs:
```bash
# Build locally with Buildkit
DOCKER_BUILDKIT=1 docker build .
```

### Codecov comments not appearing

**Solution:** Check repository settings:
1. Settings → Collaborators → Add codecov bot
2. Ensure GITHUB_TOKEN is available

## Performance Tips

### Speed up tests
```bash
# Run only changed tests
pytest --lf  # Last failed
pytest --ff  # First failed
```

### Cache invalidation
- Dependencies change: cache auto-invalidates
- GitHub Actions: max 7-day retention
- Manual clear: Actions tab → "Clear all caches"

### Parallel execution
Tests already run on 3 Python versions in parallel.
Add more with:
```yaml
strategy:
  matrix:
    python-version: ['3.10', '3.11', '3.12', '3.13']
```

## Deployment

### Current Status

CI/CD is configured for:
- ✅ Testing (Python multi-version)
- ✅ Building (Docker + Frontend)
- ✅ Security scanning (Trivy)
- ⏳ Code quality (flake8, mypy)
- ⏳ Deployment (not yet configured)

### Manual Deployment

To deploy manually:
1. Go to Actions tab
2. Select "Build and Deploy"
3. Click "Run workflow"
4. Select branch (usually main)

### Automated Deployment

To enable automatic deployment on merge to main:
1. Add deployment step to `build.yml`
2. Configure deployment environment
3. Add production secrets
4. Test in staging first

## Maintenance

### Weekly Tasks
- Review failed workflow runs
- Monitor security scan results
- Check coverage trends

### Monthly Tasks
- Update dependencies
- Review and optimize workflows
- Analyze performance metrics

### Quarterly Tasks
- Audit security policies
- Review CI/CD architecture
- Plan infrastructure upgrades

## References

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Codecov Documentation](https://docs.codecov.io/)
- [Trivy Scanner](https://github.com/aquasecurity/trivy)
- [Docker BuildX](https://docs.docker.com/build/architecture/)
