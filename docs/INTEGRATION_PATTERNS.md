# Common Integration Patterns for ELITEA/Pylon Plugins

This document covers common patterns and examples for different types of tool integrations. Each pattern includes working code examples you can adapt for your own plugins.

> **🚀 New to plugin development?** Start with the [Step-by-Step Guide](STEP_BY_STEP_GUIDE.md) first.
> 
> **⚡ Want a minimal example?** Check the [Quick Start Template](QUICK_START_TEMPLATE.md).
> 
> **📖 Need comprehensive details?** See the [Integration Guide](INTEGRATION_GUIDE.md).

## Pattern 1: Python Library Integration

For integrating Python libraries directly (e.g., PIL, pandas, matplotlib):

### Example: Image Processing with PIL

```python
# requirements.txt
Pillow>=9.0.0
```

```python
# routes/invoke.py
import base64
import io
from PIL import Image, ImageFilter

class Route:
    def process_with_my_tool(self, input_data, options):
        # Decode base64 image
        image_data = base64.b64decode(input_data)
        image = Image.open(io.BytesIO(image_data))
        
        # Apply processing based on options
        if options.get("blur"):
            image = image.filter(ImageFilter.BLUR)
        
        if options.get("resize"):
            size = options["resize"]
            image = image.resize((size["width"], size["height"]))
        
        # Encode result
        output = io.BytesIO()
        image.save(output, format='PNG')
        return base64.b64encode(output.getvalue()).decode()
```

```python
# routes/descriptor.py - Update args_schema
"args_schema": {
    "image_data": {
        "type": "String",
        "required": True,
        "description": "Base64 encoded image data"
    },
    "options": {
        "type": "Object",
        "required": False,
        "description": "Processing options (blur, resize, etc.)"
    }
}
```

## Pattern 2: CLI Tool Integration

For wrapping command-line tools:

### Example: FFmpeg Video Processing

```python
# methods/binaries.py
import subprocess
import os
from pylon.core.tools import web, process

class Method:
    @web.method()
    def setup_ffmpeg(self, config):
        # Check if ffmpeg is available
        try:
            process.run_command(["ffmpeg", "-version"])
        except FileNotFoundError:
            raise RuntimeError("FFmpeg not found. Please install FFmpeg.")
```

```python
# routes/invoke.py
import tempfile
import os
import shutil
from pylon.core.tools import process

class Route:
    def process_with_my_tool(self, input_data, options):
        work_dir = tempfile.mkdtemp()
        try:
            # Save input video
            input_path = os.path.join(work_dir, "input.mp4")
            with open(input_path, "wb") as f:
                f.write(base64.b64decode(input_data))
            
            # Prepare output path
            output_path = os.path.join(work_dir, "output.mp4")
            
            # Build ffmpeg command
            cmd = ["ffmpeg", "-i", input_path]
            
            if options.get("scale"):
                scale = options["scale"]
                cmd.extend(["-vf", f"scale={scale['width']}:{scale['height']}"])
            
            if options.get("bitrate"):
                cmd.extend(["-b:v", options["bitrate"]])
            
            cmd.append(output_path)
            
            # Execute ffmpeg
            result = process.run_command(cmd, capture_output=True)
            
            if result.returncode != 0:
                raise RuntimeError(f"FFmpeg error: {result.stderr}")
            
            # Read result
            with open(output_path, "rb") as f:
                return base64.b64encode(f.read()).decode()
                
        finally:
            shutil.rmtree(work_dir)
```

## Pattern 3: Node.js Tool Integration

For integrating Node.js-based tools (following template pattern):

### Example: Puppeteer Web Scraping

```python
# methods/binaries.py
class Method:
    @web.method()
    def node_packages(self, config):
        packages = [
            "puppeteer",
            "cheerio"
        ]
        
        node_bin = config["node_bin"]
        npm_binary = config["bin_npm"]
        
        node_env = os.environ.copy()
        node_env["PATH"] = os.pathsep.join([os.environ["PATH"], node_bin])
        
        for package in packages:
            package_path = os.path.join(config["node_modules"], package)
            if not os.path.exists(package_path):
                process.run_command([npm_binary, "i", "-g", package], env=node_env)
```

```javascript
// Create scraper.js in your plugin directory
const puppeteer = require('puppeteer');

async function scrapePage(url, selector) {
    const browser = await puppeteer.launch();
    const page = await browser.newPage();
    await page.goto(url);
    
    const content = await page.evaluate((sel) => {
        const element = document.querySelector(sel);
        return element ? element.textContent : null;
    }, selector);
    
    await browser.close();
    return content;
}

// Read command line arguments
const args = process.argv.slice(2);
const url = args[0];
const selector = args[1];

scrapePage(url, selector)
    .then(result => console.log(result))
    .catch(error => {
        console.error(error);
        process.exit(1);
    });
```

```python
# routes/invoke.py
class Route:
    def process_with_my_tool(self, input_data, options):
        config = self.runtime_config()
        node_bin = config["node_bin"]
        
        # Setup environment
        env = os.environ.copy()
        env["PATH"] = os.pathsep.join([env["PATH"], node_bin])
        
        # Execute Node.js script
        script_path = os.path.join(os.path.dirname(__file__), "..", "scraper.js")
        url = input_data
        selector = options.get("selector", "body")
        
        result = process.run_command([
            "node", script_path, url, selector
        ], env=env, capture_output=True)
        
        if result.returncode != 0:
            raise RuntimeError(f"Scraping failed: {result.stderr}")
        
        return result.stdout.strip()
```

## Pattern 4: REST API Integration

For integrating with external REST APIs:

### Example: Translation Service

```python
# routes/invoke.py
import requests

class Route:
    def process_with_my_tool(self, input_data, options):
        config = self.runtime_config()
        api_key = config.get("translation_api_key")
        
        if not api_key:
            raise ValueError("Translation API key not configured")
        
        # Call external API
        response = requests.post(
            "https://api.translate.service.com/v1/translate",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "text": input_data,
                "source_lang": options.get("source_lang", "auto"),
                "target_lang": options.get("target_lang", "en")
            }
        )
        
        response.raise_for_status()
        return response.json()["translated_text"]
```

```yaml
# config.yml
translation_api_key: ${TRANSLATION_API_KEY}  # Environment variable
```

## Pattern 5: Database Integration

For tools that work with databases:

### Example: Data Processing with SQLAlchemy

```python
# requirements.txt
sqlalchemy>=1.4.0
pandas>=1.3.0
```

```python
# methods/config.py
class Method:
    @web.method()
    def runtime_config(self):
        result = super().runtime_config()
        
        # Add database configuration
        db_config = {
            "db_url": "sqlite:///data.db",
            "connection_timeout": 30,
        }
        
        for key, default in db_config.items():
            result[key] = self.descriptor.config.get(key, default)
        
        return result
```

```python
# routes/invoke.py
import pandas as pd
from sqlalchemy import create_engine

class Route:
    def process_with_my_tool(self, input_data, options):
        config = self.runtime_config()
        engine = create_engine(config["db_url"])
        
        # Parse SQL query from input
        query = input_data
        
        # Execute query and return results
        df = pd.read_sql(query, engine)
        
        # Format output based on options
        output_format = options.get("format", "json")
        
        if output_format == "csv":
            return df.to_csv(index=False)
        elif output_format == "html":
            return df.to_html(index=False)
        else:
            return df.to_json(orient="records")
```

## Pattern 6: File Processing

For tools that process files:

### Example: Document Converter

```python
# requirements.txt
python-docx>=0.8.11
pypdf2>=2.0.0
```

```python
# routes/invoke.py
import tempfile
import os
from docx import Document
import PyPDF2

class Route:
    def process_with_my_tool(self, input_data, options):
        work_dir = tempfile.mkdtemp()
        try:
            input_format = options.get("input_format", "pdf")
            output_format = options.get("output_format", "txt")
            
            # Save input file
            input_path = os.path.join(work_dir, f"input.{input_format}")
            with open(input_path, "wb") as f:
                f.write(base64.b64decode(input_data))
            
            # Process based on formats
            if input_format == "pdf" and output_format == "txt":
                return self.pdf_to_text(input_path)
            elif input_format == "docx" and output_format == "txt":
                return self.docx_to_text(input_path)
            else:
                raise ValueError(f"Conversion from {input_format} to {output_format} not supported")
                
        finally:
            shutil.rmtree(work_dir)
    
    def pdf_to_text(self, pdf_path):
        with open(pdf_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            return text
    
    def docx_to_text(self, docx_path):
        doc = Document(docx_path)
        return "\n".join([paragraph.text for paragraph in doc.paragraphs])
```

## Pattern 7: Machine Learning Model Integration

For ML model serving:

### Example: TensorFlow Model

```python
# requirements.txt
tensorflow>=2.8.0
numpy>=1.21.0
```

```python
# methods/init.py
import tensorflow as tf

class Method:
    @web.init()
    def init(self):
        config = self.runtime_config()
        
        # Load model during initialization
        model_path = config.get("model_path", "model.h5")
        self.model = tf.keras.models.load_model(model_path)
        
        self.start_ts = time.time()
```

```python
# routes/invoke.py
import numpy as np
import json

class Route:
    def process_with_my_tool(self, input_data, options):
        # Parse input data
        data = json.loads(input_data)
        input_array = np.array(data["features"])
        
        # Reshape if needed
        if len(input_array.shape) == 1:
            input_array = input_array.reshape(1, -1)
        
        # Make prediction
        prediction = self.model.predict(input_array)
        
        # Format output
        return {
            "prediction": prediction.tolist(),
            "confidence": float(np.max(prediction))
        }
```

## Error Handling Patterns

### Comprehensive Error Handling

```python
# routes/invoke.py
import traceback
from pylon.core.tools import log

class Route:
    @web.route("/tools/<toolkit_name>/<tool_name>/invoke", methods=["POST"])
    def invoke_route(self, toolkit_name, tool_name):
        try:
            # Validation
            if toolkit_name != "MyToolkit":
                return self.error_response(404, "Toolkit not found", [f"Unknown toolkit: {toolkit_name}"])
            
            if tool_name not in ["process_data", "other_tool"]:
                return self.error_response(404, "Tool not found", [f"Unknown tool: {tool_name}"])
            
            request_data = flask.request.json
            if not request_data:
                return self.error_response(400, "Invalid JSON", ["Request body must be valid JSON"])
            
            if "parameters" not in request_data:
                return self.error_response(400, "Missing parameters", ["Request must include 'parameters' field"])
            
            # Tool execution
            result = self.process_with_my_tool(request_data["parameters"])
            
            return {
                "invocation_id": str(uuid.uuid4()),
                "status": "Completed",
                "result": result,
                "result_type": "String",
            }
            
        except ValueError as e:
            log.warning("Validation error: %s", str(e))
            return self.error_response(400, "Validation Error", [str(e)])
        
        except FileNotFoundError as e:
            log.error("Resource not found: %s", str(e))
            return self.error_response(404, "Resource Not Found", [str(e)])
        
        except Exception as e:
            log.exception("Unexpected error in %s:%s", toolkit_name, tool_name)
            return self.error_response(500, "Internal Server Error", ["An unexpected error occurred"])
    
    def error_response(self, code, message, details):
        return {
            "errorCode": str(code),
            "message": message,
            "details": details,
        }, code
```

## Configuration Patterns

### Environment-Based Configuration

```yaml
# config.yml
service_location_url: ${SERVICE_URL:http://127.0.0.1:8080}
api_key: ${API_KEY}
debug_mode: ${DEBUG:false}
database_url: ${DATABASE_URL:sqlite:///app.db}
```

```python
# methods/config.py
import os

class Method:
    @web.method()
    def runtime_config(self):
        result = {}
        
        # Process environment variables in config
        config_map = {
            "service_location_url": "http://127.0.0.1:8080",
            "api_key": None,
            "debug_mode": False,
            "database_url": "sqlite:///app.db",
        }
        
        for key, default in config_map.items():
            # Get from config file (which may have env var references)
            value = self.descriptor.config.get(key, default)
            
            # Handle environment variable references
            if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                env_spec = value[2:-1]  # Remove ${ and }
                if ":" in env_spec:
                    env_var, default_val = env_spec.split(":", 1)
                    value = os.getenv(env_var, default_val)
                else:
                    value = os.getenv(env_spec)
                    if value is None:
                        raise ValueError(f"Required environment variable {env_spec} not set")
            
            result[key] = value
        
        return result
```

These patterns should cover most common integration scenarios. Choose the pattern that best fits your tool and customize as needed.
