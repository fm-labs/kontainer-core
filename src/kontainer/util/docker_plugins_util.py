import subprocess
import json
import os
from typing import Dict, List, Optional


class DockerPluginChecker:
    def __init__(self,
                 docker_bin: str = 'docker',
                 docker_host: str = None,
                 docker_context: str = None,
                 env: Optional[Dict[str, str]] = None):

        self.results = {
            'engine_plugins': [],
            'cli_plugins': [],
            'desktop_extensions': None,
            'special_features': {}
        }
        self.env = env if env is not None else os.environ.copy()
        self.docker_bin = docker_bin
        self.docker_host = docker_host
        self.docker_context = docker_context
        if self.docker_host is not None and self.docker_context is not None:
            raise ValueError("Cannot set both DOCKER_HOST and DOCKER_CONTEXT. Use one or the other.")

        if self.docker_host:
            self.env['DOCKER_HOST'] = self.docker_host
        if self.docker_context:
            self.env['DOCKER_CONTEXT'] = self.docker_context


    def check_engine_plugins(self) -> List[Dict]:
        """Check Docker Engine plugins (runtime plugins)"""
        try:
            result = subprocess.run(['docker', 'plugin', 'ls', '--format', 'json'],
                                    capture_output=True, text=True, timeout=10, env=self.env)

            if result.returncode == 0 and result.stdout.strip():
                plugins = []
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        plugins.append(json.loads(line))
                return plugins
            return []
        except Exception as e:
            print(f"Error checking engine plugins: {e}")
            return []

    def check_cli_plugins(self) -> List[str]:
        """Check Docker CLI plugins"""
        plugins = []

        # Method 1: Check ~/.docker/cli-plugins/ directory
        plugins_dir = os.path.expanduser('~/.docker/cli-plugins/')
        if os.path.exists(plugins_dir):
            for item in os.listdir(plugins_dir):
                item_path = os.path.join(plugins_dir, item)
                if os.path.isfile(item_path) and os.access(item_path, os.X_OK):
                    plugins.append(item)

        # Method 2: Check common CLI plugins by testing commands
        common_plugins = ['compose', 'mcp', 'buildx', 'scan', 'extension']
        for plugin in common_plugins:
            if self._test_cli_plugin(plugin):
                if plugin not in plugins:
                    plugins.append(plugin)

        return plugins

    def _test_cli_plugin(self, plugin_name: str) -> bool:
        """Test if a CLI plugin is available"""
        try:
            result = subprocess.run(['docker', plugin_name, '--help'],
                                    capture_output=True, text=True, timeout=5, env=self.env)
            return result.returncode == 0
        except:
            return False

    def check_desktop_extensions(self) -> Optional[str]:
        """Check Docker Desktop extensions"""
        try:
            # Try docker extension ls command
            result = subprocess.run(['docker', 'extension', 'ls'],
                                    capture_output=True, text=True, timeout=10, env=self.env)
            if result.returncode == 0:
                return result.stdout
        except:
            pass

        return "Docker Desktop extensions not accessible or not installed"

    def check_special_features(self) -> Dict[str, bool]:
        """Check for specific Docker AI features"""
        features = {}

        # Check MCP Toolkit
        features['mcp_toolkit'] = self._test_cli_plugin('mcp')

        # Check Model Runner (could be various command names)
        features['model_runner'] = (
                self._test_cli_plugin('model-runner') or
                self._test_cli_plugin('modelrunner') or
                self._test_cli_plugin('model')
        )

        # Check Docker AI Agent
        features['docker_ai'] = self._test_cli_plugin('ai')

        # Check Docker Compose
        features['docker_compose'] = self._test_cli_plugin('compose')

        # Check Docker Buildx
        features['docker_buildx'] = self._test_cli_plugin('buildx')

        return features


    def run_all_checks(self):
        self.results['engine_plugins'] = self.check_engine_plugins()
        self.results['cli_plugins'] = self.check_cli_plugins()
        self.results['desktop_extensions'] = self.check_desktop_extensions()
        self.results['special_features'] = self.check_special_features()


    def print_results(self):
        """Run all plugin checks"""
        print("🔍 Checking Docker Plugins and Extensions...")
        print("=" * 50)

        # Check engine plugins
        print("\n📦 Docker Engine Plugins:")
        if self.results['engine_plugins']:
            for plugin in self.results['engine_plugins']:
                status = "✅ Enabled" if plugin.get('Enabled') else "❌ Disabled"
                print(f"  • {plugin['Name']} - {status}")
                print(f"    Description: {plugin.get('Description', 'N/A')}")
        else:
            print("  No engine plugins found")

        # Check CLI plugins
        print("\n🔧 Docker CLI Plugins:")
        if self.results['cli_plugins']:
            for plugin in self.results['cli_plugins']:
                print(f"  • {plugin}")
        else:
            print("  No CLI plugins found")

        # Check desktop extensions
        print("\n🖥️  Docker Desktop Extensions:")
        print(f"  {self.results['desktop_extensions']}")

        # Check special features
        print("\n🤖 Special AI Features:")
        for feature, available in self.results['special_features'].items():
            status = "✅ Available" if available else "❌ Not Available"
            feature_name = feature.replace('_', ' ').title()
            print(f"  • {feature_name}: {status}")

        return self.results

    def get_json_output(self) -> str:
        """Return results as JSON"""
        return json.dumps(self.results, indent=2)