import os
import subprocess
import json


class DockerMCPProxy:

    def __init__(self, docker_bin='docker', docker_host=None, docker_context=None, env=None):
        """
        Initialize the DockerMCPProxy class.
        This class provides methods to interact with the MCP CLI via Docker.
        """
        print(f"Initializing MCP proxy for docker_host={docker_host}")

        self.docker_bin = docker_bin
        self.docker_host = docker_host
        self.docker_context = docker_context
        self.env = env if env is not None else {}
        self.env["PATH"] = os.environ.get("PATH", "")

        if self.docker_host:
            self.env['DOCKER_HOST'] = self.docker_host
        #if self.docker_context:
        #     self.env['DOCKER_CONTEXT'] = self.docker_context

        # print env
        for key, value in self.env.items():
            print(f"Env: {key}={value}")


    def mcp_version(self):
        """
        Get MCP version.

        :return: MCP version string
        """
        try:
            env = self.env.copy()
            result = subprocess.run(
                ["docker", "mcp", "--version"],
                capture_output=True,
                text=True,
                check=True,
                env=env
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            print(f"Error getting MCP version: {e}")
            return None

    def list_mcp_tools(self):
        """
        List all available MCP tools via docker mcp cli.

        :return: List of tool names
        """
        try:
            env = self.env.copy()
            result = subprocess.run(
                ["docker", "mcp", "tools", "list", "--format", "json"],
                capture_output=True,
                text=True,
                check=False,
                env=env
            )
            if result.returncode != 0:
                raise subprocess.CalledProcessError(result.returncode, result.args, output=result.stdout, stderr=result.stderr)

            tools = json.loads(result.stdout)
            return tools
        except subprocess.CalledProcessError as e:
            print(f"Error listing MCP tools: {e}")
            print(f"Command output: {e.output}")
            print(f"Command stderr: {e.stderr}")
            return []
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            return []


    def run_mcp_tool(self, tool_name, **kwargs):
        """
        Run a specific MCP tool with the given arguments.

        :param tool_name: Name of the MCP tool to run
        :param args: Arguments to pass to the MCP tool
        :return: Output of the tool execution
        """

        # Convert kwargs to mcp call arguments
        cmd_args = []
        for k, v in kwargs.items():
            if v is not None:
                cmd_args.append(f"{k}={v}")

        cmd = ["docker", "mcp", "tools", "call", tool_name] + cmd_args
        print(f"Executing MCP tool cmd '{" ".join(cmd)}'")
        try:
            env = self.env.copy()
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                env=env
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            print(f"Error running MCP tool '{tool_name}': {e}")
            return None