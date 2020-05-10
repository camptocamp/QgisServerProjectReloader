import sys
import traceback

from qgis.core import Qgis, QgsMessageLog
from qgis.server import QgsConfigCache, QgsServerFilter, QgsServerInterface

from ProjectReloader import __name__ as NAME


class ProjectReloaderPlugin(QgsServerFilter):
    """
    This plugin checks if the project from the Map Request value is loaded.
    it then check periodically if current requested project needs to be reloaded.
    """

    def __init__(self, server_iface: QgsServerInterface) -> None:
        super().__init__(server_iface)
        self._reloading = False
        self._last_reload_times = {}
        QgsMessageLog.logMessage(
            f"Registering ProjectReloaderPlugin", NAME, level=Qgis.Info
        )
        self.serverInterface().registerFilter(self)

    def requestReady(self):
        try:
            self.updateProject()
        except Exception as e:
            QgsMessageLog.logMessage(
                "".join(traceback.format_exception(*sys.exc_info())),
                NAME,
                level=Qgis.Critical,
            )

    def updateProject(self):
        if self._reloading:
            QgsMessageLog.logMessage(
                f"Project is already reloading, skip.", NAME, level=Qgis.Info
            )
            return

        config_file = self.serverInterface().configFilePath()
        config_cache = QgsConfigCache.instance()
        project = config_cache.project(config_file)

        source_project_time = project.lastModified().toPyDateTime()
        source_project_path = config_file
        if not source_project_path in self._last_reload_times:
            self._last_reload_times[source_project_path] = source_project_time
        else:
            QgsMessageLog.logMessage(
                f"source_project_time: {source_project_time}", NAME, level=Qgis.Info
            )
            QgsMessageLog.logMessage(
                f"last_reload_time: {self._last_reload_times[source_project_path]}",
                NAME,
                level=Qgis.Info,
            )

            if source_project_time > self._last_reload_times[source_project_path]:
                self._reloading = True
                QgsMessageLog.logMessage(f"Reloading project", NAME, level=Qgis.Warning)
                project.read()
                self._reloading = False
                self._last_reload_times[source_project_path] = source_project_time
