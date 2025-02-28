import json

import flask
from flask import jsonify, request, url_for
from flask_jwt_extended.view_decorators import jwt_required

from kstack.agent.admin.templates import find_templates, write_template, download_template, load_template

templates_api_bp = flask.Blueprint('templates_api', __name__, url_prefix='/api/templates')


@templates_api_bp.route('', methods=["GET"])
@jwt_required()
def list_templates():
    """
    Returns a list of available templates.
    """
    template_ids = find_templates()
    templates = [{
        'template_id': template_id,
        'label': template_id,
        'url': url_for('templates_api.get_template', template_id=template_id, _external=True)
    } for template_id in template_ids]
    return jsonify(templates)


@templates_api_bp.route('', methods=["POST"])
@jwt_required()
def add_template():
    """
    Adds a new template.
    """
    data = request.get_json()
    template_id = data.get('template_id', None)
    template_content = data.get('template_content', None)
    template_url = data.get('template_url', None)

    if template_id is None:
        return jsonify({'error': 'template_id is required'}), 400

    if template_content is None and template_url is None:
        return jsonify({'error': 'content or url is required'}), 400

    if template_content is not None and template_url is not None:
        return jsonify({'error': 'content and url are mutually exclusive'}), 400

    if template_content is not None:
        write_template(template_id, template_content)
        return jsonify({'template_id': template_id, 'status': 'created'}), 201

    if template_url is not None:
        download_template(template_id, template_url)
        return jsonify({'template_id': template_id, 'status': 'created'}), 201


@templates_api_bp.route('/<string:template_id>', methods=["GET"])
@jwt_required()
def get_template(template_id):
    """
    Returns the contents of a specific template.
    """
    try:
        template_contents = load_template(template_id)
    except json.decoder.JSONDecodeError:
        return jsonify({'error': 'Template is not a valid JSON'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    if template_contents is None:
        return jsonify({'error': 'Template not found'}), 404

    # return jsonify({'template_id': template_id, 'content': template_contents})
    return jsonify(template_contents)


@templates_api_bp.route('/<string:template_id>', methods=["POST"])
@jwt_required()
def update_template(template_id):
    """
    Updates an existing template.
    Does the same as 'add_template' but checks if the template exists first.
    """
    template_contents = load_template(template_id)
    if template_contents is None:
        return jsonify({'error': 'Template not found'}), 404

    add_template()
