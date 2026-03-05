import reflex as rx

config = rx.Config(
    app_name="mex",
    disable_plugins=["reflex.plugins.sitemap.SitemapPlugin"],
    telemetry_enabled=False,
)
