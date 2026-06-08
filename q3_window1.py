from __future__ import annotations

import json
import urllib.error
import urllib.request

import flet as ft


API_BASE_URL = "http://127.0.0.1:8000"

COLORS = {
    "appbar": "#FCB288",
    "page_bg": "#F9E2E1",
    "table_header": "#353445",
    "post_btn": "#FCB288",
    "text_box": "#F8DED3",
    "even_row": "#FFFFFF",
    "odd_row": "#FFF8EE",
    "snackbar": "#242436",
    "white": "#FFFFFF",
    "delete": "#B92626",
    "nav_text": "#353445",
    "muted_text": "#6B5E5A",
    "border": "#E5C7BD",
}


def pick_value(record: dict, *keys: str, default: str = "") -> str:
    for key in keys:
        value = record.get(key)
        if value not in (None, ""):
            return str(value)
    return default


def normalize_donor(record: dict, index: int) -> dict:
    first_name = pick_value(record, "first_name", "firstname")
    last_name = pick_value(record, "last_name", "lastname", "surname")
    full_name = pick_value(record, "full_name", "fullname", "name")
    if not full_name:
        full_name = f"{first_name} {last_name}".strip() or f"Donor {index + 1}"

    donor_id = pick_value(record, "donor_id", "DonorID", "id", default=str(index + 1))
    blood_type = pick_value(record, "blood_type", "BloodType", "bloodGroup", default="-")
    phone = pick_value(record, "phone", "Phone", "phone_number", default="-")

    available = record.get("available")
    status = pick_value(record, "status", "availability")
    if not status:
        status = "Available" if available in (None, True, "true", "True", 1, "1") else "Unavailable"

    return {
        "donor_id": donor_id,
        "full_name": full_name,
        "blood_type": blood_type,
        "phone": phone,
        "status": status,
    }


def fetch_donors() -> tuple[list[dict], str | None]:
    request = urllib.request.Request(
        f"{API_BASE_URL}/donors",
        headers={"Accept": "application/json"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        return [], f"Backend xetasi: HTTP {exc.code}"
    except urllib.error.URLError:
        return [], "FastAPI backend ile baglanti qurulmadi."
    except json.JSONDecodeError:
        return [], "Backend cavabi JSON formatinda deyil."

    donors_payload = payload
    if isinstance(payload, dict):
        donors_payload = []
        for key in ("donors", "items", "data", "results"):
            if isinstance(payload.get(key), list):
                donors_payload = payload[key]
                break

    if not isinstance(donors_payload, list):
        return [], "GET /donors cavabi gozlenilen formatda deyil."

    donors = [
        normalize_donor(item, index)
        for index, item in enumerate(donors_payload)
        if isinstance(item, dict)
    ]
    return donors, None


def row_cell(value: str, bgcolor: str) -> ft.DataCell:
    return ft.DataCell(
        ft.Container(
            content=ft.Text(value, color=COLORS["nav_text"], size=13),
            bgcolor=bgcolor,
            padding=ft.padding.symmetric(horizontal=10, vertical=8),
            border_radius=8,
        )
    )


def build_rows(donors: list[dict]) -> list[ft.DataRow]:
    rows: list[ft.DataRow] = []
    for index, donor in enumerate(donors):
        row_bg = COLORS["even_row"] if index % 2 == 0 else COLORS["odd_row"]
        rows.append(
            ft.DataRow(
                cells=[
                    row_cell(donor["donor_id"], row_bg),
                    row_cell(donor["full_name"], row_bg),
                    row_cell(donor["blood_type"], row_bg),
                    row_cell(donor["phone"], row_bg),
                ]
            )
        )
    return rows


def build_bottom_sheet_preview(donors: list[dict]) -> ft.Container:
    donor = donors[0] if donors else None
    donor_summary = (
        f'{donor["full_name"]}, Blood Type: {donor["blood_type"]}, {donor["status"]}'
        if donor
        else "No donor data available."
    )

    return ft.Container(
        bgcolor=COLORS["text_box"],
        border=ft.border.all(1, COLORS["border"]),
        border_radius=18,
        padding=18,
        content=ft.Column(
            spacing=10,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        ft.Container(
                            width=54,
                            height=5,
                            bgcolor=ft.Colors.WHITE54,
                            border_radius=20,
                        )
                    ],
                ),
                ft.Text(
                    "Bottom Sheet",
                    size=16,
                    weight=ft.FontWeight.BOLD,
                    color=COLORS["table_header"],
                ),
                ft.Text(
                    donor_summary,
                    size=15,
                    weight=ft.FontWeight.W_600,
                    color=COLORS["nav_text"],
                ),
                ft.Text(
                    "Tap drag handle to expand full details.",
                    size=13,
                    color=COLORS["muted_text"],
                ),
            ],
        ),
    )


def main(page: ft.Page) -> None:
    page.title = "BloodBank"
    page.bgcolor = COLORS["page_bg"]
    page.window.width = 980
    page.window.height = 760
    page.window.min_width = 900
    page.window.min_height = 700
    page.padding = 0
    page.theme_mode = ft.ThemeMode.LIGHT
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    donors, error_message = fetch_donors()

    if error_message:
        page.snack_bar = ft.SnackBar(
            content=ft.Text(error_message, color=COLORS["white"]),
            bgcolor=COLORS["snackbar"],
            open=True,
        )

    data_table = ft.DataTable(
        bgcolor=COLORS["white"],
        heading_row_color=COLORS["table_header"],
        heading_row_height=46,
        data_row_min_height=52,
        data_row_max_height=52,
        divider_thickness=0,
        horizontal_lines=ft.BorderSide(0, ft.Colors.TRANSPARENT),
        columns=[
            ft.DataColumn(ft.Text("DonorID", color=COLORS["white"], weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("FullName", color=COLORS["white"], weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("BloodType", color=COLORS["white"], weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Phone", color=COLORS["white"], weight=ft.FontWeight.BOLD)),
        ],
        rows=build_rows(donors),
    )

    content = ft.Container(
        expand=True,
        padding=ft.padding.symmetric(horizontal=26, vertical=20),
        content=ft.Column(
            expand=True,
            spacing=18,
            controls=[
                ft.Container(
                    bgcolor=COLORS["appbar"],
                    border_radius=ft.border_radius.only(bottom_left=22, bottom_right=22),
                    padding=ft.padding.symmetric(horizontal=20, vertical=18),
                    content=ft.Text(
                        "BloodBank",
                        size=24,
                        weight=ft.FontWeight.BOLD,
                        color=COLORS["white"],
                    ),
                ),
                ft.Container(
                    bgcolor=COLORS["white"],
                    border_radius=18,
                    border=ft.border.all(1, COLORS["border"]),
                    padding=16,
                    content=ft.Column(
                        spacing=12,
                        controls=[
                            ft.Text(
                                "Donor List",
                                size=18,
                                weight=ft.FontWeight.BOLD,
                                color=COLORS["table_header"],
                            ),
                            ft.Container(
                                content=ft.Column(
                                    scroll=ft.ScrollMode.AUTO,
                                    controls=[data_table],
                                ),
                            ),
                        ],
                    ),
                ),
                ft.Text(
                    f"Total Donors: {len(donors)}",
                    size=16,
                    weight=ft.FontWeight.BOLD,
                    color=COLORS["table_header"],
                ),
                build_bottom_sheet_preview(donors),
                ft.Container(expand=True),
                ft.Container(
                    bgcolor=COLORS["appbar"],
                    border_radius=18,
                    padding=ft.padding.symmetric(horizontal=26, vertical=16),
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text("Donors", color=COLORS["white"], weight=ft.FontWeight.BOLD),
                            ft.Text("Inventory", color=COLORS["white"], weight=ft.FontWeight.BOLD),
                            ft.Text("Requests", color=COLORS["white"], weight=ft.FontWeight.BOLD),
                        ],
                    ),
                ),
            ],
        ),
    )

    page.add(content)


def run_app() -> None:
    try:
        ft.run(main, view=ft.AppView.FLET_APP)
    except urllib.error.HTTPError as exc:
        if exc.code != 504:
            raise
        print("Desktop runtime yuklenmedi, app browser rejiminde acilir...")
        ft.run(main, view=ft.AppView.WEB_BROWSER, port=8550)


if __name__ == "__main__":
    run_app()
