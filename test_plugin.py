#!/usr/bin/env python3
"""
ELITEA/Pylon Plugin Test Utility

This script provides automated testing for your plugin to ensure it works correctly.
"""

import sys
import json
import requests
import argparse
import time
from pathlib import Path


class PluginTester:
    """Test utility for ELITEA/Pylon plugins"""
    
    def __init__(self, base_url="http://127.0.0.1:8080"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.timeout = 30
    
    def test_health(self):
        """Test the health endpoint"""
        print("🏥 Testing health endpoint...")
        
        try:
            response = self.session.get(f"{self.base_url}/health")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Health check passed")
                print(f"   📊 Status: {data.get('status', 'unknown')}")
                print(f"   ⏱️ Uptime: {data.get('uptime', 0)} seconds")
                if 'plugin' in data:
                    print(f"   🔌 Plugin: {data['plugin']}")
                return True
            else:
                print(f"   ❌ Health check failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Health check error: {e}")
            return False
    
    def test_descriptor(self):
        """Test the descriptor endpoint"""
        print("📋 Testing descriptor endpoint...")
        
        try:
            response = self.session.get(f"{self.base_url}/descriptor")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Descriptor retrieved successfully")
                
                # Validate structure
                if 'provided_toolkits' in data:
                    toolkits = data['provided_toolkits']
                    print(f"   🛠️ Toolkits: {len(toolkits)}")
                    
                    for toolkit in toolkits:
                        toolkit_name = toolkit.get('name', 'Unknown')
                        tools = toolkit.get('provided_tools', [])
                        print(f"   📦 {toolkit_name}: {len(tools)} tools")
                        
                        for tool in tools:
                            tool_name = tool.get('name', 'Unknown')
                            params = tool.get('args_schema', {})
                            print(f"      🔧 {tool_name}: {len(params)} parameters")
                
                return data
            else:
                print(f"   ❌ Descriptor failed: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"   ❌ Descriptor error: {e}")
            return None
    
    def test_tool_invocation(self, toolkit_name, tool_name, parameters=None):
        """Test a tool invocation"""
        print(f"🚀 Testing tool: {toolkit_name}/{tool_name}")
        
        if parameters is None:
            parameters = {}
        
        try:
            url = f"{self.base_url}/tools/{toolkit_name}/{tool_name}/invoke"
            payload = {"parameters": parameters}
            
            response = self.session.post(url, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Tool invocation successful")
                print(f"   🆔 Invocation ID: {data.get('invocation_id', 'N/A')}")
                print(f"   📊 Status: {data.get('status', 'Unknown')}")
                
                if 'result' in data:
                    result = data['result']
                    if isinstance(result, dict):
                        if 'success' in result:
                            success = result['success']
                            print(f"   🎯 Result: {'Success' if success else 'Failed'}")
                            if not success and 'error' in result:
                                print(f"   ⚠️ Error: {result['error']}")
                        else:
                            print(f"   📄 Result keys: {list(result.keys())}")
                    else:
                        print(f"   📄 Result type: {type(result).__name__}")
                
                return data
            else:
                print(f"   ❌ Tool invocation failed: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   💬 Error: {error_data.get('message', 'Unknown error')}")
                except:
                    print(f"   💬 Error: {response.text}")
                return None
                
        except Exception as e:
            print(f"   ❌ Tool invocation error: {e}")
            return None
    
    def test_invocation_status(self, toolkit_name, tool_name, invocation_id):
        """Test invocation status checking"""
        print(f"📊 Testing invocation status: {invocation_id}")
        
        try:
            url = f"{self.base_url}/tools/{toolkit_name}/{tool_name}/invocations/{invocation_id}"
            response = self.session.get(url)
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Status check successful")
                print(f"   📊 Status: {data.get('status', 'Unknown')}")
                return data
            else:
                print(f"   ❌ Status check failed: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"   ❌ Status check error: {e}")
            return None
    
    def auto_test_all_tools(self):
        """Automatically test all tools with empty parameters"""
        print("🤖 Auto-testing all tools...")
        
        descriptor = self.test_descriptor()
        if not descriptor:
            print("   ❌ Cannot auto-test without descriptor")
            return False
        
        success_count = 0
        total_count = 0
        
        for toolkit in descriptor.get('provided_toolkits', []):
            toolkit_name = toolkit.get('name')
            
            for tool in toolkit.get('provided_tools', []):
                tool_name = tool.get('name')
                total_count += 1
                
                # Try with empty parameters first
                result = self.test_tool_invocation(toolkit_name, tool_name, {})
                
                if result:
                    success_count += 1
                    
                    # Test status if we got an invocation ID
                    invocation_id = result.get('invocation_id')
                    if invocation_id:
                        self.test_invocation_status(toolkit_name, tool_name, invocation_id)
        
        print(f"\n📈 Auto-test results: {success_count}/{total_count} tools passed")
        return success_count == total_count
    
    def run_full_test_suite(self):
        """Run the complete test suite"""
        print("🧪 Running full plugin test suite...")
        print("=" * 50)
        
        tests_passed = 0
        total_tests = 3
        
        # Test 1: Health check
        if self.test_health():
            tests_passed += 1
        
        print()
        
        # Test 2: Descriptor
        descriptor = self.test_descriptor()
        if descriptor:
            tests_passed += 1
        
        print()
        
        # Test 3: Tool auto-testing
        if self.auto_test_all_tools():
            tests_passed += 1
        
        print()
        print("=" * 50)
        print(f"🏆 Test Results: {tests_passed}/{total_tests} test suites passed")
        
        if tests_passed == total_tests:
            print("🎉 All tests passed! Your plugin is working correctly.")
            return True
        else:
            print("⚠️ Some tests failed. Check the output above for details.")
            return False


def create_sample_test_parameters():
    """Create sample test parameters file"""
    sample_config = {
        "description": "Sample test parameters for your plugin tools",
        "tests": [
            {
                "toolkit_name": "YourToolkitName",
                "tool_name": "your_tool_name",
                "parameters": {
                    "param1": "sample_value",
                    "param2": 42,
                    "param3": True
                },
                "description": "Sample test for your_tool_name"
            }
        ]
    }
    
    with open('test_parameters.json', 'w') as f:
        json.dump(sample_config, f, indent=2)
    
    print("📄 Created test_parameters.json with sample configuration")
    print("   Edit this file to add specific test cases for your tools")


def load_custom_tests():
    """Load custom test parameters from file"""
    if Path('test_parameters.json').exists():
        try:
            with open('test_parameters.json', 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Error loading test_parameters.json: {e}")
    return None


def main():
    """Main test function"""
    parser = argparse.ArgumentParser(description='Test ELITEA/Pylon plugin')
    parser.add_argument('--url', default='http://127.0.0.1:8080', 
                       help='Plugin base URL (default: http://127.0.0.1:8080)')
    parser.add_argument('--test', choices=['health', 'descriptor', 'invoke', 'all'], 
                       default='all', help='Which test to run')
    parser.add_argument('--toolkit', help='Toolkit name for invoke test')
    parser.add_argument('--tool', help='Tool name for invoke test')
    parser.add_argument('--create-sample', action='store_true', 
                       help='Create sample test_parameters.json file')
    parser.add_argument('--custom-tests', action='store_true',
                       help='Run custom tests from test_parameters.json')
    
    args = parser.parse_args()
    
    if args.create_sample:
        create_sample_test_parameters()
        return
    
    tester = PluginTester(args.url)
    
    if args.custom_tests:
        print("🎯 Running custom tests...")
        custom_config = load_custom_tests()
        if custom_config:
            for test in custom_config.get('tests', []):
                tester.test_tool_invocation(
                    test['toolkit_name'],
                    test['tool_name'],
                    test.get('parameters', {})
                )
        else:
            print("❌ No custom tests found. Use --create-sample first.")
        return
    
    if args.test == 'health':
        tester.test_health()
    elif args.test == 'descriptor':
        tester.test_descriptor()
    elif args.test == 'invoke':
        if not args.toolkit or not args.tool:
            print("❌ --toolkit and --tool are required for invoke test")
            sys.exit(1)
        tester.test_tool_invocation(args.toolkit, args.tool)
    elif args.test == 'all':
        success = tester.run_full_test_suite()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
