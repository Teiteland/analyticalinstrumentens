import customtkinter as ctk
from tkinter import filedialog
from database import init_db, InstrumentRepository, ColumnRepository, MaintenanceRepository, export_all_to_csv, import_all_from_csv

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class InstrumentApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        init_db()
        
        self.title("Instrumentoversikt")
        self.geometry("1000x800")
        self.minsize(900, 700)
        
        self.current_view = None
        self.current_instrument_id = None
        
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.create_sidebar()
        self.show_dashboard()
        
    def create_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(7, weight=1)
        
        self.logo_label = ctk.CTkLabel(
            self.sidebar, 
            text="Instrument\nOversikt",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        self.nav_buttons = []
        
        nav_items = [
            ("Dashboard", self.show_dashboard),
            ("LC Instrumenter", lambda: self.show_instrument_list("LC")),
            ("GC Instrumenter", lambda: self.show_instrument_list("GC")),
            ("GPC Instrumenter", lambda: self.show_instrument_list("GPC")),
            ("Alle Kolonner", self.show_columns),
        ]
        
        for i, (text, command) in enumerate(nav_items, start=1):
            btn = ctk.CTkButton(
                self.sidebar,
                text=text,
                command=command,
                fg_color="transparent",
                text_color=("gray10", "gray90"),
                hover_color=("gray70", "gray30")
            )
            btn.grid(row=i, column=0, padx=20, pady=5, sticky="ew")
            self.nav_buttons.append(btn)
        
        ctk.CTkLabel(self.sidebar, text="Data", font=ctk.CTkFont(weight="bold")).grid(row=7, column=0, padx=20, pady=(20, 5), sticky="w")
        
        ctk.CTkButton(
            self.sidebar,
            text="Eksporter",
            command=self.show_export,
            fg_color="transparent",
            text_color=("gray10", "gray90"),
            hover_color=("gray70", "gray30")
        ).grid(row=8, column=0, padx=20, pady=5, sticky="ew")
        
        ctk.CTkButton(
            self.sidebar,
            text="Importer",
            command=self.show_import,
            fg_color="transparent",
            text_color=("gray10", "gray90"),
            hover_color=("gray70", "gray30")
        ).grid(row=9, column=0, padx=20, pady=5, sticky="ew")
        
        self.sidebar.grid_columnconfigure(0, weight=1)
        
    def clear_content(self):
        if self.current_view:
            self.current_view.destroy()
            
    def show_dashboard(self):
        self.clear_content()
        
        self.current_view = ctk.CTkFrame(self, fg_color="transparent")
        self.current_view.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.current_view.grid_rowconfigure(2, weight=1)
        self.current_view.grid_columnconfigure(0, weight=1)
        
        title = ctk.CTkLabel(self.current_view, text="Dashboard", font=ctk.CTkFont(size=24, weight="bold"))
        title.grid(row=0, column=0, pady=(0, 20), sticky="w")
        
        stats_frame = ctk.CTkFrame(self.current_view)
        stats_frame.grid(row=1, column=0, pady=(0, 20), sticky="ew")
        stats_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        instruments = InstrumentRepository.get_all()
        
        lc_count = len([i for i in instruments if i["type"] == "LC"])
        gc_count = len([i for i in instruments if i["type"] == "GC"])
        gpc_count = len([i for i in instruments if i["type"] == "GPC"])
        
        ctk.CTkLabel(stats_frame, text=f"LC: {lc_count}", font=ctk.CTkFont(size=16)).grid(row=0, column=0, padx=20, pady=20)
        ctk.CTkLabel(stats_frame, text=f"GC: {gc_count}", font=ctk.CTkFont(size=16)).grid(row=0, column=1, padx=20, pady=20)
        ctk.CTkLabel(stats_frame, text=f"GPC: {gpc_count}", font=ctk.CTkFont(size=16)).grid(row=0, column=2, padx=20, pady=20)
        
        recent_frame = ctk.CTkFrame(self.current_view)
        recent_frame.grid(row=2, column=0, sticky="nsew")
        recent_frame.grid_rowconfigure(1, weight=1)
        recent_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(recent_frame, text="Siste vedlikehold", font=ctk.CTkFont(size=18, weight="bold")).grid(
            row=0, column=0, padx=20, pady=(10, 5), sticky="w"
        )
        
        recent = MaintenanceRepository.get_recent(5)
        
        if recent:
            cols = ["Dato", "Type", "Instrument", "Beskrivelse"]
            tree = ctk.CTkScrollableFrame(recent_frame)
            tree.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
            
            headers = ctk.CTkFrame(tree, fg_color="transparent")
            headers.pack(fill="x")
            for col in cols:
                ctk.CTkLabel(headers, text=col, font=ctk.CTkFont(weight="bold")).pack(side="left", padx=10, pady=5)
                
            for record in recent:
                row_frame = ctk.CTkFrame(tree, fg_color="transparent")
                row_frame.pack(fill="x")
                ctk.CTkLabel(row_frame, text=record["date"] or "-").pack(side="left", padx=10, pady=2)
                ctk.CTkLabel(row_frame, text=record["maintenance_type"] or "-").pack(side="left", padx=10, pady=2)
                ctk.CTkLabel(row_frame, text=record["instrument_name"] or "-").pack(side="left", padx=10, pady=2)
                ctk.CTkLabel(row_frame, text=(record["description"] or "-")[:30]).pack(side="left", padx=10, pady=2)
        else:
            ctk.CTkLabel(recent_frame, text="Ingen vedlikehold registrert").grid(row=1, column=0, pady=20)
            
    def show_instrument_list(self, instrument_type: str):
        self.clear_content()
        self.current_instrument_id = None
        
        self.current_view = ctk.CTkFrame(self, fg_color="transparent")
        self.current_view.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.current_view.grid_rowconfigure(2, weight=1)
        self.current_view.grid_columnconfigure(0, weight=1)
        
        title = ctk.CTkLabel(
            self.current_view, 
            text=f"{instrument_type} Instrumenter", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.grid(row=0, column=0, pady=(0, 10), sticky="w")
        
        btn_frame = ctk.CTkFrame(self.current_view, fg_color="transparent")
        btn_frame.grid(row=1, column=0, pady=(0, 10), sticky="w")
        
        ctk.CTkButton(
            btn_frame,
            text="+ Legg til instrument",
            command=lambda: self.show_add_instrument(instrument_type)
        ).pack(side="left", padx=(0, 10))
        
        instruments = InstrumentRepository.get_all(instrument_type)
        
        if instruments:
            list_frame = ctk.CTkScrollableFrame(self.current_view)
            list_frame.grid(row=2, column=0, sticky="nsew")
            
            for inst in instruments:
                item_frame = ctk.CTkFrame(list_frame)
                item_frame.pack(fill="x", pady=5)
                
                info_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
                info_frame.pack(side="left", padx=10, pady=10)
                
                ctk.CTkLabel(
                    info_frame,
                    text=inst["name"],
                    font=ctk.CTkFont(weight="bold")
                ).pack(anchor="w")
                ctk.CTkLabel(
                    info_frame,
                    text=f"Model: {inst['model'] or '-'} | Serienr: {inst['serial_number'] or '-'} | Kjøpt: {inst['purchase_date'] or '-'}"
                ).pack(anchor="w")
                
                btn_frame_item = ctk.CTkFrame(item_frame, fg_color="transparent")
                btn_frame_item.pack(side="right", padx=10, pady=10)
                
                ctk.CTkButton(
                    btn_frame_item,
                    text="Detaljer",
                    width=80,
                    command=lambda inst_id=inst["id"]: self.show_instrument_detail(inst_id)
                ).pack(padx=2)
                ctk.CTkButton(
                    btn_frame_item,
                    text="Slett",
                    width=60,
                    fg_color="#c42b1c",
                    hover_color="#9f2318",
                    command=lambda inst_id=inst["id"], inst_type=inst["type"]: self.delete_instrument(inst_id, inst_type)
                ).pack(padx=2)
        else:
            ctk.CTkLabel(
                self.current_view,
                text=f"Ingen {instrument_type} instrumenter registrert"
            ).grid(row=2, column=0)
            
    def show_add_instrument(self, instrument_type: str):
        dialog = ctk.CTkToplevel(self)
        dialog.title(f"Legg til {instrument_type}")
        dialog.geometry("450x700")
        dialog.transient(self)
        
        ctk.CTkLabel(dialog, text=f"Legg til {instrument_type}", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)
        
        form = ctk.CTkFrame(dialog, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=20, pady=10)
        
        entries = {}
        
        fields = [
            ("Navn *", "name"),
            ("Model", "model"),
            ("Produsent", "manufacturer"),
            ("Serienummer", "serial_number"),
            ("Kjøpsdato", "purchase_date"),
            ("Notater", "notes"),
        ]
        
        for label, key in fields:
            ctk.CTkLabel(form, text=label).pack(anchor="w", pady=(10, 0))
            if key == "notes":
                entry = ctk.CTkTextbox(form, height=60)
                entry.pack(fill="x", pady=(5, 10))
                entries[key] = entry
            else:
                entry = ctk.CTkEntry(form)
                entry.pack(fill="x", pady=(5, 10))
                entries[key] = entry
                
        def save():
            name = entries["name"].get().strip()
            if not name:
                ctk.CTkLabel(form, text="Navn er påkrevd", text_color="red").pack()
                return
                
            InstrumentRepository.create(
                name=name,
                instrument_type=instrument_type,
                model=entries["model"].get().strip() or None,
                manufacturer=entries["manufacturer"].get().strip() or None,
                serial_number=entries["serial_number"].get().strip() or None,
                purchase_date=entries["purchase_date"].get().strip() or None,
                notes=entries["notes"].get("1.0", "end").strip() or None
            )
            dialog.destroy()
            self.show_instrument_list(instrument_type)
            
        ctk.CTkButton(dialog, text="Lagre", command=save).pack(pady=10)
        ctk.CTkButton(dialog, text="Avbryt", command=dialog.destroy).pack(pady=5)
        
    def show_instrument_detail(self, instrument_id: int):
        self.current_instrument_id = instrument_id
        instrument = InstrumentRepository.get_by_id(instrument_id)
        
        if not instrument:
            return
        
        self.clear_content()
        
        self.current_view = ctk.CTkFrame(self, fg_color="transparent")
        self.current_view.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.current_view.grid_rowconfigure(3, weight=1)
        self.current_view.grid_columnconfigure(0, weight=1)
        
        header = ctk.CTkFrame(self.current_view, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        ctk.CTkButton(
            header,
            text="← Tilbake",
            command=lambda: self.show_instrument_list(instrument["type"]),
            fg_color="transparent"
        ).pack(side="left")
        
        title = ctk.CTkLabel(
            header,
            text=f"{instrument['name']} ({instrument['type']})",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(side="left", padx=10)
        
        info_frame = ctk.CTkFrame(self.current_view)
        info_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        
        info_items = [
            ("Model", instrument["model"]),
            ("Produsent", instrument["manufacturer"]),
            ("Serienummer", instrument["serial_number"]),
            ("Kjøpsdato", instrument["purchase_date"]),
            ("Status", instrument["status"]),
        ]
        
        for i, (label, value) in enumerate(info_items):
            ctk.CTkLabel(info_frame, text=f"{label}:", font=ctk.CTkFont(weight="bold")).grid(
                row=i//2, column=(i%2)*2, sticky="w", padx=10, pady=5
            )
            ctk.CTkLabel(info_frame, text=value or "-").grid(
                row=i//2, column=(i%2)*2+1, sticky="w", padx=10, pady=5
            )
            
        tabs = ctk.CTkTabview(self.current_view)
        tabs.grid(row=2, column=0, sticky="nsew")
        
        columns_tab = tabs.add("Kolonner")
        maintenance_tab = tabs.add("Vedlikehold")
        
        self.build_columns_tab(columns_tab, instrument_id)
        self.build_maintenance_tab(maintenance_tab, instrument_id)
        
    def build_columns_tab(self, parent, instrument_id):
        parent.grid_rowconfigure(1, weight=1)
        parent.grid_columnconfigure(0, weight=1)
        
        btn_frame = ctk.CTkFrame(parent, fg_color="transparent")
        btn_frame.grid(row=0, column=0, sticky="w", pady=(0, 10))
        
        ctk.CTkButton(
            btn_frame,
            text="+ Legg til kolonne",
            command=lambda: self.show_add_column(instrument_id)
        ).pack(side="left")
        
        columns = ColumnRepository.get_by_instrument(instrument_id)
        
        if columns:
            list_frame = ctk.CTkScrollableFrame(parent)
            list_frame.grid(row=1, column=0, sticky="nsew")
            
            for col in columns:
                item = ctk.CTkFrame(list_frame)
                item.pack(fill="x", pady=3)
                
                info = ctk.CTkFrame(item, fg_color="transparent")
                info.pack(side="left", padx=10, pady=10)
                
                ctk.CTkLabel(info, text=col["name"], font=ctk.CTkFont(weight="bold")).pack(anchor="w")
                ctk.CTkLabel(info, text=f"Type: {col['column_type'] or '-'} | Dim: {col['length_cm'] or '-'}cm x {col['diameter_mm'] or '-'}mm | Status: {col['status']}").pack(anchor="w")
                
                ctk.CTkButton(
                    item,
                    text="Slett",
                    width=60,
                    fg_color="#c42b1c",
                    hover_color="#9f2318",
                    command=lambda col_id=col["id"], inst_id=instrument_id: self.delete_column(col_id, inst_id)
                ).pack(side="right", padx=10)
        else:
            ctk.CTkLabel(parent, text="Ingen kolonner registrert").grid(row=1, column=0, pady=20)
            
    def build_maintenance_tab(self, parent, instrument_id):
        parent.grid_rowconfigure(1, weight=1)
        parent.grid_columnconfigure(0, weight=1)
        
        btn_frame = ctk.CTkFrame(parent, fg_color="transparent")
        btn_frame.grid(row=0, column=0, sticky="w", pady=(0, 10))
        
        ctk.CTkButton(
            btn_frame,
            text="+ Legg til vedlikehold",
            command=lambda: self.show_add_maintenance(instrument_id)
        ).pack(side="left")
        
        records = MaintenanceRepository.get_by_instrument(instrument_id)
        
        if records:
            list_frame = ctk.CTkScrollableFrame(parent)
            list_frame.grid(row=1, column=0, sticky="nsew")
            
            for rec in records:
                item = ctk.CTkFrame(list_frame)
                item.pack(fill="x", pady=3)
                
                info = ctk.CTkFrame(item, fg_color="transparent")
                info.pack(side="left", padx=10, pady=10)
                
                ctk.CTkLabel(info, text=f"{rec['date']} - {rec['maintenance_type']}", font=ctk.CTkFont(weight="bold")).pack(anchor="w")
                ctk.CTkLabel(info, text=f"Beskrivelse: {rec['description'] or '-'}").pack(anchor="w")
                ctk.CTkLabel(info, text=f"Utført av: {rec['performed_by'] or '-'} | Kostnad: {rec['cost'] or '-'}").pack(anchor="w")
                
                ctk.CTkButton(
                    item,
                    text="Slett",
                    width=60,
                    fg_color="#c42b1c",
                    hover_color="#9f2318",
                    command=lambda maint_id=rec["id"], inst_id=instrument_id: self.delete_maintenance(maint_id, inst_id)
                ).pack(side="right", padx=10)
        else:
            ctk.CTkLabel(parent, text="Ingen vedlikehold registrert").grid(row=1, column=0, pady=20)
            
    def show_add_column(self, instrument_id: int):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Legg til kolonne")
        dialog.geometry("450x650")
        dialog.transient(self)
        
        ctk.CTkLabel(dialog, text="Legg til kolonne", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)
        
        form = ctk.CTkFrame(dialog, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=20, pady=10)
        
        entries = {}
        
        fields = [
            ("Navn *", "name"),
            ("Type (f.eks. C18)", "column_type"),
            ("Lengde (cm)", "length_cm"),
            ("Diameter (mm)", "diameter_mm"),
            ("Pore størrelse", "pore_size"),
            ("Installasjonsdato", "install_date"),
            ("Notater", "notes"),
        ]
        
        for label, key in fields:
            ctk.CTkLabel(form, text=label).pack(anchor="w", pady=(10, 0))
            if key == "notes":
                entry = ctk.CTkTextbox(form, height=60)
                entry.pack(fill="x", pady=(5, 10))
                entries[key] = entry
            else:
                entry = ctk.CTkEntry(form)
                entry.pack(fill="x", pady=(5, 10))
                entries[key] = entry
                
        def save():
            name = entries["name"].get().strip()
            if not name:
                return
                
            length = entries["length_cm"].get().strip()
            diameter = entries["diameter_mm"].get().strip()
            
            ColumnRepository.create(
                instrument_id=instrument_id,
                name=name,
                column_type=entries["column_type"].get().strip() or None,
                length_cm=float(length) if length else None,
                diameter_mm=float(diameter) if diameter else None,
                pore_size=entries["pore_size"].get().strip() or None,
                install_date=entries["install_date"].get().strip() or None,
                notes=entries["notes"].get("1.0", "end").strip() or None
            )
            dialog.destroy()
            self.show_instrument_detail(instrument_id)
            
        ctk.CTkButton(dialog, text="Lagre", command=save).pack(pady=10)
        ctk.CTkButton(dialog, text="Avbryt", command=dialog.destroy).pack(pady=5)
        
    def show_add_maintenance(self, instrument_id: int):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Legg til vedlikehold")
        dialog.geometry("450x600")
        dialog.transient(self)
        
        ctk.CTkLabel(dialog, text="Legg til vedlikehold", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)
        
        form = ctk.CTkFrame(dialog, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=20, pady=10)
        
        entries = {}
        
        ctk.CTkLabel(form, text="Dato *").pack(anchor="w", pady=(10, 0))
        date_entry = ctk.CTkEntry(form)
        date_entry.pack(fill="x", pady=(5, 10))
        date_entry.insert(0, "2026-02-18")
        entries["date"] = date_entry
        
        ctk.CTkLabel(form, text="Type *").pack(anchor="w", pady=(10, 0))
        type_combo = ctk.CTkComboBox(form, values=["Preventive", "Repair", "Calibration", "Other"])
        type_combo.pack(fill="x", pady=(5, 10))
        entries["maintenance_type"] = type_combo
        
        fields = [
            ("Beskrivelse", "description"),
            ("Utført av", "performed_by"),
            ("Kostnad", "cost"),
        ]
        
        for label, key in fields:
            ctk.CTkLabel(form, text=label).pack(anchor="w", pady=(10, 0))
            entry = ctk.CTkEntry(form)
            entry.pack(fill="x", pady=(5, 10))
            entries[key] = entry
                
        def save():
            date = entries["date"].get().strip()
            maint_type = entries["maintenance_type"].get()
            if not date or not maint_type:
                return
                
            cost = entries["cost"].get().strip()
            
            MaintenanceRepository.create(
                instrument_id=instrument_id,
                date=date,
                maintenance_type=maint_type,
                description=entries["description"].get().strip() or None,
                performed_by=entries["performed_by"].get().strip() or None,
                cost=float(cost) if cost else None
            )
            dialog.destroy()
            self.show_instrument_detail(instrument_id)
            
        ctk.CTkButton(dialog, text="Lagre", command=save).pack(pady=10)
        ctk.CTkButton(dialog, text="Avbryt", command=dialog.destroy).pack(pady=5)
        
    def delete_instrument(self, instrument_id: int, instrument_type: str = None):
        if instrument_type is None:
            inst = InstrumentRepository.get_by_id(instrument_id)
            instrument_type = inst["type"] if inst else "LC"
        
        dialog = ctk.CTkToplevel(self)
        dialog.title("Bekreft sletting")
        dialog.geometry("400x180")
        dialog.transient(self)
        
        ctk.CTkLabel(
            dialog, 
            text="Er du sikker på at du vil slette dette instrumentet?\nDette vil også slette alle tilknyttede kolonner og vedlikehold.",
            wraplength=350
        ).pack(pady=20)
        
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(pady=10)
        
        def confirm():
            InstrumentRepository.delete(instrument_id)
            dialog.destroy()
            self.show_instrument_list(instrument_type)
            
        ctk.CTkButton(btn_frame, text="Ja, slett", fg_color="#c42b1c", hover_color="#9f2318", command=confirm).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Avbryt", command=dialog.destroy).pack(side="left", padx=5)
        
    def delete_column(self, column_id: int, instrument_id: int):
        ColumnRepository.delete(column_id)
        self.show_instrument_detail(instrument_id)
        
    def delete_maintenance(self, maintenance_id: int, instrument_id: int):
        MaintenanceRepository.delete(maintenance_id)
        self.show_instrument_detail(instrument_id)
        
    def show_columns(self):
        self.clear_content()
        
        self.current_view = ctk.CTkFrame(self, fg_color="transparent")
        self.current_view.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.current_view.grid_rowconfigure(1, weight=1)
        self.current_view.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            self.current_view,
            text="Alle Kolonner",
            font=ctk.CTkFont(size=24, weight="bold")
        ).grid(row=0, column=0, pady=(0, 10), sticky="w")
        
        columns = ColumnRepository.get_all()
        
        if columns:
            list_frame = ctk.CTkScrollableFrame(self.current_view)
            list_frame.grid(row=1, column=0, sticky="nsew")
            
            headers = ctk.CTkFrame(list_frame, fg_color="transparent")
            headers.pack(fill="x")
            
            ctk.CTkLabel(headers, text="Navn", font=ctk.CTkFont(weight="bold"), width=120).pack(side="left", padx=5)
            ctk.CTkLabel(headers, text="Type", font=ctk.CTkFont(weight="bold"), width=80).pack(side="left", padx=5)
            ctk.CTkLabel(headers, text="Instrument", font=ctk.CTkFont(weight="bold"), width=100).pack(side="left", padx=5)
            ctk.CTkLabel(headers, text="Status", font=ctk.CTkFont(weight="bold"), width=80).pack(side="left", padx=5)
            ctk.CTkLabel(headers, text="Installert", font=ctk.CTkFont(weight="bold"), width=80).pack(side="left", padx=5)
            
            for col in columns:
                row = ctk.CTkFrame(list_frame, fg_color="transparent")
                row.pack(fill="x", pady=2)
                
                ctk.CTkLabel(row, text=col["name"], width=120).pack(side="left", padx=5)
                ctk.CTkLabel(row, text=col["column_type"] or "-", width=80).pack(side="left", padx=5)
                ctk.CTkLabel(row, text=col["instrument_name"] or "-", width=100).pack(side="left", padx=5)
                ctk.CTkLabel(row, text=col["status"], width=80).pack(side="left", padx=5)
                ctk.CTkLabel(row, text=col["install_date"] or "-", width=80).pack(side="left", padx=5)
        else:
            ctk.CTkLabel(self.current_view, text="Ingen kolonner registrert").grid(row=1, column=0)

    def show_export(self):
        folder = filedialog.askdirectory(title="Velg mappe for eksport")
        if folder:
            try:
                export_all_to_csv(folder)
                dialog = ctk.CTkToplevel(self)
                dialog.title("Eksport vellykket")
                dialog.geometry("300x150")
                dialog.transient(self)
                ctk.CTkLabel(dialog, text="Eksport fullført!", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=20)
                ctk.CTkLabel(dialog, text=f"Filer eksportert til:\n{folder}").pack(pady=10)
                ctk.CTkButton(dialog, text="OK", command=dialog.destroy).pack(pady=10)
            except Exception as e:
                dialog = ctk.CTkToplevel(self)
                dialog.title("Feil")
                dialog.geometry("300x150")
                dialog.transient(self)
                ctk.CTkLabel(dialog, text="Eksport feilet!", text_color="red", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=20)
                ctk.CTkLabel(dialog, text=str(e)).pack(pady=10)
                ctk.CTkButton(dialog, text="OK", command=dialog.destroy).pack(pady=10)

    def show_import(self):
        folder = filedialog.askdirectory(title="Velg mappe for import")
        if folder:
            try:
                import_all_from_csv(folder)
                dialog = ctk.CTkToplevel(self)
                dialog.title("Import vellykket")
                dialog.geometry("300x150")
                dialog.transient(self)
                ctk.CTkLabel(dialog, text="Import fullført!", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=20)
                ctk.CTkLabel(dialog, text="Data er importert.").pack(pady=10)
                ctk.CTkButton(dialog, text="OK", command=lambda: [dialog.destroy(), self.show_dashboard()]).pack(pady=10)
            except Exception as e:
                dialog = ctk.CTkToplevel(self)
                dialog.title("Feil")
                dialog.geometry("300x150")
                dialog.transient(self)
                ctk.CTkLabel(dialog, text="Import feilet!", text_color="red", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=20)
                ctk.CTkLabel(dialog, text=str(e)).pack(pady=10)
                ctk.CTkButton(dialog, text="OK", command=dialog.destroy).pack(pady=10)


if __name__ == "__main__":
    app = InstrumentApp()
    app.mainloop()
