from qgis.core import QgsMessageLog


def serverClassFactory(serverIface):  # noqa
    QgsMessageLog.logMessage("Starting DB project reloader...", level=4)
    try:
        from ProjectReloader.project_reloader_plugin import ProjectReloaderPlugin

        return ProjectReloaderPlugin(serverIface)
    except Exception as e:
        QgsMessageLog.logMessage(str(e))
