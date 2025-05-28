# ELITEA/Pylon Plugin Template

This template repository helps you quickly create new ELITEA/Pylon integration plugins. It provides a complete working structure that you can customize for your specific tool or service.

## 🚀 Quick Start

### 1. Use This Template

1. Click **"Use this template"** button (or clone this repository)
2. Name your new repository (e.g., `my-tool-plugin`)
3. Clone your new repository locally

### 2. Customize for Your Tool

```bash
cd my-tool-plugin

# Run the setup script to customize the template
python setup_template.py
```

The setup script will interactively prompt you for:
- **Plugin name** (e.g., "ImageProcessor", "VideoConverter")
- **Tool names** and descriptions (e.g., "resize_image", "convert_video") 
- **Parameters** for each tool
- **Dependencies** your tool needs
- **Configuration options**

### 3. Implement Your Logic

After running the setup script, you'll have a complete plugin structure:

1. **Add your tool logic** in `methods/tool_operations.py`
2. **Install dependencies** in `methods/dependencies.py` 
3. **Test your plugin** with `python test_plugin.py`
4. **Customize configuration** in `config.yml`

> **💡 Need help?** Check the generated files for TODO comments and example implementations.

## 📁 Template Structure

```
plugin-template/
├── setup_template.py          # 🎯 Customization script
├── test_plugin.py             # 🧪 Testing utilities
├── metadata.json              # Plugin metadata for Pylon
├── config.yml                 # Configuration defaults
├── requirements.txt           # Python dependencies
├── __init__.py               # Module entry point
├── module.py                 # Main Pylon module
├── methods/                  # Internal plugin methods
│   ├── __init__.py
│   ├── init.py              # Initialization logic
│   ├── config.py            # Configuration management
│   ├── dependencies.py       # Dependency management
│   └── tool_operations.py   # 📝 YOUR TOOL LOGIC HERE
└── routes/                  # HTTP endpoints
    ├── __init__.py
    ├── descriptor.py        # Toolkit registration
    ├── invoke.py           # Tool invocation
    ├── invocations.py      # Status checking
    └── health.py           # Health check
```

## 🛠️ Customization Guide

### What the Setup Script Does

The `setup_template.py` script will:

1. **Replace placeholders** in all files with your specific values
2. **Generate tool schemas** based on your input
3. **Update configuration** with your tool's needs
4. **Create example implementations** for your tools

### Manual Customization

If you prefer manual setup, replace these placeholders:

- `{{PLUGIN_NAME}}` → Your plugin name (e.g., "ImageProcessor")
- `{{PLUGIN_DESCRIPTION}}` → Description of your plugin
- `{{TOOLKIT_NAME}}` → Your toolkit name (e.g., "ImageProcessingToolkit")
- `{{TOOL_NAME}}` → Your tool name (e.g., "resize_image")
- `{{TOOL_DESCRIPTION}}` → What your tool does

## 📋 Implementation Checklist

After customization, implement these components:

### ✅ Core Functionality
- [ ] **Tool Logic** - Implement your tools in `methods/tool_operations.py`
- [ ] **Dependencies** - Set up required libraries/binaries in `methods/dependencies.py`
- [ ] **Configuration** - Add any custom config in `config.yml`
- [ ] **Error Handling** - Add proper error handling and validation

### ✅ Testing
- [ ] **Unit Tests** - Test your tool methods
- [ ] **Integration Tests** - Test the full HTTP API
- [ ] **Manual Testing** - Use `test_plugin.py` for manual verification

### ✅ Documentation
- [ ] **Update README** - Describe your specific plugin
- [ ] **API Documentation** - Document your tool parameters
- [ ] **Configuration Guide** - Document available settings

## 🧪 Testing Your Plugin

### Automated Testing

```bash
# Run the test suite
python test_plugin.py

# Test specific components
python test_plugin.py --test descriptor
python test_plugin.py --test invoke
python test_plugin.py --test health
```

### Manual Testing

```bash
# Start your plugin (method depends on your Pylon setup)
pylon start

# Test the descriptor
curl http://localhost:8080/descriptor

# Test a tool invocation
curl -X POST http://localhost:8080/tools/YourToolkit/your_tool/invoke \
  -H "Content-Type: application/json" \
  -d '{"parameters": {"param1": "value1"}}'

# Check health
curl http://localhost:8080/health
```

## 📚 Learning Resources

- **[Step-by-Step Guide](STEP_BY_STEP_GUIDE.md)** - Complete walkthrough
- **[Integration Patterns](INTEGRATION_PATTERNS.md)** - Common patterns
- **[Integration Template Example](../README.md)** - Real-world reference implementation

## 🔧 Common Plugin Types

This template works for:

- **🐍 Python Libraries** (PIL, pandas, scikit-learn, etc.)
- **🛠️ CLI Tools** (FFmpeg, ImageMagick, Pandoc, etc.)
- **🌐 APIs** (REST services, GraphQL, etc.)
- **📊 Data Processing** (CSV, JSON, XML processing)
- **🤖 AI/ML Models** (TensorFlow, PyTorch, Hugging Face)
- **🗄️ Databases** (SQL queries, data export)

## 📝 Example Plugins

Here are some ideas for plugins you could create:

### Image Processing Plugin
```yaml
Tools:
  - resize_image: Resize images to specific dimensions
  - convert_format: Convert between image formats
  - add_watermark: Add watermarks to images
```

### Document Converter Plugin
```yaml
Tools:
  - markdown_to_pdf: Convert Markdown to PDF
  - docx_to_html: Convert Word documents to HTML
  - merge_pdfs: Combine multiple PDFs
```

### Data Analysis Plugin
```yaml
Tools:
  - csv_summary: Generate statistics from CSV files
  - plot_data: Create charts from data
  - clean_data: Remove duplicates and normalize data
```

## 🤝 Contributing

1. Fork this template repository
2. Make improvements to the template
3. Submit a pull request with your enhancements

## 📄 License

This template is licensed under the Apache License, Version 2.0.

---

**Ready to build your plugin?** Run `python setup_template.py` to get started!
