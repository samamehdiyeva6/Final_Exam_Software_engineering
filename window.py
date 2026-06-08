import flet as ft
import sqlite3
import os
from pydantic import BaseModel, Field, ValidationError
from typing import Optional

class DonorModel(BaseModel):
    DonorID: Optional[int] = None
    FullName: str = Field(min_length=2, max_length=100)
    BloodType: str = Field(pattern=r"^(A|B|AB|O)[+-]$")
    Phone: str = Field(min_length=6, max_length=20)

DB_NAME = os.path.join(os.path.dirname(__file__), "bloodbank.db")

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Donors (
            DonorID INTEGER PRIMARY KEY AUTOINCREMENT,
            FullName TEXT NOT NULL,
            BloodType TEXT NOT NULL,
            Phone TEXT
        )
    ''')
    cursor.execute('SELECT COUNT(*) FROM Donors')
    if cursor.fetchone()[0] == 0:
        sample_donors = [
            ("Elvin A.", "A+", "555-0101"),
            ("Gunel M.", "O-", "555-0102"),
            ("Tarlan R.", "B+", "555-0103")
        ]
        cursor.executemany('INSERT INTO Donors (FullName, BloodType, Phone) VALUES (?, ?, ?)', sample_donors)
    conn.commit()
    conn.close()

def get_all_donors():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Donors')
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def add_donor(donor_id, fullname, bloodtype, phone):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        if donor_id and str(donor_id).strip() != "":
            cursor.execute('INSERT INTO Donors (DonorID, FullName, BloodType, Phone) VALUES (?, ?, ?, ?)', (donor_id, fullname, bloodtype, phone))
        else:
            cursor.execute('INSERT INTO Donors (FullName, BloodType, Phone) VALUES (?, ?, ?)', (fullname, bloodtype, phone))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def delete_donor(donor_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM Donors WHERE DonorID = ?', (donor_id,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted

def main(page: ft.Page):
    page.title = "BloodBank App"
    page.bgcolor = "#F9E2E1"
    page.theme_mode = ft.ThemeMode.LIGHT
    
    init_db()

    def show_snack_bar(message):
        page.overlay.clear()
        snack = ft.SnackBar(content=ft.Text(message), bgcolor="#242436", open=True)
        page.overlay.append(snack)
        page.update()

    def show_window_1():
        page.clean()
        
        # Build App Bar
        page.appbar = ft.AppBar(
            title=ft.Text("BloodBank", color=ft.Colors.WHITE),
            bgcolor="#C62828",
            center_title=False,
            actions=[
                ft.IconButton(ft.Icons.ADD, icon_color=ft.Colors.WHITE, tooltip="Add Donor", on_click=lambda _: show_window_2())
            ]
        )
        
        # Build Navigation Bar
        page.navigation_bar = ft.NavigationBar(
            destinations=[
                ft.NavigationBarDestination(icon=ft.Icons.PEOPLE, label="Donors"),
                ft.NavigationBarDestination(icon=ft.Icons.INVENTORY_2, label="Inventory"),
                ft.NavigationBarDestination(icon=ft.Icons.REQUEST_PAGE, label="Requests"),
            ],
        )

        donors_data = get_all_donors()
        rows = []
        for index, donor in enumerate(donors_data):
            row_color = "#FFFFFF" if index % 2 == 0 else "#FFE8EE"
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(donor.get("DonorID", "")), color=ft.Colors.BLACK)),
                        ft.DataCell(ft.Text(str(donor.get("FullName", "")), color=ft.Colors.BLACK)),
                        ft.DataCell(ft.Text(str(donor.get("BloodType", "")), color=ft.Colors.BLACK)),
                        ft.DataCell(ft.Text(str(donor.get("Phone", "")), color=ft.Colors.BLACK)),
                    ],
                    color=row_color
                )
            )

        data_table = ft.DataTable(
            width=float("inf"),
            heading_row_color="#353445",
            heading_text_style=ft.TextStyle(color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
            columns=[
                ft.DataColumn(ft.Text("DonorID")),
                ft.DataColumn(ft.Text("FullName")),
                ft.DataColumn(ft.Text("BloodType")),
                ft.DataColumn(ft.Text("Phone")),
            ],
            rows=rows,
        )

        table_container = ft.Column([data_table], scroll=ft.ScrollMode.AUTO, expand=True)
        total_donors_text = ft.Text(f"Total Donors: {len(donors_data)}", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK87)

        bottom_sheet_info = ft.Container(
            content=ft.Column([
                ft.Text("Elvin A. , Blood Type: A+ , Available", weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK87),
                ft.Container(height=5),
                ft.Row(
                    [
                        ft.Icon(ft.Icons.DRAG_HANDLE, size=16, color=ft.Colors.BLACK54),
                        ft.Text("Tap drag handle to expand full details.", color=ft.Colors.BLACK54, size=12)
                    ],
                    alignment=ft.MainAxisAlignment.CENTER
                )
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=15,
            bgcolor="#F8DED3",
            border_radius=10,
            border=ft.Border.all(1, ft.Colors.BLACK26),
            width=float("inf"),
            alignment=ft.Alignment(0, 0)
        )

        page.add(
            table_container,
            total_donors_text,
            bottom_sheet_info
        )
        page.update()

    def show_window_2():
        page.clean()
        
        # Build App Bar
        page.appbar = ft.AppBar(
            leading=ft.IconButton(ft.Icons.ARROW_BACK, icon_color=ft.Colors.WHITE, on_click=lambda _: show_window_1()),
            leading_width=40,
            title=ft.Text("Add Donor", color=ft.Colors.WHITE),
            bgcolor="#C62828",
            center_title=False,
        )
        
        # Remove navigation bar on window 2
        page.navigation_bar = None

        donors_data = get_all_donors()
        w2_rows = []
        for index, donor in enumerate(donors_data):
            row_color = "#FFFFFF" if index % 2 == 0 else "#FFE8EE"
            w2_rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(donor.get("DonorID", "")), color=ft.Colors.BLACK)),
                        ft.DataCell(ft.Text(str(donor.get("FullName", "")), color=ft.Colors.BLACK)),
                        ft.DataCell(ft.Text(str(donor.get("BloodType", "")), color=ft.Colors.BLACK)),
                        ft.DataCell(ft.Text(str(donor.get("Phone", "")), color=ft.Colors.BLACK)),
                    ],
                    color=row_color
                )
            )

        data_table2 = ft.DataTable(
            width=float("inf"),
            heading_row_color="#353445",
            heading_text_style=ft.TextStyle(color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
            columns=[
                ft.DataColumn(ft.Text("DonorID")),
                ft.DataColumn(ft.Text("FullName")),
                ft.DataColumn(ft.Text("BloodType")),
                ft.DataColumn(ft.Text("Phone")),
            ],
            rows=w2_rows,
        )

        table_container2 = ft.Column([data_table2], scroll=ft.ScrollMode.AUTO, expand=True)

        def refresh_table2():
            donors_data = get_all_donors()
            w2_rows = []
            for index, donor in enumerate(donors_data):
                row_color = "#FFFFFF" if index % 2 == 0 else "#FFE8EE"
                w2_rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(str(donor.get("DonorID", "")), color=ft.Colors.BLACK)),
                            ft.DataCell(ft.Text(str(donor.get("FullName", "")), color=ft.Colors.BLACK)),
                            ft.DataCell(ft.Text(str(donor.get("BloodType", "")), color=ft.Colors.BLACK)),
                            ft.DataCell(ft.Text(str(donor.get("Phone", "")), color=ft.Colors.BLACK)),
                        ],
                        color=row_color
                    )
                )
            data_table2.rows = w2_rows
            page.update()

        donor_id_input = ft.TextField(label="DonorID (Optional)", width=150, bgcolor="#F8DED3")
        fullname_input = ft.TextField(label="FullName", width=150, bgcolor="#F8DED3")
        bloodtype_input = ft.TextField(label="BloodType", width=150, bgcolor="#F8DED3")
        phone_input = ft.TextField(label="Phone", width=150, bgcolor="#F8DED3")

        inputs_row = ft.Row([donor_id_input, fullname_input, bloodtype_input, phone_input], wrap=True)

        def on_add_click(e):
            donor_id_raw = donor_id_input.value
            fullname_raw = fullname_input.value
            bloodtype_raw = bloodtype_input.value
            phone_raw = phone_input.value
            
            donor_id_val = None
            if donor_id_raw and donor_id_raw.strip() != "":
                try:
                    donor_id_val = int(donor_id_raw)
                except ValueError:
                    show_snack_bar("DonorID must be an integer!")
                    return

            try:
                # Validate using Pydantic
                valid_donor = DonorModel(
                    DonorID=donor_id_val,
                    FullName=fullname_raw,
                    BloodType=bloodtype_raw,
                    Phone=phone_raw
                )
            except ValidationError as ve:
                # Show the first validation error in the SnackBar with user-friendly messages
                error = ve.errors()[0]
                field = error["loc"][0]
                
                custom_msg = error["msg"]
                if field == "BloodType":
                    custom_msg = "Must be in correct format (e.g., A+, B-, AB+, O-)."
                elif field == "FullName":
                    custom_msg = "Must be between 2 and 100 characters long."
                elif field == "Phone":
                    custom_msg = "Must be between 6 and 20 characters long."
                    
                show_snack_bar(f"Validation Error ({field}): {custom_msg}")
                return
                
            success = add_donor(valid_donor.DonorID, valid_donor.FullName, valid_donor.BloodType, valid_donor.Phone)
            if success:
                show_snack_bar("Record added successfully!")
                donor_id_input.value = ""
                fullname_input.value = ""
                bloodtype_input.value = ""
                phone_input.value = ""
                refresh_table2()
            else:
                show_snack_bar("Failed to add record. ID might already exist.")

        def on_delete_click(e):
            donor_id_raw = donor_id_input.value
            if not donor_id_raw or not donor_id_raw.strip():
                show_snack_bar("Error: Please enter DonorID to delete!")
                return
                
            try:
                donor_id = int(donor_id_raw)
            except ValueError:
                show_snack_bar("Error: DonorID must be a number!")
                return
                
            deleted = delete_donor(donor_id)
            if deleted:
                show_snack_bar("Record deleted successfully!")
                donor_id_input.value = ""
                refresh_table2()
            else:
                show_snack_bar(f"Error: Donor with ID {donor_id} not found.")

        add_button = ft.ElevatedButton("POST add", color=ft.Colors.WHITE, bgcolor="#C62828", on_click=on_add_click)
        delete_button = ft.ElevatedButton("DELETE", color=ft.Colors.WHITE, bgcolor=ft.Colors.RED_800, on_click=on_delete_click)
        buttons_row = ft.Row([add_button, delete_button])

        page.add(
            table_container2,
            ft.Divider(),
            ft.Text("Add new record", weight=ft.FontWeight.BOLD, size=16, color=ft.Colors.BLACK87),
            inputs_row,
            buttons_row
        )
        page.update()

    # Start the app by showing window 1
    show_window_1()

ft.app(target=main)
