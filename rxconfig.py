import reflex as rx

config = rx.Config(
    app_name="mex",
    disable_plugins=["reflex.plugins.sitemap.SitemapPlugin"],
    frontend_port=8020,
    backend_port=8021,
    telemetry_enabled=False,
)
