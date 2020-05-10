from qgis.core import QgsProject, QgsVectorLayer
import requests
from xml.etree import ElementTree

DATA_PATH = "/data"
LAYER1_PATH = "/data/faces.gml"
LAYER2_PATH = "/data/state.gml"
FILE_PROJECT_PATH = "/data/project.qgs"
DB_PROJECT_PATH = "postgresql://qgis:qgis@db:5432?sslmode=disable&dbname=qgis&schema=public&project=project"


def one_layer_file_project():
    project = QgsProject()

    layer = QgsVectorLayer(LAYER1_PATH, "faces", "ogr")
    assert layer.isValid()
    project.addMapLayer(layer)

    project.write(FILE_PROJECT_PATH)


def two_layers_file_project():
    project = QgsProject()

    layer = QgsVectorLayer(LAYER1_PATH, "faces", "ogr")
    assert layer.isValid()
    project.addMapLayer(layer)

    layer = QgsVectorLayer(LAYER2_PATH, "state", "ogr")
    assert layer.isValid()
    project.addMapLayer(layer)

    project.write(FILE_PROJECT_PATH)


def _get_layers_count(project_path):
    url = "http://qgisserver:8000/?SERVICE=WMS&VERSION=1.3.0&REQUEST=GetCapabilities&MAP={}".format(project_path)
    response = requests.get(url)

    tree = ElementTree.fromstring(response.content)
    root_layer = tree.find('./{http://www.opengis.net/wms}Capability/{http://www.opengis.net/wms}Layer')
    return len(root_layer.findall('{http://www.opengis.net/wms}Layer'))


class TestProjectReloaderPlugin():

    def test_file_project_reload(self):
        two_layers_file_project()
        assert _get_layers_count(project_path=FILE_PROJECT_PATH), 1

        two_layers_file_project()
        assert _get_layers_count(project_path=FILE_PROJECT_PATH), 2
