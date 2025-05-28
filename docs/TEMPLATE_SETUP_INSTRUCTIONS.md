# Template Repository Setup Instructions

Follow these steps to create a GitHub template repository from this integration template reference implementation:

## 🎯 Creating the Template Repository

### Step 1: Prepare Template Files

1. **Create a new directory for the template:**
```bash
mkdir elitea-pylon-plugin-template
cd elitea-pylon-plugin-template
```

2. **Copy the core template files:**
```bash
# Copy the template-specific files
cp ../integration-template/TEMPLATE_README.md ./README.md
cp ../integration-template/setup_template.py ./
cp ../integration-template/test_plugin.py ./

# Create template structure with placeholders
mkdir -p methods routes
```

3. **Create placeholder files with template variables:**

Create these files with `{{PLACEHOLDER}}` variables that the setup script will replace:

**`metadata.json`:**
```json
{
  "name": "Host for tools: {{PLUGIN_NAME}}",
  "version": "1.0.0",
  "description": "{{PLUGIN_DESCRIPTION}}",
  "depends_on": [],
  "init_after": []
}
```

**`config.yml`:**
```yaml
# {{PLUGIN_NAME}} Plugin Configuration
service_location_url: http://127.0.0.1:8080
base_path: /tmp/{{PLUGIN_NAME_LOWER}}
```

**`requirements.txt`:**
```
flask>=2.0.0
requests>=2.25.0
```

**`__init__.py`:**
```python
#!/usr/bin/python3
# coding=utf-8
""" {{PLUGIN_NAME}} Plugin """
from .module import Module
```

### Step 2: Create GitHub Template Repository

1. **Create new repository on GitHub:**
   - Repository name: `elitea-pylon-plugin-template`
   - Description: "Template for creating ELITEA/Pylon integration plugins"
   - Make it public
   - ✅ **Check "Template repository"** option

2. **Push template files:**
```bash
git init
git add .
git commit -m "Initial template repository setup"
git branch -M main
git remote add origin https://github.com/YOUR-ORG/elitea-pylon-plugin-template.git
git push -u origin main
```

### Step 3: Configure Template Repository

1. **Add repository description and topics:**
   - Description: "🚀 Template for creating ELITEA/Pylon integration plugins with automated setup"
   - Topics: `elitea`, `pylon`, `plugin`, `template`, `integration`, `python`

2. **Create comprehensive README:**
   - Use the `TEMPLATE_README.md` content
   - Add badges for license, version, etc.
   - Include screenshot/demo if possible

3. **Set up repository settings:**
   - Enable Issues and Wiki
   - Set license to Apache 2.0
   - Add code of conduct and contributing guidelines

## 🛠️ Template Features

The template repository will include:

### ✅ Automated Setup
- **`setup_template.py`** - Interactive setup script
- **`test_plugin.py`** - Comprehensive testing utility
- **Clear documentation** with step-by-step instructions

### ✅ Complete Structure
- **All required files** with proper placeholders
- **Standard Pylon structure** following best practices
- **Example implementations** that users can customize

### ✅ Developer Experience
- **One-command setup** via the setup script
- **Built-in testing** to verify everything works
- **Comprehensive documentation** linking to examples

## 📋 Using the Template

Once the template is set up, users can:

1. **Click "Use this template"** on GitHub
2. **Clone their new repository**
3. **Run `python setup_template.py`** for guided setup
4. **Implement their tool logic**
5. **Test with `python test_plugin.py`**

## 🔗 Reference Links

In the template README, include links to:
- This integration template implementation as a complex example
- Step-by-step guide for detailed learning
- Integration patterns for specific tool types
- ELITEA platform documentation

## 📝 Template Repository Contents

```
elitea-pylon-plugin-template/
├── README.md                   # Template usage instructions
├── setup_template.py           # Interactive setup script
├── test_plugin.py             # Testing utilities
├── LICENSE                    # Apache 2.0 license
├── .gitignore                 # Python/IDE ignores
├── metadata.json              # Template metadata with placeholders
├── config.yml                 # Template config with placeholders
├── requirements.txt           # Base requirements
├── __init__.py               # Template module entry
├── module.py                 # Template main module
├── methods/                  # Template methods directory
│   ├── __init__.py
│   ├── init.py              # Template initialization
│   ├── config.py            # Template configuration
│   ├── dependencies.py      # Template dependency management
│   └── tool_operations.py   # Template tool implementations
└── routes/                  # Template routes directory
    ├── __init__.py
    ├── descriptor.py        # Template descriptor
    ├── invoke.py           # Template invocation
    ├── invocations.py      # Template status
    └── health.py           # Template health check
```

## 🎉 Result

Users will be able to:
1. Create a new plugin in minutes using the template
2. Follow guided setup for their specific tool
3. Get a working plugin with proper structure
4. Test everything before deployment
5. Reference this template implementation for advanced patterns

This creates a smooth developer experience for anyone wanting to integrate their tools with ELITEA!
