# Installing the Charmcraft Skill

Quick guide to installing and using the charmcraft skill with Claude.

## For Claude Code

### Method 1: Personal Skills (Recommended)

Install globally for all your projects:

```bash
# Copy to personal skills directory
mkdir -p ~/.claude/skills
cp -r charmcraft-skill ~/.claude/skills/

# Verify installation
ls -la ~/.claude/skills/charmcraft-skill/
```

The skill will now be available in all Claude Code sessions.

### Method 2: Project-Specific

Install for a specific project only:

```bash
# Navigate to your project
cd /path/to/your/project

# Create skills directory
mkdir -p .claude/skills

# Copy skill
cp -r /path/to/charmcraft-skill .claude/skills/

# Verify installation
ls -la .claude/skills/charmcraft-skill/
```

The skill will only be available when working in this project directory.

### Method 3: Symlink (For Development)

If you're actively developing the skill:

```bash
# Create symlink instead of copying
mkdir -p ~/.claude/skills
ln -s /path/to/charmcraft-skill ~/.claude/skills/charmcraft

# Changes to the skill will be immediately available
```

## For Claude API

### Step 1: Create Skill Archive

```bash
cd charmcraft-skill
zip -r ../charmcraft-skill.zip .
```

### Step 2: Upload via API

```bash
# Using curl
curl -X POST https://api.anthropic.com/v1/skills \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2025-10-02" \
  -H "anthropic-beta: skills-2025-10-02" \
  -F "file=@../charmcraft-skill.zip" \
  -F "name=charmcraft"

# Or using the Anthropic Python SDK
from anthropic import Anthropic

client = Anthropic(api_key="your-api-key")

with open("charmcraft-skill.zip", "rb") as f:
    skill = client.skills.create(
        file=f,
        name="charmcraft"
    )

print(f"Skill ID: {skill.id}")
```

### Step 3: Use in API Calls

```python
from anthropic import Anthropic

client = Anthropic()

message = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=1024,
    container={
        "type": "code_execution",
        "skill_ids": ["charmcraft"]  # Your skill ID
    },
    tools=[{"type": "code_execution_2025-08-25"}],
    messages=[{
        "role": "user",
        "content": "Help me create a new Kubernetes charm"
    }]
)
```

## For Claude.ai

### Step 1: Create ZIP File

```bash
cd charmcraft-skill
zip -r ../charmcraft-skill.zip .
```

### Step 2: Upload to Claude.ai

1. Go to [claude.ai](https://claude.ai)
2. Click on your profile icon (bottom left)
3. Select "Settings"
4. Navigate to "Features" section
5. Find "Skills" section
6. Click "Upload Skill"
7. Select `charmcraft-skill.zip`
8. Wait for upload to complete

### Step 3: Verify

Start a new conversation and ask:
```
"Can you help me with charmcraft?"
```

Claude should recognize and use the skill automatically.

## Verification

After installation, verify the skill works:

### Test Query 1: Basic Command
```
User: "How do I initialize a new Kubernetes charm?"

Expected: Claude provides charmcraft init command with kubernetes profile
```

### Test Query 2: Advanced Workflow
```
User: "Help me build and publish my charm to the edge channel"

Expected: Claude provides pack, analyse, upload workflow
```

### Test Query 3: Configuration Help
```
User: "What should go in charmcraft.yaml for a database integration?"

Expected: Claude provides charmcraft.yaml example with database relation
```

## Troubleshooting

### Skill Not Loading

**Claude Code:**
```bash
# Check skill directory exists
ls -la ~/.claude/skills/charmcraft-skill/SKILL.md

# Check permissions
chmod -R u+r ~/.claude/skills/charmcraft-skill/

# Restart Claude Code
```

**Claude API:**
```bash
# List installed skills
curl https://api.anthropic.com/v1/skills \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2025-10-02" \
  -H "anthropic-beta: skills-2025-10-02"
```

### Skill Not Triggering

The skill should trigger automatically when you mention:
- charmcraft
- charm development
- Juju charms
- Charmhub
- charm libraries
- Building/packing charms

If it's not triggering, try being more explicit:
```
"Using charmcraft, help me..."
"I'm working on a Juju charm and need to..."
```

### Invalid ZIP File

Ensure ZIP doesn't include parent directory:
```bash
# Wrong (includes parent directory)
zip -r charmcraft-skill.zip charmcraft-skill/

# Correct (contents only)
cd charmcraft-skill
zip -r ../charmcraft-skill.zip .
```

## Updating the Skill

### Claude Code

Simply replace the files:
```bash
# Personal skills
cp -r charmcraft-skill ~/.claude/skills/

# Or use rsync to update
rsync -av --delete charmcraft-skill/ ~/.claude/skills/charmcraft-skill/
```

### Claude API

Delete old version and upload new:
```bash
# List skills to get ID
curl https://api.anthropic.com/v1/skills \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2025-10-02" \
  -H "anthropic-beta: skills-2025-10-02"

# Delete old skill
curl -X DELETE https://api.anthropic.com/v1/skills/{skill_id} \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2025-10-02" \
  -H "anthropic-beta: skills-2025-10-02"

# Upload new version
curl -X POST https://api.anthropic.com/v1/skills \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2025-10-02" \
  -H "anthropic-beta: skills-2025-10-02" \
  -F "file=@charmcraft-skill.zip" \
  -F "name=charmcraft"
```

### Claude.ai

1. Go to Settings > Features
2. Remove old skill
3. Upload new zip file

## Uninstalling

### Claude Code
```bash
rm -rf ~/.claude/skills/charmcraft-skill
```

### Claude API
```bash
curl -X DELETE https://api.anthropic.com/v1/skills/{skill_id} \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2025-10-02" \
  -H "anthropic-beta: skills-2025-10-02"
```

### Claude.ai
Settings > Features > Skills > Remove

## Next Steps

After installation:

1. Read [README.md](README.md) for skill overview
2. Check [EXAMPLE-USAGE.md](EXAMPLE-USAGE.md) for usage examples
3. Try the skill with your charmcraft projects
4. Provide feedback for improvements

## Support

For issues with:
- **The skill**: Open an issue in this repository
- **Claude Code**: Check [Claude Code docs](https://code.claude.com/docs)
- **Claude API**: Check [Claude API docs](https://docs.anthropic.com/claude/docs)
- **Charmcraft itself**: See [Charmcraft docs](https://documentation.ubuntu.com/charmcraft/)
