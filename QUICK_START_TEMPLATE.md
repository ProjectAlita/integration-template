# Quick Start Template for ELITEA/Pylon Plugins

This template provides a minimal working example to get you started with creating ELITEA/Pylon integration plugins.

## 1. Create Project Structure

```bash
mkdir my_tool_plugin
cd my_tool_plugin

# Create directory structure
mkdir -p methods routes
touch __init__.py methods/__init__.py routes/__init__.py
touch module.py metadata.json config.yml requirements.txt
touch methods/init.py methods/config.py
touch routes/descriptor.py routes/invoke.py routes/health.py routes/invocations.py
```

## 2. Basic Files Setup

### `metadata.json`
```json
{
  "name": "Host for tools: my_tool",
  "version": "0.1",
  "depends_on": [],
  "init_after": []
}
```

### `config.yml`
```yaml
service_location_url: http://127.0.0.1:8080
base_path: /data/my_tool
```

### `requirements.txt`
```
flask>=2.0.0
requests>=2.25.0
```

### `__init__.py`
```python
#!/usr/bin/python3
# coding=utf-8
""" Module init """
from .module import Module
```

### `module.py`
```python
#!/usr/bin/python3
# coding=utf-8
""" Module """
from pylon.core.tools import module

class Module(module.ModuleModel):
    """ Pylon module """
    def init(self):
        """ Initialize module """
        self.descriptor.init_all(
            url_prefix="/",
            static_url_prefix="/",
        )
```

## 3. Core Implementation

### `methods/config.py`
```python
#!/usr/bin/python3
# coding=utf-8
""" Method """
import os
import pathlib
from pylon.core.tools import web

class Method:
    @web.method()
    def runtime_config(self):
        """ Method """
        result = {}
        
        config_map = {
            "base_path": str(pathlib.Path(__file__).parent.parent.joinpath("data", "my_tool")),
            "service_location_url": "http://127.0.0.1:8080",
        }
        
        for key, default in config_map.items():
            result[key] = self.descriptor.config.get(key, default)
        
        return result
```

### `methods/init.py`
```python
#!/usr/bin/python3
# coding=utf-8
""" Method """
import time
from pylon.core.tools import web

class Method:
    @web.init()
    def init(self):
        """ Init """
        config = self.runtime_config()
        
        # Add your initialization logic here
        # self.setup_tool(config)
        
        self.start_ts = time.time()
```

### `routes/descriptor.py`
```python
#!/usr/bin/python3
# coding=utf-8
""" Route """
from pylon.core.tools import web

class Route:
    @web.route("/descriptor")
    def descriptor_route(self):
        """ Handler """
        service_location_url = self.descriptor.config.get(
            "service_location_url", "http://127.0.0.1:8080"
        )
        
        return {
            "name": "MyToolServiceProvider",
            "service_location_url": service_location_url,
            "configuration": {},
            "provided_toolkits": [
                {
                    "name": "MyToolkit",
                    "description": "Description of what my toolkit does",
                    "toolkit_config": {
                        "type": "My Tool Configuration",
                        "description": "Configuration for my tool",
                        "parameters": {},
                    },
                    "provided_tools": [
                        {
                            "name": "process_data",
                            "args_schema": {
                                "input_data": {
                                    "type": "String",
                                    "required": True,
                                    "description": "Input data to process"
                                },
                                "options": {
                                    "type": "Object",
                                    "required": False,
                                    "description": "Processing options"
                                }
                            },
                            "description": "Process input data and return result",
                            "tool_metadata": {
                                "result_target": "inline",
                            },
                            "tool_result_type": "String",
                            "sync_invocation_supported": True,
                            "async_invocation_supported": False,
                        },
                    ],
                    "toolkit_metadata": {},
                },
            ]
        }
```

### `routes/invoke.py`
```python
#!/usr/bin/python3
# coding=utf-8
""" Route """
import uuid
import flask
from pylon.core.tools import web, log

class Route:
    @web.route("/tools/<toolkit_name>/<tool_name>/invoke", methods=["POST"])
    def invoke_route(self, toolkit_name, tool_name):
        """ Handler """
        # Validate toolkit and tool
        if toolkit_name != "MyToolkit" or tool_name != "process_data":
            return {
                "errorCode": "404",
                "message": "Resource Not Found",
                "details": [],
            }, 404
        
        try:
            request_data = flask.request.json
            
            # Validate request
            if "parameters" not in request_data or "input_data" not in request_data["parameters"]:
                return {
                    "errorCode": "400",
                    "message": "Bad Request",
                    "details": ["Missing required parameter: input_data"],
                }, 400
            
            # Extract parameters
            input_data = request_data["parameters"]["input_data"]
            options = request_data["parameters"].get("options", {})
            
            # TODO: Replace this with your actual tool logic
            result = self.process_with_my_tool(input_data, options)
            
            return {
                "invocation_id": str(uuid.uuid4()),
                "status": "Completed",
                "result": result,
                "result_type": "String",
            }
            
        except Exception as e:
            log.exception("Failed to invoke %s:%s", toolkit_name, tool_name)
            return {
                "errorCode": "500",
                "message": "Internal Server Error",
                "details": [str(e)],
            }, 500
    
    def process_with_my_tool(self, input_data, options):
        """ Replace this method with your actual tool logic """
        # Example: simple string processing
        result = f"Processed: {input_data}"
        if options.get("uppercase"):
            result = result.upper()
        return result
```

### `routes/health.py`
```python
#!/usr/bin/python3
# coding=utf-8
""" Route """
import time
import datetime
from pylon.core.tools import web

class Route:
    @web.route("/health")
    def health_route(self):
        """ Handler """
        return {
            "status": "UP",
            "providerVersion": "latest",
            "uptime": int(time.time() - self.start_ts),
            "timestamp": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S+00:00"),
            "extra_info": {},
        }
```

### `routes/invocations.py`
```python
#!/usr/bin/python3
# coding=utf-8
""" Route """
from pylon.core.tools import web

class Route:
    @web.route("/tools/<toolkit_name>/<tool_name>/invocations/<invocation_id>", methods=["GET", "DELETE"])
    def invocations_route(self, toolkit_name, tool_name, invocation_id):
        """ Handler """
        # For sync tools, this can return a simple not implemented response
        return {
            "errorCode": "501",
            "message": "Not Implemented - Sync invocation only",
            "details": [],
        }, 501
```

## 4. Customization Points

### For Python-based tools:
1. **Replace `process_with_my_tool`** in `routes/invoke.py` with your actual Python logic
2. **Add dependencies** to `requirements.txt`
3. **Update descriptor** with your tool's parameters and description

### For External Binary/CLI tools:
1. **Add binary setup** in `methods/init.py`:
```python
def setup_tool(self, config):
    """ Download and setup external tool """
    # Download binary, extract, set permissions, etc.
    pass
```

2. **Execute external command** in `routes/invoke.py`:
```python
from pylon.core.tools import process

def process_with_my_tool(self, input_data, options):
    result = process.run_command([
        "/path/to/your/tool", 
        "--input", input_data,
        "--option", options.get("some_option", "default")
    ], capture_output=True)
    return result.stdout
```

### For Node.js tools (like the Slidev example):
1. **Add Node.js setup** following the `methods/binaries.py` pattern from Slidev
2. **Install npm packages** during initialization
3. **Execute Node.js commands** with proper environment setup

## 5. Testing Your Plugin

1. **Test descriptor endpoint**:
```bash
curl http://localhost:8080/descriptor
```

2. **Test tool invocation**:
```bash
curl -X POST http://localhost:8080/tools/MyToolkit/process_data/invoke \
  -H "Content-Type: application/json" \
  -d '{"parameters": {"input_data": "test data", "options": {"uppercase": true}}}'
```

3. **Test health endpoint**:
```bash
curl http://localhost:8080/health
```

## 6. Next Steps

1. **Replace the example logic** with your actual tool implementation
2. **Update the descriptor** to match your tool's interface
3. **Add proper error handling** for your specific use cases
4. **Add configuration options** in `config.yml` as needed
5. **Test thoroughly** with various inputs and error scenarios

This template gives you a working foundation that you can build upon for any type of tool integration.
