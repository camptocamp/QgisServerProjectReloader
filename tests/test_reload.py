import os
from qgis.core import QgsProject
import requests
from xml.etree import ElementTree
from shutil import copyfile
import pytest


@pytest.fixture(scope="session", autouse=True)
def set_up():
    # Will be executed before the first test
    copyfile("project.qgs", "base_project.qgs")
    yield
    # Will be executed after the last test
    copyfile("base_project.qgs", "project.qgs")
    os.remove("base_project.qgs")


def _get_capabilities():
    url = "http://172.17.0.1:8380/?SERVICE=WMS&REQUEST=GetCapabilities"
    response = requests.get(url)

    tree = ElementTree.fromstring(response.content)
    layers = tree.getchildren()[1].getchildren()[3]
    layer_count = 0
    for layer in layers.getchildren():
        if "Layer" in layer.tag:
            layer_count += 1
    return layer_count


def test_get_initial_layer_count():
    assert _get_capabilities(), 2


def test_remove_layer_from_project():

    project = QgsProject.instance()
    project.read("project.qgs")
    id_layer = list(project.mapLayers().keys())[0]
    project.removeMapLayer(id_layer)
    project.write()
    assert _get_capabilities(), 1
