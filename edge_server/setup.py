import subprocess
from setuptools import setup
from setuptools.command.install import install as _install


class install(_install):
    def run(self):
        _install.run(self)
        subprocess.call(["bash", "post_install"])


setup(
    name="chronos",
    version="0.4.1",
    description="Boiling/cooling water system.",
    url="https://bitbucket.org/quarck/chronos/",
    author="Dmitry Misharov",
    author_email="quarckster@gmail.com",
    packages=[
        "chronos",
        "chronos.lib",
        "chronos.bin",
        "chronos.utils"
    ],
    install_requires=[
        "apscheduler",
        "sqlalchemy",
        "Flask",
        "pymodbus",
        "python-socketio",
        "socketIO_client",
        "uwsgi",
        "gevent-websocket"
    ],
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "chronosd = chronos.bin.chronosd:main",
            "chronos_debug = chronos.utils.chronos_hardware_debug:main"
        ]
    },
    data_files=[
        ("/etc", ["data_files/chronos_config.json"]),
        ("/etc/systemd/system/", ["data_files/uwsgi-socketio.service"]),
        ("/etc/init.d", ["data_files/chronos", "data_files/uwsgi"]),
        ("/var/www", ["data_files/chronos.wsgi"]),
        ("/etc/nginx/sites-enabled/", ["data_files/chronos.conf"]),
        ("/etc/uwsgi/apps-enabled/", ["data_files/chronos.ini", "data_files/socketio_server.ini"])
    ],
    cmdclass={"install": install},
    classifiers=["Private :: Do Not Upload"]
)
