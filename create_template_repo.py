#!/usr/bin/env python3
"""
Create Template Repository Script

This script creates a clean template repository from the current Slidev implementation.
It removes Slidev-specific code and replaces it with template placeholders.
"""

import os
import shutil
import json
from pathlib import Path


def create_template_repository():
    """Create the template repository structure"""
    
    template_dir = "elitea-pylon-plugin-template"
    
    # Remove existing template directory if it exists
    if os.path.exists(template_dir):
        shutil.rmtree(template_dir)
    
    # Create template directory structure
    os.makedirs(template_dir)
    os.makedirs(f"{template_dir}/methods")
    os.makedirs(f"{template_dir}/routes")
    
    print(f"📁 Created template directory: {template_dir}")
    
    # Copy documentation files
    docs_to_copy = [
        "TEMPLATE_README.md",
        "setup_template.py", 
        "test_plugin.py",
        "STEP_BY_STEP_GUIDE.md",
        "INTEGRATION_GUIDE.md", 
        "QUICK_START_TEMPLATE.md",
        "INTEGRATION_PATTERNS.md",
        "LICENSE"
    ]
    
    for doc in docs_to_copy:
        if os.path.exists(doc):
            if doc == "TEMPLATE_README.md":
                shutil.copy2(doc, f"{template_dir}/README.md")
            else:
                shutil.copy2(doc, f"{template_dir}/{doc}")
            print(f"📄 Copied: {doc}")
    
    # Create template files with placeholders
    create_template_files(template_dir)
    
    # Create .gitignore
    create_gitignore(template_dir)
    
    print(f"\n✅ Template repository created in: {template_dir}")
    print(f"🚀 Next steps:")
    print(f"   1. cd {template_dir}")
    print(f"   2. git init")
    print(f"   3. git add .")
    print(f"   4. git commit -m 'Initial template setup'")
    print(f"   5. Create repository on GitHub as template")
    print(f"   6. git remote add origin <your-repo-url>")
    print(f"   7. git push -u origin main")


def create_template_files(template_dir):
    """Create template files with placeholders"""
    
    # metadata.json
    metadata = {
        "name": "Host for tools: {{PLUGIN_NAME}}",
        "version": "1.0.0", 
        "description": "{{PLUGIN_DESCRIPTION}}",
        "depends_on": [],
        "init_after": []
    }
    
    with open(f"{template_dir}/metadata.json", 'w') as f:
        json.dump(metadata, f, indent=2)
    
    # config.yml
    config_content = """# {{PLUGIN_NAME}} Plugin Configuration
service_location_url: http://127.0.0.1:8080
base_path: /tmp/{{PLUGIN_NAME_LOWER}}

# Add your custom configuration options here
# example_setting: default_value
"""
    
    with open(f"{template_dir}/config.yml", 'w') as f:
        f.write(config_content)
    
    # requirements.txt
    requirements = """flask>=2.0.0
requests>=2.25.0
# Add your specific requirements here
# Pillow>=8.0.0
# pandas>=1.3.0
"""
    
    with open(f"{template_dir}/requirements.txt", 'w') as f:
        f.write(requirements)
    
    # Create Python template files
    create_python_templates(template_dir)


def create_python_templates(template_dir):
    """Create Python template files"""
    
    # __init__.py
    init_content = '''#!/usr/bin/python3
# coding=utf-8
""" {{PLUGIN_NAME}} Plugin """
from .module import Module
'''
    
    with open(f"{template_dir}/__init__.py", 'w') as f:
        f.write(init_content)
    
    # module.py
    module_content = '''#!/usr/bin/python3
# coding=utf-8

""" {{PLUGIN_NAME}} Plugin Module """

from pylon.core.tools import log, module


class Module(module.ModuleModel):
    """ Plugin Module """

    def __init__(self, context, descriptor):
        self.context = context
        self.descriptor = descriptor

    def init(self):
        """ Initialize the plugin """
        log.info("Initializing {{PLUGIN_NAME}} Plugin")
        self.descriptor.init_all(
            url_prefix="/",
            static_url_prefix="/",
        )
        log.info("{{PLUGIN_NAME}} Plugin initialized successfully")

    def deinit(self):
        """ Cleanup when plugin is disabled """
        log.info("Deinitializing {{PLUGIN_NAME}} Plugin")
'''
    
    with open(f"{template_dir}/module.py", 'w') as f:
        f.write(module_content)
    
    # methods/__init__.py
    with open(f"{template_dir}/methods/__init__.py", 'w') as f:
        f.write('#!/usr/bin/python3\n# coding=utf-8\n""" {{PLUGIN_NAME}} Methods """\n')
    
    # methods/init.py
    init_method_content = '''#!/usr/bin/python3
# coding=utf-8

""" Initialization Methods """

import time
from pylon.core.tools import log, web


class Method:
    """ Initialization methods """

    @web.init()
    def init_config(self):
        """ Initialize plugin configuration """
        config = self.runtime_config()
        log.info(f"{{PLUGIN_NAME}} configured with base_path: {config.get('base_path', 'N/A')}")
        
        # Store start time for health checks
        self.start_time = time.time()
        
        # Setup dependencies
        self.setup_dependencies()
        
        # Setup directories
        self.setup_directories()
'''
    
    with open(f"{template_dir}/methods/init.py", 'w') as f:
        f.write(init_method_content)
    
    # methods/config.py
    config_method_content = '''#!/usr/bin/python3
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
            "base_path": "/tmp/{{PLUGIN_NAME_LOWER}}",
            "service_location_url": "http://127.0.0.1:8080"
            # Add your default configuration here
        }
        
        # Merge with user config
        for key, default in defaults.items():
            config[key] = self.descriptor.config.get(key, default)
        
        # Ensure paths are absolute
        if "base_path" in config:
            config["base_path"] = os.path.abspath(config["base_path"])
        
        return config

    @web.method()
    def setup_directories(self):
        """ Create necessary directories """
        config = self.runtime_config()
        
        directories = [
            config.get("base_path"),
            # Add additional directories your plugin needs
        ]
        
        for directory in directories:
            if directory:
                pathlib.Path(directory).mkdir(parents=True, exist_ok=True)
                log.info(f"Created directory: {directory}")
'''
    
    with open(f"{template_dir}/methods/config.py", 'w') as f:
        f.write(config_method_content)
    
    # methods/dependencies.py
    deps_content = '''#!/usr/bin/python3
# coding=utf-8

""" Dependency Management """

from pylon.core.tools import log, web


class Method:
    """ Dependency management methods """

    @web.method()
    def setup_dependencies(self):
        """ Setup and verify dependencies """
        try:
            # TODO: Add your dependency checks here
            # Example:
            # import required_library
            # self.check_external_binary()
            
            log.info("{{PLUGIN_NAME}} dependencies verified")
        except ImportError as e:
            log.error(f"Missing dependency: {e}")
            raise RuntimeError(f"{{PLUGIN_NAME}} dependency not available: {e}")
        except Exception as e:
            log.error(f"Dependency setup failed: {e}")
            raise

    @web.method()
    def check_dependency(self, module_name):
        """ Check if a specific dependency is available """
        try:
            __import__(module_name)
            return True
        except ImportError:
            return False

    @web.method()
    def install_external_binary(self, binary_url, install_path):
        """ Example method for installing external binaries """
        # TODO: Implement if your plugin needs external tools
        # See slidev_host/methods/binaries.py for example
        pass
'''
    
    with open(f"{template_dir}/methods/dependencies.py", 'w') as f:
        f.write(deps_content)
    
    # methods/tool_operations.py
    operations_content = '''#!/usr/bin/python3
# coding=utf-8

""" {{PLUGIN_NAME}} Tool Operations """

from pylon.core.tools import log, web


class Method:
    """ Tool operation methods """

    @web.method()
    def example_tool(self, input_data=None, option=None):
        """ Example tool implementation """
        try:
            # TODO: Implement your tool logic here
            # This is a placeholder that will be replaced by setup_template.py
            
            result = {
                "success": True,
                "message": "Example tool completed successfully",
                "input_data": input_data,
                "option": option
            }
            
            log.info("Example tool executed successfully")
            return result
            
        except Exception as e:
            log.error(f"Example tool failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    # Additional tool methods will be generated by setup_template.py
'''
    
    with open(f"{template_dir}/methods/tool_operations.py", 'w') as f:
        f.write(operations_content)
    
    # routes/__init__.py  
    with open(f"{template_dir}/routes/__init__.py", 'w') as f:
        f.write('#!/usr/bin/python3\n# coding=utf-8\n""" {{PLUGIN_NAME}} Routes """\n')
    
    # routes/descriptor.py
    descriptor_content = '''#!/usr/bin/python3
# coding=utf-8

""" Plugin Descriptor Route """

from pylon.core.tools import web


class Route:
    """ Descriptor route """

    @web.route("/descriptor")
    def descriptor_route(self):
        """ Return plugin descriptor """
        config = self.runtime_config()
        
        descriptor = {
            "name": "{{PLUGIN_NAME}}ServiceProvider",
            "service_location_url": config["service_location_url"],
            "configuration": {},
            "provided_toolkits": [
                {
                    "name": "{{TOOLKIT_NAME}}",
                    "description": "{{PLUGIN_DESCRIPTION}}",
                    "toolkit_config": {
                        "type": "{{PLUGIN_NAME}} Configuration",
                        "description": "Configuration for {{PLUGIN_NAME}}.",
                        "parameters": {},
                    },
                    "provided_tools": [
                        # Tools will be generated by setup_template.py
                        {
                            "name": "example_tool",
                            "args_schema": {
                                "input_data": {
                                    "type": "String",
                                    "required": False,
                                    "description": "Input data for processing"
                                },
                                "option": {
                                    "type": "String", 
                                    "required": False,
                                    "description": "Processing option"
                                }
                            },
                            "description": "Example tool for demonstration",
                            "tool_metadata": {
                                "result_target": "artifact",
                                "result_extension": "json",
                                "result_encoding": "utf-8"
                            },
                            "tool_result_type": "String",
                            "sync_invocation_supported": True,
                            "async_invocation_supported": False
                        }
                    ],
                    "toolkit_metadata": {},
                }
            ]
        }
        
        return descriptor
'''
    
    with open(f"{template_dir}/routes/descriptor.py", 'w') as f:
        f.write(descriptor_content)
    
    # routes/invoke.py
    invoke_content = '''#!/usr/bin/python3
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
        if toolkit_name != "{{TOOLKIT_NAME}}":
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
            if tool_name == "example_tool":
                result = self._handle_example_tool(parameters)
            # Additional tool routes will be generated by setup_template.py
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

    def _handle_example_tool(self, parameters):
        """ Handle example_tool """
        return self.example_tool(
            input_data=parameters.get("input_data"),
            option=parameters.get("option")
        )

    # Additional handler methods will be generated by setup_template.py
'''
    
    with open(f"{template_dir}/routes/invoke.py", 'w') as f:
        f.write(invoke_content)
    
    # routes/invocations.py
    invocations_content = '''#!/usr/bin/python3
# coding=utf-8

""" Invocation Status Route """

import flask
from pylon.core.tools import web


class Route:
    """ Invocation status route """

    @web.route("/tools/<toolkit_name>/<tool_name>/invocations/<invocation_id>", methods=["GET", "DELETE"])
    def invocations_route(self, toolkit_name, tool_name, invocation_id):
        """ Handle invocation status requests """
        
        if flask.request.method == "GET":
            # For synchronous operations, always return completed
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
'''
    
    with open(f"{template_dir}/routes/invocations.py", 'w') as f:
        f.write(invocations_content)
    
    # routes/health.py
    health_content = '''#!/usr/bin/python3
# coding=utf-8

""" Health Check Route """

import time
import datetime
from pylon.core.tools import web


class Route:
    """ Health check route """

    @web.route("/health")
    def health_route(self):
        """ Return plugin health status """
        try:
            current_time = time.time()
            uptime = current_time - getattr(self, 'start_time', current_time)
            
            config = self.runtime_config()
            
            return {
                "status": "UP",
                "providerVersion": "1.0.0",
                "uptime": int(uptime),
                "timestamp": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S+00:00"),
                "plugin": "{{PLUGIN_NAME}}",
                "configuration": {
                    "base_path": config.get("base_path"),
                    # Add other relevant config for health check
                },
                "extra_info": {},
            }
        except Exception as e:
            return {
                "status": "DOWN",
                "error": str(e)
            }, 500
'''
    
    with open(f"{template_dir}/routes/health.py", 'w') as f:
        f.write(health_content)


def create_gitignore(template_dir):
    """Create .gitignore file"""
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual environments
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Plugin-specific
/data/
/tmp/
test_parameters.json

# Logs
*.log
logs/
"""
    
    with open(f"{template_dir}/.gitignore", 'w') as f:
        f.write(gitignore_content)


if __name__ == "__main__":
    print("🏗️ Creating ELITEA/Pylon Plugin Template Repository")
    print("=" * 60)
    create_template_repository()
