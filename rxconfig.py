import reflex as rx
from reflex.plugins.sitemap import SitemapPlugin

config = rx.Config(
    app_name="mex",
    disable_plugins=[SitemapPlugin],
    frontend_port=8020,
    backend_port=8021,
    telemetry_enabled=False,
)
