# Step-by-Step Guide: Creating ELITEA/Pylon Integration Plugins

This comprehensive guide walks you through creating an ELITEA/Pylon integration plugin from scratch. We'll build a simple example step by step, explaining each component and why it's needed.

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Understanding the Architecture](#understanding-the-architecture)
3. [Step 1: Project Setup](#step-1-project-setup)
4. [Step 2: Core Module Structure](#step-2-core-module-structure)
5. [Step 3: Configuration Management](#step-3-configuration-management)
6. [Step 4: Plugin Descriptor](#step-4-plugin-descriptor)
7. [Step 5: Tool Invocation](#step-5-tool-invocation)
8. [Step 6: Status Management](#step-6-status-management)
9. [Step 7: External Dependencies](#step-7-external-dependencies)
10. [Step 8: Testing Your Plugin](#step-8-testing-your-plugin)
11. [Step 9: Advanced Patterns](#step-9-advanced-patterns)
12. [Common Troubleshooting](#common-troubleshooting)

---

## Prerequisites

Before starting, ensure you have:
- Python 3.8+ installed
- Basic understanding of Python and HTTP APIs
- The tool/library you want to integrate (if applicable)
- Access to an ELITEA platform instance

---

## Understanding the Architecture

### The Big Picture

An ELITEA/Pylon plugin acts as a bridge between the ELITEA platform and external tools. Here's how it works:

```
ELITEA Platform ←→ Your Plugin ←→ External Tool
```

1. **Registration Phase**: Your plugin tells ELITEA what tools it provides
2. **Invocation Phase**: ELITEA calls your plugin to use those tools
3. **Result Phase**: Your plugin returns the results back to ELITEA

### Key Concepts

- **Toolkit**: A collection of related tools (e.g., "ImageProcessingToolkit")
- **Tool**: A specific function (e.g., "resize_image", "convert_format")
- **Invocation**: A single call to execute a tool
- **Descriptor**: The JSON that registers your toolkit with ELITEA

---

## Step 1: Project Setup

Let's create a simple image processing plugin as our example.

### 1.1 Create the Project Structure

```bash
# Create your plugin directory
mkdir image_processor_plugin
cd image_processor_plugin

# Create the standard directory structure
mkdir -p methods routes
touch __init__.py methods/__init__.py routes/__init__.py

# Create the core files
touch module.py metadata.json config.yml requirements.txt
touch methods/init.py methods/config.py methods/image_ops.py
touch routes/descriptor.py routes/invoke.py routes/invocations.py routes/health.py
```

Your structure should look like this:
```
image_processor_plugin/
├── __init__.py
├── module.py
├── metadata.json
├── config.yml
├── requirements.txt
├── methods/
│   ├── __init__.py
│   ├── init.py
│   ├── config.py
│   └── image_ops.py
└── routes/
    ├── __init__.py
    ├── descriptor.py
    ├── invoke.py
    ├── invocations.py
    └── health.py
```

### 1.2 Define Plugin Metadata

Create `metadata.json` - this tells Pylon about your plugin:

```json
{
  "name": "Host for tools: Image Processor",
  "version": "1.0.0",
  "description": "Image processing toolkit integration",
  "depends_on": [],
  "init_after": []
}
```

### 1.3 Set Default Configuration

Create `config.yml` - default settings for your plugin:

```yaml
# Service configuration
service_location_url: http://127.0.0.1:8080

# Working directories
base_path: /tmp/image_processor
work_dir: /tmp/image_processor/work

# Tool-specific settings
max_image_size: 10485760  # 10MB
supported_formats: ["jpg", "jpeg", "png", "gif", "bmp", "webp"]
```

### 1.4 Define Python Dependencies

Create `requirements.txt`:

```
Pillow>=8.0.0
flask>=2.0.0
requests>=2.25.0
```

---

## Step 2: Core Module Structure

### 2.1 Module Entry Point

Create `__init__.py`:

```python
#!/usr/bin/python3
# coding=utf-8
""" Image Processor Plugin """
from .module import Module
```

### 2.2 Main Module Class

Create `module.py` - the heart of your plugin:

```python
#!/usr/bin/python3
# coding=utf-8

""" Image Processor Plugin Module """

from pylon.core.tools import log, module


class Module(module.ModuleModel):
    """ Plugin Module """

    def __init__(self, context, descriptor):
        self.context = context
        self.descriptor = descriptor

    def init(self):
        """ Initialize the plugin """
        log.info("Initializing Image Processor Plugin")
        
        # Initialize configuration
        self.init_config()
        
        # Set up working directories
        self.setup_directories()
        
        log.info("Image Processor Plugin initialized successfully")

    def deinit(self):
        """ Cleanup when plugin is disabled """
        log.info("Deinitializing Image Processor Plugin")
```

**Why this matters**: The Module class is how Pylon manages your plugin's lifecycle. The `init()` method runs when your plugin starts, and `deinit()` runs when it's stopped.

---

## Step 3: Configuration Management

### 3.1 Configuration Handler

Create `methods/config.py`:

```python
#!/usr/bin/python3
# coding=utf-8

""" Configuration Management """

import os
import pathlib
from pylon.core.tools import log, web


class Method:
    """ Configuration methods """

    @web.method()
    def runtime_config(self):
        """ Get runtime configuration """
        config = {}
        
        # Base configuration
        defaults = {
            "base_path": "/tmp/image_processor",
            "work_dir": "/tmp/image_processor/work", 
            "max_image_size": 10485760,
            "supported_formats": ["jpg", "jpeg", "png", "gif", "bmp", "webp"],
            "service_location_url": "http://127.0.0.1:8080"
        }
        
        # Merge with user config
        for key, default in defaults.items():
            config[key] = self.descriptor.config.get(key, default)
        
        # Ensure paths are absolute
        config["base_path"] = os.path.abspath(config["base_path"])
        config["work_dir"] = os.path.abspath(config["work_dir"])
        
        return config

    @web.method()
    def setup_directories(self):
        """ Create necessary directories """
        config = self.runtime_config()
        
        directories = [
            config["base_path"],
            config["work_dir"]
        ]
        
        for directory in directories:
            pathlib.Path(directory).mkdir(parents=True, exist_ok=True)
            log.info(f"Created directory: {directory}")
```

**Why this matters**: Configuration management lets users customize your plugin without modifying code. The `runtime_config()` method is the single source of truth for all settings.

### 3.2 Initialization Logic

Create `methods/init.py`:

```python
#!/usr/bin/python3
# coding=utf-8

""" Initialization Methods """

from pylon.core.tools import log, web


class Method:
    """ Initialization methods """

    @web.init()
    def init_config(self):
        """ Initialize plugin configuration """
        config = self.runtime_config()
        log.info(f"Plugin configured with base_path: {config['base_path']}")
        
        # Store start time for health checks
        import time
        self.start_time = time.time()
```

**Why this matters**: The `@web.init()` decorator ensures this runs during plugin startup. You can add any setup logic here.

---

## Step 4: Plugin Descriptor

The descriptor is how your plugin announces its capabilities to ELITEA.

### 4.1 Create the Descriptor Endpoint

Create `routes/descriptor.py`:

```python
#!/usr/bin/python3
# coding=utf-8

""" Plugin Descriptor Route """

from pylon.core.tools import web


class Route:
    """ Descriptor route """

    @web.route("/descriptor", methods=["GET"])
    def descriptor_route(self):
        """ Return plugin descriptor """
        config = self.runtime_config()
        
        descriptor = {
            "type": "toolkit",
            "provider": "ImageProcessorPlugin",
            "version": "1.0.0",
            "name": "ImageProcessingToolkit",
            "description": "Toolkit for image processing operations",
            "service_location_url": config["service_location_url"],
            "tools": [
                {
                    "type": "function",
                    "name": "resize_image",
                    "description": "Resize an image to specified dimensions",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "image_data": {
                                "type": "string",
                                "description": "Base64 encoded image data"
                            },
                            "width": {
                                "type": "integer",
                                "description": "Target width in pixels"
                            },
                            "height": {
                                "type": "integer", 
                                "description": "Target height in pixels"
                            },
                            "format": {
                                "type": "string",
                                "description": "Output format (jpg, png, etc.)",
                                "default": "png"
                            }
                        },
                        "required": ["image_data", "width", "height"]
                    }
                },
                {
                    "type": "function",
                    "name": "convert_format",
                    "description": "Convert image to different format",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "image_data": {
                                "type": "string",
                                "description": "Base64 encoded image data"
                            },
                            "target_format": {
                                "type": "string",
                                "description": "Target format (jpg, png, webp, etc.)"
                            }
                        },
                        "required": ["image_data", "target_format"]
                    }
                }
            ]
        }
        
        return descriptor
```

**Key Points**:
- **`type: "toolkit"`**: Tells ELITEA this is a toolkit provider
- **`name`**: The toolkit name that ELITEA will use in URLs
- **`tools`**: Array of functions your toolkit provides
- **`parameters`**: JSON Schema defining what inputs each tool expects

---

## Step 5: Tool Invocation

This is where the actual work happens when ELITEA calls your tools.

### 5.1 Create Image Processing Methods

Create `methods/image_ops.py`:

```python
#!/usr/bin/python3
# coding=utf-8

""" Image Processing Operations """

import base64
import io
from PIL import Image
from pylon.core.tools import log, web


class Method:
    """ Image processing methods """

    @web.method()
    def resize_image(self, image_data, width, height, format="png"):
        """ Resize an image """
        try:
            # Decode base64 image
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))
            
            # Resize the image
            resized_image = image.resize((width, height), Image.Resampling.LANCZOS)
            
            # Convert to target format
            output_buffer = io.BytesIO()
            resized_image.save(output_buffer, format=format.upper())
            
            # Encode result
            result_data = base64.b64encode(output_buffer.getvalue()).decode()
            
            return {
                "success": True,
                "data": result_data,
                "format": format,
                "width": width,
                "height": height
            }
            
        except Exception as e:
            log.error(f"Image resize failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    @web.method()
    def convert_format(self, image_data, target_format):
        """ Convert image format """
        try:
            # Decode base64 image
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))
            
            # Convert format
            output_buffer = io.BytesIO()
            image.save(output_buffer, format=target_format.upper())
            
            # Encode result
            result_data = base64.b64encode(output_buffer.getvalue()).decode()
            
            return {
                "success": True,
                "data": result_data,
                "format": target_format
            }
            
        except Exception as e:
            log.error(f"Format conversion failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
```

### 5.2 Create the Invocation Route

Create `routes/invoke.py`:

```python
#!/usr/bin/python3
# coding=utf-8

""" Tool Invocation Route """

import uuid
import flask
from pylon.core.tools import log, web


class Route:
    """ Invocation route """

    @web.route("/tools/<toolkit_name>/<tool_name>/invoke", methods=["POST"])
    def invoke_route(self, toolkit_name, tool_name):
        """ Handle tool invocation """
        
        # Validate toolkit
        if toolkit_name != "ImageProcessingToolkit":
            return {
                "errorCode": "404",
                "message": "Toolkit not found",
                "details": [f"Unknown toolkit: {toolkit_name}"]
            }, 404
        
        try:
            # Get request data
            request_data = flask.request.json
            if not request_data or "parameters" not in request_data:
                return {
                    "errorCode": "400",
                    "message": "Missing parameters",
                    "details": ["Request must include 'parameters' field"]
                }, 400
            
            parameters = request_data["parameters"]
            
            # Route to appropriate tool
            if tool_name == "resize_image":
                result = self._handle_resize_image(parameters)
            elif tool_name == "convert_format":
                result = self._handle_convert_format(parameters)
            else:
                return {
                    "errorCode": "404",
                    "message": "Tool not found",
                    "details": [f"Unknown tool: {tool_name}"]
                }, 404
            
            # Generate invocation ID
            invocation_id = str(uuid.uuid4())
            
            # Return success response
            return {
                "invocation_id": invocation_id,
                "status": "Completed",
                "result": result,
                "result_type": "Object"
            }
            
        except Exception as e:
            log.exception(f"Tool invocation failed: {toolkit_name}:{tool_name}")
            return {
                "errorCode": "500",
                "message": "Internal server error",
                "details": [str(e)]
            }, 500

    def _handle_resize_image(self, parameters):
        """ Handle resize_image tool """
        required_params = ["image_data", "width", "height"]
        for param in required_params:
            if param not in parameters:
                raise ValueError(f"Missing required parameter: {param}")
        
        return self.resize_image(
            image_data=parameters["image_data"],
            width=parameters["width"],
            height=parameters["height"],
            format=parameters.get("format", "png")
        )

    def _handle_convert_format(self, parameters):
        """ Handle convert_format tool """
        required_params = ["image_data", "target_format"]
        for param in required_params:
            if param not in parameters:
                raise ValueError(f"Missing required parameter: {param}")
        
        return self.convert_format(
            image_data=parameters["image_data"],
            target_format=parameters["target_format"]
        )
```

**Key Points**:
- **URL Pattern**: `/tools/<toolkit_name>/<tool_name>/invoke`
- **Input Validation**: Always validate required parameters
- **Error Handling**: Return proper HTTP status codes and error messages
- **Invocation ID**: Generate unique IDs for tracking

---

## Step 6: Status Management

### 6.1 Create Status Route

Create `routes/invocations.py`:

```python
#!/usr/bin/python3
# coding=utf-8

""" Invocation Status Route """

from pylon.core.tools import web


class Route:
    """ Invocation status route """

    @web.route("/tools/<toolkit_name>/<tool_name>/invocations/<invocation_id>", methods=["GET", "DELETE"])
    def invocations_route(self, toolkit_name, tool_name, invocation_id):
        """ Handle invocation status requests """
        
        if flask.request.method == "GET":
            # In this simple example, we don't store invocation state
            # For async operations, you would track status here
            return {
                "invocation_id": invocation_id,
                "status": "Completed",
                "message": "Synchronous operation completed immediately"
            }
        
        elif flask.request.method == "DELETE":
            # Handle cancellation (if supported)
            return {
                "message": "Synchronous operations cannot be cancelled"
            }, 400
```

### 6.2 Create Health Check

Create `routes/health.py`:

```python
#!/usr/bin/python3
# coding=utf-8

""" Health Check Route """

import time
from pylon.core.tools import web


class Route:
    """ Health check route """

    @web.route("/health", methods=["GET"])
    def health_route(self):
        """ Return plugin health status """
        try:
            current_time = time.time()
            uptime = current_time - getattr(self, 'start_time', current_time)
            
            config = self.runtime_config()
            
            return {
                "status": "healthy",
                "uptime_seconds": round(uptime, 2),
                "plugin": "ImageProcessingToolkit",
                "version": "1.0.0",
                "configuration": {
                    "base_path": config["base_path"],
                    "max_image_size": config["max_image_size"],
                    "supported_formats": config["supported_formats"]
                }
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }, 500
```

---

## Step 7: External Dependencies

For plugins that need external tools (like Node.js modules or Python packages), you'll need dependency management.

### 7.1 Example: Python Library Management

Add to `methods/init.py`:

```python
@web.method()
def check_dependencies(self):
    """ Check and install required dependencies """
    try:
        import PIL
        log.info("PIL/Pillow is available")
    except ImportError:
        log.error("PIL/Pillow not found. Install with: pip install Pillow")
        raise RuntimeError("Missing required dependency: Pillow")
```

### 7.2 Example: External Binary Management

For complex setups like Node.js (see the template example), create `methods/binaries.py`:

```python
@web.method()
def download_external_tool(self, config):
    """ Download and setup external tools """
    # Implementation similar to integration-template/methods/binaries.py
    pass
```

---

## Step 8: Testing Your Plugin

### 8.1 Test the Descriptor

```bash
# Start your plugin (method depends on your Pylon setup)
# Then test the descriptor endpoint:

curl http://localhost:8080/descriptor
```

Expected response:
```json
{
  "type": "toolkit",
  "name": "ImageProcessingToolkit",
  "tools": [...]
}
```

### 8.2 Test Tool Invocation

```bash
# Create a simple test image (base64 encoded)
echo "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg==" > test_image.txt

# Test resize tool
curl -X POST http://localhost:8080/tools/ImageProcessingToolkit/resize_image/invoke \
  -H "Content-Type: application/json" \
  -d '{
    "parameters": {
      "image_data": "'"$(cat test_image.txt)"'",
      "width": 100,
      "height": 100,
      "format": "png"
    }
  }'
```

### 8.3 Test Health Check

```bash
curl http://localhost:8080/health
```

---

## Step 9: Advanced Patterns

### 9.1 Asynchronous Operations

For long-running operations, implement proper status tracking:

```python
# In your invoke route
import threading

def invoke_route(self, toolkit_name, tool_name):
    # Store invocation state
    invocation_id = str(uuid.uuid4())
    
    # Start background task
    thread = threading.Thread(
        target=self._background_process,
        args=(invocation_id, parameters)
    )
    thread.start()
    
    return {
        "invocation_id": invocation_id,
        "status": "Running"
    }
```

### 9.2 Configuration Validation

```python
@web.method()
def validate_config(self, config):
    """ Validate configuration settings """
    if config["max_image_size"] <= 0:
        raise ValueError("max_image_size must be positive")
    
    for fmt in config["supported_formats"]:
        if fmt not in ["jpg", "jpeg", "png", "gif", "bmp", "webp"]:
            raise ValueError(f"Unsupported format: {fmt}")
```

### 9.3 Resource Cleanup

```python
import tempfile
import shutil

@web.method()
def process_with_cleanup(self, parameters):
    """ Process with automatic cleanup """
    work_dir = None
    try:
        work_dir = tempfile.mkdtemp()
        # Do processing...
        return result
    finally:
        if work_dir:
            shutil.rmtree(work_dir)
```

---

## Common Troubleshooting

### Problem: Plugin not loading
**Solution**: Check `metadata.json` syntax and ensure all required files exist.

### Problem: Tools not appearing in ELITEA
**Solution**: Verify descriptor endpoint returns valid JSON and toolkit name matches URL pattern.

### Problem: Tool invocation fails
**Solution**: Check parameter validation and error handling in invoke route.

### Problem: Dependencies not found
**Solution**: Ensure `requirements.txt` includes all needed packages and they're installed.

### Problem: Paths not working
**Solution**: Always use absolute paths in configuration.

---

## Next Steps

1. **🔧 Study the Template Example**: For complex external tool integration, see [this repository's template implementation](../README.md)
2. **📋 Read Integration Patterns**: For specific tool types, check [Integration Patterns](INTEGRATION_PATTERNS.md)
3. **⚡ Use the Quick Start Template**: For minimal working examples, see [Quick Start Template](QUICK_START_TEMPLATE.md)
4. **📖 Reference the Integration Guide**: For comprehensive details, see [Integration Guide](INTEGRATION_GUIDE.md)
5. **🧪 Set up Testing**: Use `python setup_template.py` and `python test_plugin.py` for development
6. **🛠️ Create from Template**: Use [Template Setup Instructions](TEMPLATE_SETUP_INSTRUCTIONS.md) to create your own template repository

---

## Summary

You've learned to create a complete ELITEA/Pylon integration plugin:

1. ✅ **Project Structure** - Organized code layout
2. ✅ **Configuration** - Flexible settings management
3. ✅ **Descriptor** - Tool registration with ELITEA
4. ✅ **Invocation** - Handling tool execution
5. ✅ **Status Management** - Tracking operation status
6. ✅ **Health Checks** - Monitoring plugin health
7. ✅ **Testing** - Verifying functionality

Your plugin is now ready to integrate any tool or service with the ELITEA platform!
