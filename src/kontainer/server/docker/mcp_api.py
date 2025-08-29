from flask import jsonify, request, Blueprint, g
from flask_jwt_extended.view_decorators import jwt_required

from kontainer.server.middleware import docker_service_middleware
from kontainer.util.docker_mcp_util import DockerMCPProxy

mcp_api_bp = Blueprint('mcp_api', __name__, url_prefix='/api/docker/mcp')
docker_service_middleware(mcp_api_bp)


@mcp_api_bp.route('/version', methods=["GET"])
@jwt_required()
def mcp_version():
    """
    Get Engine Info

    :return: dict
    """
    docker_host = g.dkr_host
    mcp_proxy = DockerMCPProxy(docker_host=docker_host)
    version = mcp_proxy.mcp_version()
    return jsonify({"version": version})


@mcp_api_bp.route('/tools', methods=["GET"])
@jwt_required()
def mcp_tools():
    """
    List all available MCP tools

    :return: list of tool names
    """
    docker_host = g.dkr_host
    mcp_proxy = DockerMCPProxy(docker_host=docker_host)
    try:
        tools = mcp_proxy.list_mcp_tools()
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({"tools": tools})


@mcp_api_bp.route('/tools/<string:tool_name>', methods=["POST"])
@jwt_required()
def run_mcp_tool(tool_name):
    """
    Run a specific MCP tool with the given arguments.
    The arguments should be provided in the request body as JSON.

    :param tool_name: Name of the MCP tool to run
    :return: Output of the tool execution
    """
    kwargs = request.get_json() or {}
    docker_host = g.dkr_host
    mcp_proxy = DockerMCPProxy(docker_host=docker_host)
    output = mcp_proxy.run_mcp_tool(tool_name, **kwargs)
    return jsonify({"output": output})