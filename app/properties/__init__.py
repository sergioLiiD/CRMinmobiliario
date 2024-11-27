from flask import Blueprint

bp = Blueprint('properties', __name__)

from . import routes  # noqa
