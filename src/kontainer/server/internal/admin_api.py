import re

import flask
from flask import jsonify, request
from flask_jwt_extended.view_decorators import jwt_required

from kontainer.app import app
from kontainer.admin.credentials import private_key_exists, write_private_key, delete_private_key, find_private_keys
from kontainer.admin.registries import update_container_registry, delete_container_registry, \
    list_container_registries, request_container_registry_login

admin_api_bp = flask.Blueprint('admin_api', __name__, url_prefix='/api/admin')


@admin_api_bp.route('/registries', methods=["GET"])
@jwt_required()
def container_registries_index():
    registries = list_container_registries(safe=True)
    return jsonify(registries)


@admin_api_bp.route('/registries/<string:registry_name>', methods=["POST"])
@jwt_required()
def container_registries_update(registry_name):
    data = request.get_json()
    registry_host = data.get('host', '').strip()
    registry_label = data.get('label', '').strip()
    registry_username = data.get('username', '').strip()
    registry_password = data.get('password', '').strip()
    registry_data = {
        "host": registry_host,
        "label": registry_label,
        "username": registry_username,
        "password": registry_password,
    }
    registry = update_container_registry(registry_name, registry_data)
    return jsonify(registry), 200


@admin_api_bp.route('/registries/<string:registry_name>/login', methods=["POST"])
@jwt_required()
def container_registry_login(registry_name):
    try:
        app.logger.info(f"Requesting login for {registry_name}")
        success = request_container_registry_login(registry_name)
        if not success:
            return jsonify({'error': 'Login failed'}), 401

        return jsonify({'message': 'Login successful'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@admin_api_bp.route('/registries/<string:registry_name>', methods=["DELETE"])
@jwt_required()
def container_registries_delete(registry_name):
    delete_container_registry(registry_name)
    return jsonify({'name': registry_name, 'status': 'deleted'}), 200


@admin_api_bp.route('/keys', methods=["GET"])
@jwt_required()
def private_keys_index():
    private_key_ids = find_private_keys()
    return jsonify(private_key_ids)


@admin_api_bp.route('/keys', methods=["POST"])
@jwt_required()
def private_keys_create_or_update():
    data = request.get_json()

    key_id = data.get('key_id', '').strip()
    if key_id is None or key_id == "":
        return jsonify({'error': 'key_id is required'}), 400

    # check key_id pattern (alphanumeric and underscore)
    pattern = r'^[a-zA-Z0-9_]+$'
    if not re.match(pattern, key_id):
        return jsonify({'error': 'key_id must container only alphanumeric and underscore characters'}), 400

    # # check if key with key_id already exists
    # key_exists = has_private_key(key_id)
    # if key_exists:
    #     return jsonify({'error': 'key_id already exists'}), 400

    key_content = data.get('key_content', '').strip()
    if key_content is None or key_content == "":
        return jsonify({'error': 'key_content is required'}), 400

    try:
        write_private_key(key_id, key_content)
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    return jsonify({'key_id': key_id, 'status': 'created'}), 201


@admin_api_bp.route('/keys/<string:key_id>', methods=["DELETE"])
@jwt_required()
def private_keys_delete(key_id):
    key_exists = private_key_exists(key_id)
    if not key_exists:
        return jsonify({'error': 'key_id does not exist'}), 404

    write_private_key(key_id, "")
    delete_private_key(key_id)
    return jsonify({'key_id': key_id, 'status': 'deleted'}), 200