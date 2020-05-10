from qgis.core import QgsProject, QgsVectorLayer
import requests
from xml.etree import ElementTree

DATA_PATH = "/data"
LAYER1_PATH = "/data/faces.gml"
LAYER2_PATH = "/data/state.gml"
FILE_PROJECT_PATH = "/data/project.qgs"
DB_PROJECT_PATH = "postgresql://qgis:qgis@db:5432?sslmode=disable&dbname=qgis&schema=public&project=project"
QGIS_SERVER_URL = "http://qgisserver:8000"


def one_layer_project():
    project = QgsProject()

    layer = QgsVectorLayer(LAYER1_PATH, "faces", "ogr")
    assert layer.isValid()
    project.addMapLayer(layer)

    return project


def two_layers_project():
    project = QgsProject()

    layer = QgsVectorLayer(LAYER1_PATH, "faces", "ogr")
    assert layer.isValid()
    project.addMapLayer(layer)

    layer = QgsVectorLayer(LAYER2_PATH, "state", "ogr")
    assert layer.isValid()
    project.addMapLayer(layer)

    return project
    project.write(FILE_PROJECT_PATH)


def get_layers_count(project_path):
    response = requests.get(
        QGIS_SERVER_URL,
        {
            "MAP": project_path,
            "SERVICE": "WMS",
            "VERSION": "1.3.0",
            "REQUEST": "GetCapabilities",
        }
    )
    tree = ElementTree.fromstring(response.content)
    root_layer = tree.find('./{http://www.opengis.net/wms}Capability/{http://www.opengis.net/wms}Layer')
    return len(root_layer.findall('{http://www.opengis.net/wms}Layer'))


def get_map(project_path, layers):
    return requests.get(
        QGIS_SERVER_URL,
        {
            "SERVICE": "WMS",
            "VERSION": "1.3.0",
            "REQUEST": "GetMap",
            "MAP": project_path,
            "LAYERS": layers,
            "STYLES": "default",
            "SRS": "EPSG:4326",
            "BBOX": "11.36429396031117,47.23595435939557,11.43933745091724,47.29938397645547",
            "WIDTH": "256",
            "HEIGHT": "256",
            "FORMAT": "image/png",
        }
    )


class TestProjectReloaderPlugin():

    def test_file_project_reload(self):
        assert one_layer_project().write(FILE_PROJECT_PATH)
        assert get_layers_count(FILE_PROJECT_PATH) == 1
        assert get_map(FILE_PROJECT_PATH, "faces").status_code == 200
        assert get_map(FILE_PROJECT_PATH, "faces,state").status_code == 400
        assert two_layers_project().write(FILE_PROJECT_PATH)
        assert get_map(FILE_PROJECT_PATH, "faces,state").status_code == 200

    def test_db_project_reload(self):
        assert one_layer_project().write(DB_PROJECT_PATH)
        assert get_layers_count(FILE_PROJECT_PATH) == 1
        assert get_map(DB_PROJECT_PATH, "faces").status_code == 200
        assert get_map(DB_PROJECT_PATH, "faces,state").status_code == 400
        assert two_layers_project().write(DB_PROJECT_PATH)
        assert get_map(DB_PROJECT_PATH, "faces,state").status_code == 200
