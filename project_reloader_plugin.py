import sys
import traceback
from datetime import timedelta

from qgis.core import QgsMessageLog, QgsProject, Qgis
from qgis.server import QgsServerInterface, QgsServerFilter

from ProjectReloader import __name__ as NAME


class ProjectReloaderPlugin(QgsServerFilter):
    """
    This plugin checks if the project is loaded via postgresql.
    it then check periodically if the project needs to be reloaded.
    """

    def __init__(self, server_iface: QgsServerInterface) -> None:
        super().__init__(server_iface)
        self._reloading = False
        self._last_reload_time = None
        QgsMessageLog.logMessage(f"Registering ProjectReloaderPlugin", NAME, level=Qgis.Info)
        self.serverInterface().registerFilter(self)

    def requestReady(self):
        try:
            self.updateProject()
        except Exception as e:
            QgsMessageLog.logMessage(
                ''.join(traceback.format_exception(*sys.exc_info())),
                NAME,
                level=Qgis.Critical
            )

    def updateProject(self):
        if self._reloading:
            QgsMessageLog.logMessage(f"Project is already reloading, skip.", NAME, level=Qgis.Info)
            return

        if not QgsProject.instance().fileName():
            QgsMessageLog.logMessage(f"Project filename is empty, nothing to do.", NAME, level=Qgis.Info)
            return

        source_project_time = QgsProject.instance().lastModified().toPyDateTime()
        if self._last_reload_time is None:
            self._last_reload_time = source_project_time
        else:
            QgsMessageLog.logMessage(f"source_project_time: {source_project_time}",  NAME, level=Qgis.Info)
            QgsMessageLog.logMessage(f"last_reload_time: {self._last_reload_time}", NAME, level=Qgis.Info)

            if source_project_time > self._last_reload_time:
                self._reloading = True
                QgsMessageLog.logMessage(f"Reloading project", NAME, level=Qgis.Warning)
                QgsProject.instance().read()
                self._reloading = False
                self._last_reload_time = source_project_time
