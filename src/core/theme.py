import flet as ft


class AppColors:
    PRIMARY = "#E94560"
    SECONDARY = "#7C4DFF"
    SUCCESS = "#2ECC71"
    WARNING = "#F39C12"
    ERROR = "#F44336"

    DARK_BG = "#0D0D0D"
    DARK_SURFACE = "#1A1A2E"
    DARK_SURFACE_VARIANT = "#16213E"
    DARK_TEXT = "#FFFFFF"
    DARK_TEXT_DIM = "#A0A0B0"
    DARK_TEXT_MUTED = "#6B6B7B"

    SPLASH_BG = "#0D0D0D"

    WHITE = ft.Colors.WHITE
    BLACK = ft.Colors.BLACK
    TRANSPARENT = ft.Colors.TRANSPARENT
    GREY_DIM = "#888888"


class AppTheme:
    @staticmethod
    def get_dark_theme() -> ft.Theme:
        return ft.Theme(
            color_scheme=ft.ColorScheme(
                primary=AppColors.PRIMARY,
                secondary=AppColors.SECONDARY,
                surface=AppColors.DARK_BG,
                on_surface=AppColors.DARK_TEXT,
                on_surface_variant=AppColors.DARK_TEXT_DIM,
                error=AppColors.ERROR,
                on_primary=ft.Colors.WHITE,
                on_secondary=ft.Colors.BLACK,
                outline=AppColors.DARK_TEXT_MUTED,
            ),
            visual_density=ft.VisualDensity.COMFORTABLE,
        )
