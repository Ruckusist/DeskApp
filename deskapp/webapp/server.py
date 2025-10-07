# deskapp/webapp/server.py
# last updated: 10-5-25
# credit: Claude Sonnet 4.5

"""Simple web server for deskapp applications"""

import os
from flask import Flask, render_template, send_from_directory


class WebApp:
    """Minimal web application server"""

    def __init__(
        self,
        Name="DeskApp",
        Host="0.0.0.0",
        Port=8080,
        TemplateFolder=None,
        StaticFolder=None
    ):
        self.Name = Name
        self.Host = Host
        self.Port = Port

        if TemplateFolder is None:
            TemplateFolder = "templates"
        if StaticFolder is None:
            StaticFolder = "static"

        self.App = Flask(
            Name,
            template_folder=TemplateFolder,
            static_folder=StaticFolder
        )

        self.SetupRoutes()

    def SetupRoutes(self):
        """Setup default routes"""

        @self.App.route("/")
        def Index():
            return render_template("index.html")

        @self.App.route("/health")
        def Health():
            return {"status": "ok"}

    def Route(self, rule, **options):
        """Decorator to add routes"""
        return self.App.route(rule, **options)

    def Run(self, Debug=False):
        """Start the web server"""
        self.App.run(
            host=self.Host,
            port=self.Port,
            debug=Debug
        )
