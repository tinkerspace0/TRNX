# core/plugin/__init__.py
from .plugin_factory import create_template, package_plugin

from .plugin_base import Plugin

from .exchange_interface import ExchangeInterface
from .data_plugins import DataPlugin, Indicator, Feature