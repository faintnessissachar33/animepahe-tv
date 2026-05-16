import flet as ft


class AppTheme:
    bg_primary = "#0D0D0D"
    bg_secondary = "#1A1A2E"
    bg_card = "#16213E"
    accent = "#E94560"
    accent_hover = "#FF6B81"
    text_primary = "#FFFFFF"
    text_secondary = "#A0A0B0"
    text_muted = "#6B6B7B"
    success = "#2ECC71"
    warning = "#F39C12"
    error = "#E74C3C"
    focus_border = "#E94560"
    focus_glow = "rgba(233, 69, 96, 0.3)"

    def heading(self, text: str, size: int = 24) -> ft.Text:
        return ft.Text(text, size=size, weight=ft.FontWeight.BOLD, color=self.text_primary)

    def body(self, text: str, size: int = 14) -> ft.Text:
        return ft.Text(text, size=size, color=self.text_secondary)

    def muted(self, text: str, size: int = 12) -> ft.Text:
        return ft.Text(text, size=size, color=self.text_muted)
