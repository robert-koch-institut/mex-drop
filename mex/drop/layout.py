from typing import cast

import reflex as rx

from mex.drop.locale_service import LocaleService, MExLocale
from mex.drop.models import NavItem, User
from mex.drop.state import State

locale_service = LocaleService.get()

# path data of the MEx wordmark, drawn on a 66x25 viewBox
_WORDMARK_PATH = (
    "M62.5 23.25L60.31 20.63L59.06 19.13L58.96 19.01L58.73 19.31C57.7942 20.4189 "
    "56.6989 21.3828 55.48 22.17C53.8977 23.2987 52.0717 24.0387 50.15 24.33C47.3585 "
    "24.7143 44.5205 24.1098 42.1278 22.6213C39.7352 21.1328 37.9388 18.854 37.05 "
    "16.18L36.95 15.84L36.62 15.77C35.509 15.5404 34.4696 15.0465 33.59 14.33C33.25 "
    "14.05 32.6 13.4 32.3 13.02C31.62 12.16 31.1 11.29 29.82 8.92C29.0909 7.44265 "
    "28.2414 6.02786 27.28 4.69C26.7952 4.03978 26.1802 3.49769 25.4743 "
    "3.09825C24.7684 2.69881 23.987 2.4508 23.18 2.37C22.78 2.31 21.51 2.32 21.07 "
    "2.38C20.29 2.5 19.67 2.68 19.08 2.98C17.48 3.79 16.53 5.32 16.15 7.65C16.09 8.01 "
    "16.09 8.16 16.07 13.7L16.04 21.93V24.47H14.24L14.23 16.36C14.23 7.43 14.23 8.15 "
    "14.05 7.23C13.8233 5.87969 13.1676 4.63836 12.18 3.69C11.38 2.99 10.42 2.59 9.14 "
    "2.39C8.68 2.31 7.31 2.31 6.84 2.39C5.44 2.59 4.38 3.09 3.57 3.93C2.54604 5.09831 "
    "1.94696 6.57838 1.87 8.13C1.84 8.34 1.83 11.03 1.83 16.46V24.47H0L0.01 16.29C0.02 "
    "8.77 0.02 8.07 0.07 7.74C0.226097 6.04291 0.864562 4.42593 1.91 3.08C2.52794 "
    "2.34415 3.28882 1.74139 4.14655 1.30822C5.00428 0.875062 5.94101 0.620514 6.9 "
    "0.559999C7.63225 0.503505 8.36775 0.503505 9.1 0.559999C10.3851 0.637027 11.6251 "
    "1.06202 12.6872 1.7895C13.7494 2.51699 14.5938 3.51958 15.13 4.69L15.3 "
    "4.39C16.0102 2.96239 17.1995 1.82974 18.66 1.19C19.4482 0.850411 20.2853 0.637778 "
    "21.14 0.559999C21.61 0.509999 22.71 0.499999 23.17 0.559999C24.3366 0.651786 "
    "25.4664 1.01067 26.4722 1.6089C27.4779 2.20714 28.3325 3.02868 28.97 4.01C30.1346 "
    "5.74068 31.1867 7.54439 32.12 9.41C32.59 10.33 32.82 10.71 33.14 11.17C33.7192 "
    "12.0133 34.456 12.7366 35.31 13.3C35.73 13.56 36.49 13.9 36.53 13.85C36.55 13.84 "
    "36.53 13.67 36.52 13.47C36.3592 11.4439 36.7157 9.41024 37.556 7.55964C38.3963 "
    "5.70904 39.6928 4.10219 41.324 2.88978C42.9552 1.67737 44.8676 0.899131 46.8819 "
    "0.628058C48.8962 0.356984 50.9463 0.601957 52.84 1.34C52.86 1.34 52.17 2.92 52.12 "
    "2.98L51.72 2.86C50.7431 2.51582 49.7157 2.3367 48.68 2.33C47.1981 2.29423 45.7264 "
    "2.58348 44.3682 3.17741C43.0101 3.77134 41.7985 4.65554 40.8187 5.76785C39.8389 "
    "6.88015 39.1146 8.19357 38.6967 9.61578C38.2789 11.038 38.1776 12.5345 38.4 "
    "14C38.43 14.08 38.44 14.08 39 14C39.51 13.93 39.83 13.85 44.07 12.69L48.19 "
    "11.57C48.21 11.6 48.66 13.25 48.64 13.28C48.64 13.3 48.35 13.39 48.01 13.48C46.46 "
    "13.9 41.78 15.18 40.84 15.45C40.2 15.6509 39.5444 15.798 38.88 15.89L39.01 "
    "16.22C39.5548 17.5642 40.38 18.7768 41.4305 19.7769C42.4811 20.7769 43.7328 "
    "21.5414 45.1023 22.0194C46.4717 22.4973 47.9273 22.6777 49.372 22.5484C50.8166 "
    "22.4192 52.2171 21.9834 53.48 21.27C54.78 20.55 55.93 19.6 57.19 18.23C57.7 17.68 "
    "57.75 17.61 57.7 17.53C57.67 17.47 55.4 14.75 53.9 12.99L53.47 12.46H55.92L57.42 "
    "14.24C58.23 15.23 58.92 16.04 58.94 16.05C58.96 16.07 59.48 15.47 60.49 14.27L62 "
    "12.47H64.45L64.31 12.63C63.42 13.67 60.19 17.55 60.19 17.57C60.19 17.59 64.39 "
    "22.61 65.92 24.42L66 24.5H63.54L62.5 23.25Z"
)

# The nav bar is a solid accent surface, so its children cannot rely on the
# theme's default foreground colors. These vars are declared on the nav bar and
# inherited by everything inside it.
NAV_BAR_PALETTE = {
    "--nav-bar-bg": "var(--accent-11)",
    "--nav-bar-fg": "var(--accent-contrast)",
    "--nav-bar-button-bg": "var(--accent-12)",
    "--nav-bar-button-bg-hover": (
        "color-mix(in srgb, var(--accent-12) 70%, var(--accent-11))"
    ),
}


def logout_button() -> rx.Component:
    """Return a logout button with a trailing arrow icon."""
    return rx.button(
        State.label_nav_bar_logout_button,
        rx.icon("arrow-right", size=18),
        on_click=State.logout,
        variant="solid",
        style=rx.Style(
            margin="0",
            # fixed width, so translating the label does not shift the nav bar
            width="calc(140px * var(--scaling))",
            backgroundColor="var(--nav-bar-button-bg)",
            color="var(--nav-bar-fg)",
        ),
        _hover={"backgroundColor": "var(--nav-bar-button-bg-hover)"},
        custom_attrs={"data-testid": "logout-button"},
    )


def user_menu() -> rx.Component:
    """Return a flat user menu with the current X-System and a logout button."""
    return rx.hstack(
        rx.text(
            cast("User", State.user).x_system,
            style=rx.Style(userSelect="none", whiteSpace="nowrap"),
        ),
        logout_button(),
        spacing="3",
        style=rx.Style(alignItems="center"),
        custom_attrs={"data-testid": "user-menu"},
    )


def language_switcher_segment(locale: MExLocale) -> rx.Component:
    """Return one segment of the language switcher for the given locale."""
    is_current = State.current_locale == locale.id
    return rx.button(
        locale.code,
        on_click=State.change_locale(locale.id),  # type: ignore[operator]
        title=locale.label,
        variant="ghost",
        radius="none",
        style=rx.Style(
            margin="0",
            paddingLeft="var(--space-3)",
            paddingRight="var(--space-3)",
            fontWeight="var(--font-weight-bold)",
            backgroundColor=rx.cond(
                is_current, "var(--nav-bar-button-bg)", "transparent"
            ),
            color="var(--nav-bar-fg)",
        ),
        _hover={"backgroundColor": "var(--nav-bar-button-bg-hover)"},
        custom_attrs={
            "data-testid": f"language-switcher-{locale.id}",
            "aria-pressed": is_current,
        },
    )


def language_switcher() -> rx.Component:
    """Return a language switcher with one button segment per available locale."""
    return rx.hstack(
        rx.foreach(
            locale_service.get_available_locales(),
            language_switcher_segment,
        ),
        spacing="0",
        style=rx.Style(
            alignItems="stretch",
            border="1px solid var(--nav-bar-button-bg)",
            borderRadius="var(--radius-3)",
            overflow="hidden",
        ),
        custom_attrs={"data-testid": "language-switcher"},
    )


def nav_link(item: NavItem) -> rx.Component:
    """Return a link component for the given navigation item."""
    return rx.link(
        rx.text(item.title, size="4", weight="medium"),
        href=item.raw_path,
        underline=rx.cond(item.active, "always", "none"),
        class_name=rx.cond(item.active, "nav-item nav-item-active", "nav-item"),
        # radix links are accent colored, which is unreadable on the accent fill
        style=rx.Style(
            color="var(--nav-bar-fg)",
            # `underline` only sets the line, leaving radix's near transparent
            # accent-a5 decoration color, which vanishes on the accent fill
            textDecorationColor="var(--nav-bar-fg)",
            # 1px matches the nav bar divider, so the two lines agree
            textDecorationThickness="1px",
            textUnderlineOffset="6px",
        ),
        custom_attrs={"data-testid": f"nav-item-{item.route_ids[0]}"},
    )


def mex_wordmark() -> rx.Component:
    """Return the MEx wordmark as an inline svg, tinted with the text color.

    The path is filled with `currentColor`, so the same component works on the
    light login card and on the solid accent nav bar.
    """
    return rx.el.svg(
        rx.el.path(d=_WORDMARK_PATH, fill="currentColor"),
        view_box="0 0 66 25",
        role="img",
        aria_label="MEx",
        style=rx.Style(
            {
                # the intrinsic size of the wordmark is 66x25
                "height": "calc(25px * var(--scaling))",
                "width": "calc(66px * var(--scaling))",
                "flexShrink": "0",
            }
        ),
    )


def app_logo() -> rx.Component:
    """Return the app logo with the MEx wordmark and the app name."""
    return rx.hstack(
        mex_wordmark(),
        rx.heading(
            "Drop",
            weight="medium",
            style=rx.Style(userSelect="none"),
        ),
        spacing="3",
        align="center",
        custom_attrs={"data-testid": "app-logo"},
    )


def nav_bar() -> rx.Component:
    """Return a navigation bar component."""
    return rx.vstack(
        rx.box(
            style=rx.Style(
                height="var(--space-6)",
                width="100%",
                backdropFilter="var(--backdrop-filter-panel)",
            ),
        ),
        rx.card(
            rx.hstack(
                app_logo(),
                rx.hstack(
                    rx.foreach(State.nav_items_translated, nav_link),
                    justify="start",
                    spacing="4",
                ),
                rx.spacer(),
                rx.hstack(
                    language_switcher(),
                    user_menu(),
                    align="center",
                    spacing="7",
                ),
                justify="between",
                align_items="center",
                # the gaps next to the spacer collapse into it, so this only
                # separates the logo from the nav items, matching the spacing
                # between the language switcher and the user menu
                spacing="7",
            ),
            size="2",
            custom_attrs={"data-testid": "nav-bar"},
            style=rx.Style(
                {
                    **NAV_BAR_PALETTE,
                    # radix paints the card surface on a ::before pseudo element
                    "--card-background-color": "var(--nav-bar-bg)",
                    "color": "var(--nav-bar-fg)",
                    "width": "100%",
                    "marginTop": "calc(-1 * var(--base-card-border-width))",
                }
            ),
        ),
        spacing="0",
        style=rx.Style(
            maxWidth="var(--app-max-width)",
            minWidth="var(--app-min-width)",
            position="fixed",
            top="0",
            width="100%",
            zIndex="1000",
        ),
    )


def page(*children: rx.Component) -> rx.Component:
    """Return a page fragment with navigation bar and given children."""
    page_content = [
        nav_bar(),
        rx.hstack(
            *children,
            style=rx.Style(
                maxWidth="var(--app-max-width)",
                minWidth="var(--app-min-width)",
                padding="calc(var(--space-6) * 4) var(--space-6) var(--space-6)",
                width="100%",
            ),
            custom_attrs={"data-testid": "page-body"},
        ),
    ]

    return rx.cond(
        State.user,
        rx.center(
            *page_content,
            style=rx.Style(
                {
                    "--app-max-width": "calc(1480px * var(--scaling))",
                    "--app-min-width": "calc(800px * var(--scaling))",
                    "width": "100%",
                }
            ),
        ),
        rx.center(
            rx.spinner(size="3"),
            style=rx.Style(marginTop="40vh"),
        ),
    )
