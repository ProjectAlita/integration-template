#!/usr/bin/env python3
"""
ELITEA/Pylon Plugin Template Setup Script

This script helps you customize the plugin template for your specific tool.
It will prompt for information about your plugin and update all the template files accordingly.
"""

import os
import json
import re
import sys
from pathlib import Path


def get_user_input():
    """Collect information about the user's plugin"""
    print("🚀 ELITEA/Pylon Plugin Template Setup")
    print("=" * 50)
    print("This script will customize the template for your specific tool.\n")
    
    # Basic plugin info
    plugin_name = input("Plugin name (e.g., 'ImageProcessor', 'VideoConverter'): ").strip()
    if not plugin_name:
        print("❌ Plugin name is required!")
        sys.exit(1)
    
    plugin_description = input("Plugin description: ").strip()
    if not plugin_description:
        plugin_description = f"Integration plugin for {plugin_name}"
    
    # Toolkit info
    toolkit_name = input(f"Toolkit name (default: '{plugin_name}Toolkit'): ").strip()
    if not toolkit_name:
        toolkit_name = f"{plugin_name}Toolkit"
    
    # Tools
    print("\n📋 Tool Configuration")
    print("Enter your tools one by one. Press Enter with empty name to finish.")
    
    tools = []
    while True:
        tool_name = input(f"Tool name (tool {len(tools) + 1}): ").strip()
        if not tool_name:
            break
        
        tool_description = input(f"Description for '{tool_name}': ").strip()
        if not tool_description:
            tool_description = f"Execute {tool_name} operation"
        
        # Simple parameter collection
        print(f"Parameters for '{tool_name}' (press Enter to skip):")
        parameters = {}
        while True:
            param_name = input("  Parameter name (or Enter to finish): ").strip()
            if not param_name:
                break
            
            param_type = input(f"  Type for '{param_name}' (string/integer/boolean): ").strip()
            if param_type not in ['string', 'integer', 'boolean']:
                param_type = 'string'
            
            param_required = input(f"  Is '{param_name}' required? (y/N): ").strip().lower() == 'y'
            param_description = input(f"  Description for '{param_name}': ").strip()
            
            parameters[param_name] = {
                'type': param_type.title(),
                'required': param_required,
                'description': param_description or f"{param_name} parameter"
            }
        
        tools.append({
            'name': tool_name,
            'description': tool_description,
            'parameters': parameters
        })
    
    if not tools:
        print("❌ At least one tool is required!")
        sys.exit(1)
    
    # Dependencies
    print("\n📦 Dependencies")
    dependencies = input("Python packages needed (comma-separated, e.g., 'Pillow,requests'): ").strip()
    dependencies = [dep.strip() for dep in dependencies.split(',') if dep.strip()]
    
    # Configuration
    print("\n⚙️ Configuration")
    config_options = {}
    while True:
        config_key = input("Configuration key (or Enter to finish): ").strip()
        if not config_key:
            break
        config_value = input(f"Default value for '{config_key}': ").strip()
        config_options[config_key] = config_value
    
    return {
        'plugin_name': plugin_name,
        'plugin_description': plugin_description,
        'toolkit_name': toolkit_name,
        'tools': tools,
        'dependencies': dependencies,
        'config_options': config_options
    }


def update_file_content(file_path, replacements):
    """Update a file with the given replacements"""
    if not os.path.exists(file_path):
        return
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    for old, new in replacements.items():
        content = content.replace(old, new)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)


def generate_tool_schema(tools):
    """Generate the tools schema for the descriptor"""
    tool_schemas = []
    
    for tool in tools:
        schema = {
            "name": tool['name'],
            "args_schema": {},
            "description": tool['description'],
            "tool_metadata": {
                "result_target": "artifact",
                "result_extension": "json",
                "result_encoding": "utf-8"
            },
            "tool_result_type": "String",
            "sync_invocation_supported": True,
            "async_invocation_supported": False
        }
        
        for param_name, param_info in tool['parameters'].items():
            schema["args_schema"][param_name] = {
                "type": param_info['type'],
                "required": param_info['required'],
                "description": param_info['description']
            }
        
        tool_schemas.append(schema)
    
    return tool_schemas


def format_tools_for_descriptor(tools_schema):
    """Format tools schema as clean Python code for the descriptor"""
    if not tools_schema:
        return "[]"
    
    tool_lines = []
    for tool in tools_schema:
        # Format args_schema
        args_schema_lines = []
        for param_name, param_info in tool.get("args_schema", {}).items():
            param_lines = [
                f'                        "{param_name}": {{',
                f'                            "type": "{param_info["type"]}",',
                f'                            "required": {param_info["required"]},',
                f'                            "description": "{param_info["description"]}"',
                '                        }'
            ]
            args_schema_lines.append('\n'.join(param_lines))
        
        args_schema_str = ",\n".join(args_schema_lines) if args_schema_lines else ""
        
        # Format the tool
        tool_str = f'''                {{
                    "name": "{tool["name"]}",
                    "args_schema": {{
{args_schema_str}
                    }},
                    "description": "{tool["description"]}",
                    "tool_metadata": {{
                        "result_target": "{tool["tool_metadata"]["result_target"]}",
                        "result_extension": "{tool["tool_metadata"]["result_extension"]}",
                        "result_encoding": "{tool["tool_metadata"]["result_encoding"]}"
                    }},
                    "tool_result_type": "{tool["tool_result_type"]}",
                    "sync_invocation_supported": {tool["sync_invocation_supported"]},
                    "async_invocation_supported": {tool["async_invocation_supported"]}
                }}'''
        
        tool_lines.append(tool_str)
    
    return "[\n" + ",\n".join(tool_lines) + "\n            ]"


def generate_invoke_methods(tools):
    """Generate method implementations for tools"""
    methods = []
    
    for tool in tools:
        method_code = f'''
    def _handle_{tool['name']}(self, parameters):
        """ Handle {tool['name']} tool """
        # Validate required parameters
        required_params = {[p for p, info in tool['parameters'].items() if info['required']]}
        for param in required_params:
            if param not in parameters:
                raise ValueError(f"Missing required parameter: {{param}}")
        
        # TODO: Implement your {tool['name']} logic here
        result = self.{tool['name']}(**parameters)
        return result'''
        
        methods.append(method_code)
    
    return '\n'.join(methods)


def generate_tool_operations(tools):
    """Generate tool operation methods"""
    operations = []
    
    for tool in tools:
        params = ', '.join([f"{p}=None" for p in tool['parameters'].keys()])
        operation_code = f'''
    @web.method()
    def {tool['name']}(self, {params}):
        """ {tool['description']} """
        try:
            # TODO: Implement your {tool['name']} logic here
            # This is a placeholder implementation
            result = {{
                "success": True,
                "message": "{tool['name']} completed successfully",
                "parameters": {{{', '.join([f'"{p}": {p}' for p in tool['parameters'].keys()])}}}
            }}
            
            return result
            
        except Exception as e:
            log.error(f"{tool['name']} failed: {{str(e)}}")
            return {{
                "success": False,
                "error": str(e)
            }}'''
        
        operations.append(operation_code)
    
    return '\n'.join(operations)


def create_template_files(config):
    """Create and customize all template files"""
    
    # Basic replacements
    replacements = {
        '{{PLUGIN_NAME}}': config['plugin_name'],
        '{{PLUGIN_DESCRIPTION}}': config['plugin_description'],
        '{{TOOLKIT_NAME}}': config['toolkit_name'],
        '{{PLUGIN_NAME_LOWER}}': config['plugin_name'].lower(),
        '{{PLUGIN_NAME_SNAKE}}': re.sub(r'(?<!^)(?=[A-Z])', '_', config['plugin_name']).lower(),
    }
    
    # Update metadata.json
    metadata = {
        "name": f"Host for tools: {config['plugin_name']}",
        "version": "1.0.0",
        "description": config['plugin_description'],
        "depends_on": [],
        "init_after": []
    }
    
    with open('metadata.json', 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)
    
    # Update config.yml
    config_yml = f"# {config['plugin_name']} Plugin Configuration\n"
    config_yml += "service_location_url: http://127.0.0.1:8080\n"
    config_yml += f"base_path: /tmp/{config['plugin_name'].lower()}\n"
    
    for key, value in config['config_options'].items():
        config_yml += f"{key}: {value}\n"
    
    with open('config.yml', 'w', encoding='utf-8') as f:
        f.write(config_yml)
    
    # Update requirements.txt
    requirements = ['flask>=2.0.0', 'requests>=2.25.0']
    requirements.extend(config['dependencies'])
    
    with open('requirements.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(requirements))
    
    # Create template files with placeholders
    create_template_python_files(config)
    
    # Apply replacements to all Python files
    python_files = [
        '__init__.py', 'module.py',
        'methods/__init__.py', 'methods/init.py', 'methods/config.py', 
        'methods/dependencies.py', 'methods/tool_operations.py',
        'routes/__init__.py', 'routes/descriptor.py', 'routes/invoke.py',
        'routes/invocations.py', 'routes/health.py'
    ]
    
    for file_path in python_files:
        update_file_content(file_path, replacements)


def create_template_python_files(config):
    """Create all the Python template files"""
    
    # Create directories
    os.makedirs('methods', exist_ok=True)
    os.makedirs('routes', exist_ok=True)
    
    # __init__.py
    with open('__init__.py', 'w', encoding='utf-8') as f:
        f.write('#!/usr/bin/python3\n# coding=utf-8\n""" {{PLUGIN_NAME}} Plugin """\nfrom .module import Module\n')
    
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
    
    with open('module.py', 'w', encoding='utf-8') as f:
        f.write(module_content)
    
    # methods/__init__.py
    with open('methods/__init__.py', 'w', encoding='utf-8') as f:
        f.write('#!/usr/bin/python3\n# coding=utf-8\n""" {{PLUGIN_NAME}} Methods """\n')
    
    # methods/init.py
    init_content = '''#!/usr/bin/python3
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
        log.info(f"{{PLUGIN_NAME}} configured with base_path: {config['base_path']}")
        
        # Store start time for health checks
        self.start_time = time.time()
        
        # Setup dependencies
        self.setup_dependencies()
'''
    
    with open('methods/init.py', 'w', encoding='utf-8') as f:
        f.write(init_content)
    
    # methods/config.py
    config_content = '''#!/usr/bin/python3
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
        
        if "base_path" in config:
            pathlib.Path(config["base_path"]).mkdir(parents=True, exist_ok=True)
            log.info(f"Created directory: {config['base_path']}")
'''
    
    with open('methods/config.py', 'w', encoding='utf-8') as f:
        f.write(config_content)
    
    # methods/dependencies.py
    dependencies_content = '''#!/usr/bin/python3
# coding=utf-8

""" Dependency Management """

from pylon.core.tools import log, web


class Method:
    """ Dependency management methods """

    @web.method()
    def setup_dependencies(self):
        """ Setup and verify dependencies """
        try:
            # TODO: Add dependency checks here
            # Example:
            # import some_required_library
            log.info("{{PLUGIN_NAME}} dependencies verified")
        except ImportError as e:
            log.error(f"Missing dependency: {e}")
            raise RuntimeError(f"{{PLUGIN_NAME}} dependency not available: {e}")

    @web.method()
    def check_dependency(self, module_name):
        """ Check if a specific dependency is available """
        try:
            __import__(module_name)
            return True
        except ImportError:
            return False
'''
    
    with open('methods/dependencies.py', 'w', encoding='utf-8') as f:
        f.write(dependencies_content)
    
    # methods/tool_operations.py
    tool_operations_content = '''#!/usr/bin/python3
# coding=utf-8

""" {{PLUGIN_NAME}} Tool Operations """

from pylon.core.tools import log, web


class Method:
    """ Tool operation methods """
''' + generate_tool_operations(config['tools'])
    
    with open('methods/tool_operations.py', 'w', encoding='utf-8') as f:
        f.write(tool_operations_content)
    
    # routes/__init__.py
    with open('routes/__init__.py', 'w', encoding='utf-8') as f:
        f.write('#!/usr/bin/python3\n# coding=utf-8\n""" {{PLUGIN_NAME}} Routes """\n')
    
    # routes/descriptor.py
    # Generate tool schema with proper formatting
    tools_schema = generate_tool_schema(config['tools'])
    
    # Format the tools for the descriptor
    formatted_tools = format_tools_for_descriptor(tools_schema)
    
    descriptor_content = f'''#!/usr/bin/python3
# coding=utf-8

""" Plugin Descriptor Route """

from pylon.core.tools import web


class Route:
    """ Descriptor route """

    @web.route("/descriptor")
    def descriptor_route(self):
        """ Return plugin descriptor """
        config = self.runtime_config()
        
        descriptor = {{
            "name": "{{{{PLUGIN_NAME}}}}ServiceProvider",
            "service_location_url": config["service_location_url"],
            "configuration": {{}},
            "provided_toolkits": [
                {{
                    "name": "{{{{TOOLKIT_NAME}}}}",
                    "description": "{{{{PLUGIN_DESCRIPTION}}}}",
                    "toolkit_config": {{
                        "type": "{{{{PLUGIN_NAME}}}} Configuration",
                        "description": "Configuration for {{{{PLUGIN_NAME}}}}.",
                        "parameters": {{}}
                    }},
                    "provided_tools": {formatted_tools},
                    "toolkit_metadata": {{}}
                }}
            ]
        }}
        
        return descriptor
'''
    
    with open('routes/descriptor.py', 'w', encoding='utf-8') as f:
        f.write(descriptor_content)
    
    # routes/invoke.py
    # Generate tool route conditionals
    tool_routes = []
    for tool in config['tools']:
        tool_routes.append(f'''            if tool_name == "{tool['name']}":
                result = self._handle_{tool['name']}(parameters)''')
    
    # Create proper if-elif chain
    if tool_routes:
        tool_route_code = tool_routes[0]  # First tool uses 'if'
        for route in tool_routes[1:]:
            tool_route_code += '\n            el' + route[12:]  # Add 'el' to make it 'elif'
    else:
        tool_route_code = ''
    
    invoke_methods = generate_invoke_methods(config['tools'])
    
    invoke_content = f'''#!/usr/bin/python3
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
        if toolkit_name != "{{{{TOOLKIT_NAME}}}}":
            return {{
                "errorCode": "404",
                "message": "Toolkit not found",
                "details": [f"Unknown toolkit: {{toolkit_name}}"]
            }}, 404
        
        try:
            # Get request data
            request_data = flask.request.json
            if not request_data or "parameters" not in request_data:
                return {{
                    "errorCode": "400",
                    "message": "Missing parameters",
                    "details": ["Request must include 'parameters' field"]
                }}, 400
            
            parameters = request_data["parameters"]
            
            # Route to appropriate tool
{tool_route_code}
            else:
                return {{
                    "errorCode": "404",
                    "message": "Tool not found",
                    "details": [f"Unknown tool: {{tool_name}}"]
                }}, 404
            
            # Generate invocation ID
            invocation_id = str(uuid.uuid4())
            
            # Return success response
            return {{
                "invocation_id": invocation_id,
                "status": "Completed",
                "result": result,
                "result_type": "Object"
            }}
            
        except Exception as e:
            log.exception(f"Tool invocation failed: {{toolkit_name}}:{{tool_name}}")
            return {{
                "errorCode": "500",
                "message": "Internal server error",
                "details": [str(e)]
            }}, 500
{invoke_methods}
'''
    
    with open('routes/invoke.py', 'w', encoding='utf-8') as f:
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
'''
    
    with open('routes/invocations.py', 'w', encoding='utf-8') as f:
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
                "configuration": config,
                "extra_info": {},
            }
        except Exception as e:
            return {
                "status": "DOWN",
                "error": str(e)
            }, 500
'''
    
    with open('routes/health.py', 'w', encoding='utf-8') as f:
        f.write(health_content)


def main():
    """Main setup function"""
    print("Setting up ELITEA/Pylon Plugin Template...")
    
    # Get user configuration
    config = get_user_input()
    
    print(f"\n🔧 Creating {config['plugin_name']} plugin...")
    
    # Create all template files
    create_template_files(config)
    
    print(f"\n✅ Template setup complete!")
    print(f"📝 Plugin: {config['plugin_name']}")
    print(f"🛠️ Toolkit: {config['toolkit_name']}")
    print(f"⚙️ Tools: {', '.join([tool['name'] for tool in config['tools']])}")
    
    print(f"\n🚀 Next steps:")
    print(f"1. Implement your tool logic in methods/tool_operations.py")
    print(f"2. Add any dependencies in methods/dependencies.py") 
    print(f"3. Test your plugin with: python test_plugin.py")
    print(f"4. Update README.md with your plugin documentation")
    
    print(f"\n📚 Resources:")
    print(f"- Step-by-step guide: docs/STEP_BY_STEP_GUIDE.md")
    print(f"- Integration patterns: docs/INTEGRATION_PATTERNS.md")


if __name__ == "__main__":
    main()
