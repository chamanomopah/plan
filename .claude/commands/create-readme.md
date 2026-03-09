---
description: Generate practical README.md for end users. Analyzes project structure and creates usage documentation with real use cases.
argument-hint: [output-path]
allowed-tools: Read, Write, Glob, Grep, Bash
---

# Generate User-Friendly README

Generate a practical, direct README.md for end users based on project analysis.

## Variables

- `output_path`: $1 - Path for README file (default: README.md)

## Purpose

Creates user-friendly documentation that answers: **"How do I use this?"**

Focus on practical use cases, not implementation details.

## Instructions

### 1. Analyze Project Structure

Understand the project:

```bash
# List main files
ls -la

# Find configuration files
find . -name "*.json" -o -name "*.yaml" -o -name "*.toml" | head -20

# Find documentation
find . -name "*.md" -o -name "README*" | head -20

# Check for main entry points
find . -name "main.*" -o -name "index.*" -o -name "app.*" | head -10
```

### 2. Identify Key Components

Look for:
- Entry points (main.py, index.html, app.js, etc.)
- Configuration files
- Documentation/specifications
- Project structure and organization
- Dependencies (requirements.txt, package.json, etc.)

### 3. Read Key Files

```bash
# Read specification files
cat specs/*.md 2>/dev/null || true

# Read configuration
cat *.json 2>/dev/null || true

# Read existing documentation
cat docs/*.md 2>/dev/null || true
```

### 4. Generate README

Create a practical, user-focused README with this format:

```markdown
# [Project Name]

**One-line description of what this project does**

## What It Does

[2-3 sentences explaining the main purpose and value proposition]

## Quick Start

### Prerequisites
- [Requirement 1]
- [Requirement 2]

### Installation

```bash
# Installation commands
[commands here]
```

### Basic Usage

```bash
# Basic usage commands
[commands here]
```

## How It Works

[Simple explanation of the core concept - what connects to what]

**Key Components:**
- **Component 1**: [What it does in user terms]
- **Component 2**: [What it does in user terms]
- **Component 3**: [What it does in user terms]

## Real Use Cases

### Use Case 1: [Practical Title]

**Scenario**: [Real-world situation]

**Steps**:
1. [Action 1]
2. [Action 2]
3. [Action 3]

**Result**: [What happens]

### Use Case 2: [Practical Title]

**Scenario**: [Real-world situation]

**Steps**:
1. [Action 1]
2. [Action 2]

**Result**: [What happens]

## Configuration

### [Config File 1]

```json
{
  "setting": "value"
}
```

**What it does**: [Explanation in user terms]

### [Config File 2]

```yaml
setting: value
```

**What it does**: [Explanation in user terms]

## Project Structure

```
[Directory tree showing important files/directories]
```

**Important Files**:
- `[file]`: [What it's for]
- `[file]`: [What it's for]

## Common Tasks

### [Task 1]

**How to do it**: [Direct steps]

**Example**:
```bash
[command or code]
```

### [Task 2]

**How to do it**: [Direct steps]

**Example**:
```bash
[command or code]
```

## Troubleshooting

### [Problem 1]

**Symptom**: [What you see]

**Solution**: [How to fix it]

### [Problem 2]

**Symptom**: [What you see]

**Solution**: [How to fix it]

## Tips & Best Practices

- [Tip 1]
- [Tip 2]
- [Tip 3]

## Need Help?

- [Documentation link or location]
- [Support contact or method]
- [Community resource]
```

### 5. Writing Guidelines

**BE DIRECT**:
- ✅ "Install dependencies: `pip install -r requirements.txt`"
- ❌ "In order to begin using the application, you should first proceed to install the required dependencies..."

**BE PRACTICAL**:
- ✅ Use real commands that work
- ❌ Use placeholder commands that don't exist

**FOCUS ON USERS**:
- ✅ "To edit a file, click the file in the sidebar"
- ❌ "The file selection mechanism operates via sidebar interaction..."

**REAL EXAMPLES**:
- ✅ Use actual file names from the project
- ✅ Show real configuration values
- ❌ Use generic placeholders like `[your-file]`

## Output

Return ONLY the path to the created README:

```text
README.md
```

## Best Practices

1. **No fluff**: Every word must add value
2. **Action-oriented**: Tell users what to DO, not what to think about
3. **Real examples**: Use actual files, commands, and values from the project
4. **Problem-solving**: Address common user problems
5. **Scannable**: Use headers, lists, and code blocks effectively
6. **User perspective**: Write for someone who wants to USE the tool, not build it

## Anti-Patterns to Avoid

❌ **Don't include**:
- Implementation details users don't need
- Theoretical explanations without practical application
- Placeholder text like `[your-value-here]`
- Long-winded introductions
- Technical jargon without explanation
- Obvious statements ("Files are used to store data")

✅ **Do include**:
- Copy-pasteable commands
- Real file names and paths
- Actual configuration examples
- Step-by-step instructions
- Troubleshooting for real problems
- Tips from actual usage
