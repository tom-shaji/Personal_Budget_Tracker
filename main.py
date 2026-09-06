# =============================================================================
# Personal Budget Tracker  v1.0.0
# A desktop application built with Python, Tkinter, and Matplotlib.
#
# Usage  : python main.py
# Licence: MIT — © 2026 tom-shaji
# =============================================================================

__version__ = "1.0.0"
__author__  = "tom-shaji"
__license__ = "MIT"


import tkinter as tk
from tkinter import ttk, messagebox
import csv
import os
from datetime import date
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.patches as mpatches

# --- Constants ---------------------------------------------------------------

CSV_FILE = "budget_data.csv"
CSV_HEADERS = ["type", "category", "amount", "date", "description"]

INCOME_CATEGORIES = [
    "Salary", "Freelance", "Investment", "Gift", "Bonus", "Other Income"
]
EXPENSE_CATEGORIES = [
    "Food", "Rent", "Utilities", "Transport", "Healthcare",
    "Entertainment", "Shopping", "Education", "Savings", "Other Expense"
]

# Colour palette
BG_DARK       = "#1A1D2E"
BG_CARD       = "#252840"
BG_ENTRY      = "#2F3354"
ACCENT_BLUE   = "#4E6EF2"
ACCENT_GREEN  = "#2ECC71"
ACCENT_RED    = "#E74C3C"
ACCENT_YELLOW = "#F1C40F"
TEXT_PRIMARY  = "#EAEAEA"
TEXT_MUTED    = "#8892B0"
BORDER_COLOR  = "#3A3F6B"

PIE_COLORS = [
    "#4E6EF2", "#E74C3C", "#2ECC71", "#F1C40F", "#9B59B6",
    "#E67E22", "#1ABC9C", "#E91E63", "#00BCD4", "#FF5722"
]

# =============================================================================
# CSV helpers
# =============================================================================

def ensure_csv_exists():
    """Create the CSV file with headers if it doesn't already exist."""
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
            writer.writeheader()


def load_transactions():
    """Return all transactions from the CSV as a list of dicts."""
    ensure_csv_exists()
    transactions = []
    with open(CSV_FILE, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                row["amount"] = float(row["amount"])
                transactions.append(row)
            except ValueError:
                pass  # skip malformed rows
    return transactions


def save_transactions(transactions):
    """Overwrite the CSV with the given list of transaction dicts."""
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
        writer.writeheader()
        for t in transactions:
            writer.writerow(t)


def append_transaction(transaction):
    """Append a single transaction dict to the CSV."""
    ensure_csv_exists()
    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
        writer.writerow(transaction)


# =============================================================================
# Validation helpers
# =============================================================================

def validate_amount(value: str) -> float | None:
    """Return the float value if valid and positive, else None."""
    try:
        amount = float(value.strip())
        if amount <= 0:
            return None
        return amount
    except ValueError:
        return None


def validate_date(value: str) -> bool:
    """Return True if value is a valid YYYY-MM-DD date string."""
    try:
        parts = value.strip().split("-")
        if len(parts) != 3:
            return False
        year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
        date(year, month, day)  # raises ValueError for invalid dates
        return True
    except (ValueError, AttributeError):
        return False


# =============================================================================
# ToolTip helper
# =============================================================================

class ToolTip:
    """Simple hover tooltip for any Tkinter widget."""

    def __init__(self, widget, text: str):
        self.widget  = widget
        self.text    = text
        self.tip_win = None
        widget.bind("<Enter>", self._show)
        widget.bind("<Leave>", self._hide)

    def _show(self, _=None):
        if self.tip_win or not self.text:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 4
        self.tip_win = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        tk.Label(tw, text=self.text, font=("Segoe UI", 9),
                 bg="#2F3354", fg=TEXT_PRIMARY,
                 relief="solid", bd=1, padx=6, pady=3).pack()

    def _hide(self, _=None):
        if self.tip_win:
            self.tip_win.destroy()
            self.tip_win = None


# =============================================================================
# Main Application Class
# =============================================================================

class BudgetTracker(tk.Tk):
    """Root window and application controller."""

    def __init__(self):
        super().__init__()
        self.title("💰 Personal Budget Tracker")
        self.geometry("1200x820")
        self.minsize(900, 650)
        self.configure(bg=BG_DARK)

        # In-memory transaction list (mirrors CSV)
        self.transactions: list[dict] = load_transactions()

        self._build_ui()
        self._refresh_table()
        self._refresh_summary()
        self._refresh_chart()
        self._refresh_title()

    # -------------------------------------------------------------------------
    # UI construction
    # -------------------------------------------------------------------------

    def _build_ui(self):
        """Assemble all UI sections."""
        # ── Title bar ────────────────────────────────────────────────────────
        title_frame = tk.Frame(self, bg=BG_DARK, pady=12)
        title_frame.pack(fill="x", padx=20)

        tk.Label(
            title_frame,
            text="💰  Personal Budget Tracker",
            font=("Segoe UI", 22, "bold"),
            bg=BG_DARK, fg=TEXT_PRIMARY
        ).pack(side="left")

        tk.Label(
            title_frame,
            text="Track · Analyse · Save",
            font=("Segoe UI", 11),
            bg=BG_DARK, fg=TEXT_MUTED
        ).pack(side="left", padx=16, pady=6)

        # ── Main content area ─────────────────────────────────────────────────
        content = tk.Frame(self, bg=BG_DARK)
        content.pack(fill="both", expand=True, padx=20, pady=(0, 16))

        # Left column: form + summary + buttons
        left = tk.Frame(content, bg=BG_DARK, width=380)
        left.pack(side="left", fill="y", padx=(0, 12))
        left.pack_propagate(False)

        # Right column: table + chart
        right = tk.Frame(content, bg=BG_DARK)
        right.pack(side="left", fill="both", expand=True)

        self._build_form(left)
        self._build_summary(left)
        self._build_buttons(left)
        self._build_table(right)
        self._build_chart(right)

        self._build_statusbar()

    # ── Form ──────────────────────────────────────────────────────────────────

    def _build_form(self, parent):
        """Input form for adding a new transaction."""
        card = self._card(parent, "➕  Add Transaction")
        card.pack(fill="x", pady=(0, 10))

        inner = tk.Frame(card, bg=BG_CARD)
        inner.pack(fill="x", padx=14, pady=8)

        # Transaction type radio
        self._label(inner, "Transaction Type")
        type_row = tk.Frame(inner, bg=BG_CARD)
        type_row.pack(fill="x", pady=(2, 8))

        self.type_var = tk.StringVar(value="Expense")
        for text, val in [("💸  Expense", "Expense"), ("💵  Income", "Income")]:
            rb = tk.Radiobutton(
                type_row, text=text, variable=self.type_var, value=val,
                command=self._on_type_change,
                bg=BG_CARD, fg=TEXT_PRIMARY, selectcolor=BG_ENTRY,
                activebackground=BG_CARD, activeforeground=TEXT_PRIMARY,
                font=("Segoe UI", 10), cursor="hand2"
            )
            rb.pack(side="left", padx=(0, 16))

        # Category dropdown
        self._label(inner, "Category")
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(
            inner, textvariable=self.category_var,
            values=EXPENSE_CATEGORIES, state="readonly",
            font=("Segoe UI", 10)
        )
        self.category_combo.pack(fill="x", pady=(2, 8))
        self.category_combo.current(0)

        # Amount
        self._label(inner, "Amount (₹)")
        self.amount_var = tk.StringVar()
        self._entry(inner, self.amount_var).pack(fill="x", pady=(2, 8))

        # Date
        self._label(inner, "Date  (YYYY-MM-DD)")
        self.date_var = tk.StringVar(value=str(date.today()))
        date_row = tk.Frame(inner, bg=BG_CARD)
        date_row.pack(fill="x", pady=(2, 8))
        self._entry(date_row, self.date_var).pack(side="left", fill="x", expand=True)
        tk.Button(
            date_row, text="Today", font=("Segoe UI", 8),
            bg=ACCENT_BLUE, fg="white", relief="flat", padx=6, cursor="hand2",
            command=lambda: self.date_var.set(str(date.today()))
        ).pack(side="left", padx=(4, 0))

        # Description
        self._label(inner, "Description")
        self.desc_var = tk.StringVar()
        self._entry(inner, self.desc_var).pack(fill="x", pady=(2, 4))

        # Add button
        # Press Enter anywhere in the form to submit
        self.bind("<Return>", lambda e: self._add_transaction())
        # Ctrl+D — delete selected transaction
        self.bind("<Control-d>", lambda e: self._delete_selected())
        # Escape — reset the input form
        self.bind("<Escape>", lambda e: self._clear_form())

        btn_row = tk.Frame(inner, bg=BG_CARD)
        btn_row.pack(fill="x", pady=(12, 4))

        tk.Button(
            btn_row, text="  ✚  Add  ",
            font=("Segoe UI", 11, "bold"),
            bg=ACCENT_BLUE, fg="white", relief="flat",
            activebackground="#3A58D4", activeforeground="white",
            cursor="hand2", pady=8,
            command=self._add_transaction
        ).pack(side="left", fill="x", expand=True, padx=(0, 4))

        tk.Button(
            btn_row, text="↺ Reset",
            font=("Segoe UI", 10),
            bg=BG_ENTRY, fg=TEXT_MUTED, relief="flat",
            activebackground=BORDER_COLOR,
            cursor="hand2", pady=8,
            command=self._clear_form
        ).pack(side="left")

    # ── Summary ───────────────────────────────────────────────────────────────

    def _build_summary(self, parent):
        """Summary cards showing totals."""
        card = self._card(parent, "📊  Summary")
        card.pack(fill="x", pady=(0, 10))

        grid = tk.Frame(card, bg=BG_CARD)
        grid.pack(fill="x", padx=14, pady=8)
        grid.columnconfigure((0, 1), weight=1)

        self.lbl_income  = self._stat_cell(grid, "Total Income",  "₹0.00",  ACCENT_GREEN,  0, 0)
        self.lbl_expense = self._stat_cell(grid, "Total Expenses","₹0.00",  ACCENT_RED,    0, 1)
        self.lbl_balance = self._stat_cell(grid, "Balance",       "₹0.00",  ACCENT_YELLOW, 1, 0)
        self.lbl_count   = self._stat_cell(grid, "Transactions",  "0",      ACCENT_BLUE,   1, 1)

    def _stat_cell(self, parent, title, initial, color, row, col):
        """A single coloured stat box. Returns the value Label."""
        cell = tk.Frame(parent, bg=BG_ENTRY, padx=10, pady=8)
        cell.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")

        tk.Label(cell, text=title, font=("Segoe UI", 8),
                 bg=BG_ENTRY, fg=TEXT_MUTED).pack(anchor="w")
        val_lbl = tk.Label(cell, text=initial, font=("Segoe UI", 14, "bold"),
                           bg=BG_ENTRY, fg=color)
        val_lbl.pack(anchor="w")
        return val_lbl

    # ── Action buttons ────────────────────────────────────────────────────────

    def _build_buttons(self, parent):
        """Delete and Clear buttons."""
        card = self._card(parent, "⚙️  Actions")
        card.pack(fill="x")

        btn_frame = tk.Frame(card, bg=BG_CARD)
        btn_frame.pack(fill="x", padx=14, pady=10)

        del_btn = tk.Button(
            btn_frame, text="🗑  Delete Selected",
            font=("Segoe UI", 10, "bold"),
            bg=ACCENT_RED, fg="white", relief="flat",
            activebackground="#C0392B", cursor="hand2", pady=7,
            command=self._delete_selected
        )
        del_btn.pack(fill="x", pady=(0, 6))
        ToolTip(del_btn, "Select a row, then click  —  or press Ctrl+D")

        clr_btn = tk.Button(
            btn_frame, text="🧹  Clear All Transactions",
            font=("Segoe UI", 10),
            bg=BG_ENTRY, fg=TEXT_MUTED, relief="flat",
            activebackground=BORDER_COLOR, cursor="hand2", pady=7,
            command=self._clear_all
        )
        clr_btn.pack(fill="x")
        ToolTip(clr_btn, "Permanently delete every transaction")

    # ── Transaction table ─────────────────────────────────────────────────────

    def _build_table(self, parent):
        """Treeview showing all transactions."""
        card = self._card(parent, "📋  All Transactions")
        card.pack(fill="both", expand=True, pady=(0, 10))

        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Custom.Treeview",
            background=BG_CARD, foreground=TEXT_PRIMARY,
            fieldbackground=BG_CARD, rowheight=28,
            font=("Segoe UI", 10)
        )
        style.configure(
            "Custom.Treeview.Heading",
            background=BG_ENTRY, foreground=TEXT_PRIMARY,
            font=("Segoe UI", 10, "bold"), relief="flat"
        )
        style.map("Custom.Treeview",
                  background=[("selected", ACCENT_BLUE)],
                  foreground=[("selected", "white")])

        columns = ("type", "category", "amount", "date", "description")
        self.tree = ttk.Treeview(
            card, columns=columns, show="headings",
            style="Custom.Treeview", selectmode="browse"
        )

        col_conf = {
            "type":        ("Type",        90,  "center"),
            "category":    ("Category",    130, "w"),
            "amount":      ("Amount (₹)",  110, "e"),
            "date":        ("Date",        110, "center"),
            "description": ("Description", 220, "w"),
        }
        for col, (heading, width, anchor) in col_conf.items():
            self.tree.heading(col, text=heading,
                              command=lambda c=col: self._sort_tree(c))
            self.tree.column(col, width=width, anchor=anchor, minwidth=60)

        # Scrollbars
        vsb = ttk.Scrollbar(card, orient="vertical",   command=self.tree.yview)
        hsb = ttk.Scrollbar(card, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        vsb.pack(side="right",  fill="y")
        hsb.pack(side="bottom", fill="x")
        self.tree.pack(fill="both", expand=True, padx=10, pady=(0, 4))

        # Tag colours for income / expense rows
        self.tree.tag_configure("income",     foreground=ACCENT_GREEN)
        self.tree.tag_configure("expense",    foreground=ACCENT_RED)
        self.tree.tag_configure("odd_income", foreground=ACCENT_GREEN, background="#1E2A20")
        self.tree.tag_configure("odd_expense",foreground=ACCENT_RED,   background="#2A1E1E")

    # ── Pie chart ─────────────────────────────────────────────────────────────

    def _build_chart(self, parent):
        """Matplotlib pie chart embedded in the window."""
        card = self._card(parent, "🥧  Expenses by Category")
        card.pack(fill="x", pady=(0, 0))

        self.fig, self.ax = plt.subplots(figsize=(5, 2.6), facecolor=BG_CARD)
        self.fig.subplots_adjust(left=0, right=0.65, top=0.9, bottom=0.05)
        self.ax.set_facecolor(BG_CARD)

        self.canvas_widget = FigureCanvasTkAgg(self.fig, master=card)
        self.canvas_widget.get_tk_widget().pack(
            fill="both", expand=True, padx=10, pady=(0, 8)
        )

    # -------------------------------------------------------------------------
    # Shared widget factories
    # -------------------------------------------------------------------------

    def _card(self, parent, title: str) -> tk.Frame:
        """A titled card frame."""
        frame = tk.Frame(parent, bg=BG_CARD, bd=0,
                         highlightthickness=1, highlightbackground=BORDER_COLOR)
        tk.Label(
            frame, text=title, font=("Segoe UI", 11, "bold"),
            bg=BG_CARD, fg=TEXT_PRIMARY, pady=8, padx=14
        ).pack(fill="x", anchor="w")
        ttk.Separator(frame, orient="horizontal").pack(fill="x")
        return frame

    def _label(self, parent, text: str):
        tk.Label(parent, text=text, font=("Segoe UI", 9),
                 bg=BG_CARD, fg=TEXT_MUTED).pack(anchor="w")

    def _entry(self, parent, textvariable) -> tk.Entry:
        return tk.Entry(
            parent, textvariable=textvariable,
            font=("Segoe UI", 10),
            bg=BG_ENTRY, fg=TEXT_PRIMARY,
            insertbackground=TEXT_PRIMARY,
            relief="flat", bd=6
        )

    # -------------------------------------------------------------------------
    # Event handlers
    # -------------------------------------------------------------------------

    def _on_type_change(self):
        """Swap category list when the transaction type changes."""
        t = self.type_var.get()
        cats = INCOME_CATEGORIES if t == "Income" else EXPENSE_CATEGORIES
        self.category_combo["values"] = cats
        self.category_combo.current(0)

    def _add_transaction(self):
        """Validate inputs and add a new transaction."""
        t_type   = self.type_var.get()
        category = self.category_var.get().strip()
        amount   = self.amount_var.get().strip()
        t_date   = self.date_var.get().strip()
        desc     = self.desc_var.get().strip()

        # --- Validation ---
        if not category:
            messagebox.showwarning("Missing Field", "Please select a category.")
            return
        amt = validate_amount(amount)
        if amt is None:
            messagebox.showwarning(
                "Invalid Amount",
                "Amount must be a positive number (e.g. 1500 or 99.50)."
            )
            return
        if not validate_date(t_date):
            messagebox.showwarning(
                "Invalid Date",
                "Date must be in YYYY-MM-DD format (e.g. 2025-06-15)."
            )
            return
        if not desc:
            messagebox.showwarning("Missing Field", "Please enter a description.")
            return

        transaction = {
            "type":        t_type,
            "category":    category,
            "amount":      amt,
            "date":        t_date,
            "description": desc
        }

        self.transactions.append(transaction)
        append_transaction(transaction)

        self._refresh_table()
        self._refresh_summary()
        self._refresh_chart()
        self._refresh_title()
        self._clear_form()
        self._set_status(f"✅  {t_type} of ₹{amt:,.2f} added — {t_date}")
        messagebox.showinfo("Success", f"{t_type} of ₹{amt:.2f} added successfully! ✅")

    def _delete_selected(self):
        """Delete the currently selected table row."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a transaction to delete.")
            return

        if not messagebox.askyesno(
            "Confirm Delete", "Delete this transaction? This cannot be undone."
        ):
            return

        # iid == stringified index into self.transactions
        idx = int(self.tree.item(selected[0])["values"][5])  # hidden index column
        self.transactions.pop(idx)
        save_transactions(self.transactions)

        self._refresh_table()
        self._refresh_summary()
        self._refresh_chart()
        self._refresh_title()

    def _clear_all(self):
        """Delete every transaction after confirmation."""
        if not self.transactions:
            messagebox.showinfo("Nothing to Clear", "There are no transactions to clear.")
            return
        if not messagebox.askyesno(
            "Confirm Clear All",
            "This will permanently delete ALL transactions.\nAre you sure?"
        ):
            return

        self.transactions.clear()
        save_transactions(self.transactions)

        self._refresh_table()
        self._refresh_summary()
        self._refresh_chart()
        self._refresh_title()
        messagebox.showinfo("Cleared", "All transactions have been deleted.")

    def _clear_form(self):
        """Reset input fields after a successful add."""
        self.amount_var.set("")
        self.date_var.set(str(date.today()))
        self.desc_var.set("")
        self.category_combo.current(0)

    def _sort_tree(self, col):
        """Sort table by column header click (toggle asc/desc)."""
        data = [(self.tree.set(child, col), child)
                for child in self.tree.get_children("")]
        try:
            data.sort(key=lambda x: float(x[0].replace("₹", "").replace(",", "")))
        except ValueError:
            data.sort()

        for index, (_, child) in enumerate(data):
            self.tree.move(child, "", index)

    # -------------------------------------------------------------------------
    # Refresh methods
    # -------------------------------------------------------------------------

    def _refresh_table(self):
        """Repopulate the Treeview from self.transactions."""
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Add a hidden 6th column for the original list index
        columns = list(self.tree["columns"]) + []  # keep existing 5
        if len(self.tree["columns"]) == 5:
            self.tree["columns"] = ("type", "category", "amount", "date", "description", "idx")
            self.tree.column("idx", width=0, stretch=False)
            self.tree.heading("idx", text="")

        for i, t in enumerate(self.transactions):
            is_odd = i % 2 == 1
            if t["type"] == "Income":
                tag = "odd_income" if is_odd else "income"
            else:
                tag = "odd_expense" if is_odd else "expense"
            sign = "+" if t["type"] == "Income" else "-"
            self.tree.insert(
                "", "end",
                values=(
                    t["type"],
                    t["category"],
                    f"{sign}₹{float(t['amount']):,.2f}",
                    t["date"],
                    t["description"],
                    i          # hidden index
                ),
                tags=(tag,)
            )

    def _refresh_summary(self):
        """Recalculate and display totals."""
        total_income  = sum(t["amount"] for t in self.transactions if t["type"] == "Income")
        total_expense = sum(t["amount"] for t in self.transactions if t["type"] == "Expense")
        balance       = total_income - total_expense
        count         = len(self.transactions)

        self.lbl_income.config(text=f"₹{total_income:,.2f}")
        self.lbl_expense.config(text=f"₹{total_expense:,.2f}")

        bal_color = ACCENT_GREEN if balance >= 0 else ACCENT_RED
        self.lbl_balance.config(text=f"₹{balance:,.2f}", fg=bal_color)
        self.lbl_count.config(text=str(count))

    def _refresh_chart(self):
        """Redraw the expenses-by-category pie chart."""
        self.ax.clear()
        self.ax.set_facecolor(BG_CARD)

        # Aggregate expense amounts per category
        expense_map: dict[str, float] = {}
        for t in self.transactions:
            if t["type"] == "Expense":
                expense_map[t["category"]] = \
                    expense_map.get(t["category"], 0) + t["amount"]

        if not expense_map:
            self.ax.text(
                0.5, 0.5, "No expense data yet",
                ha="center", va="center",
                color=TEXT_MUTED, fontsize=11,
                transform=self.ax.transAxes
            )
            self.ax.axis("off")
            self.canvas_widget.draw()
            return

        labels = list(expense_map.keys())
        sizes  = list(expense_map.values())
        colors = [PIE_COLORS[i % len(PIE_COLORS)] for i in range(len(labels))]

        wedges, _, autotexts = self.ax.pie(
            sizes,
            colors=colors,
            startangle=140,
            autopct=lambda p: f"{p:.1f}%" if p >= 5 else "",
            pctdistance=0.78,
            wedgeprops=dict(linewidth=2, edgecolor=BG_CARD)
        )
        for at in autotexts:
            at.set_color("white")
            at.set_fontsize(7.5)
            at.set_fontweight("bold")

        # Legend to the right of the pie
        legend_labels = [f"{l}  ₹{v:,.0f}" for l, v in zip(labels, sizes)]
        patches = [mpatches.Patch(color=c, label=lb)
                   for c, lb in zip(colors, legend_labels)]
        self.ax.legend(
            handles=patches,
            loc="center left",
            bbox_to_anchor=(1.02, 0.5),
            fontsize=7.5,
            frameon=False,
            labelcolor=TEXT_PRIMARY
        )

        self.ax.set_title(
            "Expense Breakdown", color=TEXT_PRIMARY,
            fontsize=10, pad=4
        )
        self.canvas_widget.draw()


    def _refresh_title(self):
        """Keep the window title in sync with the transaction count."""
        n = len(self.transactions)
        self.title(f"💰 Personal Budget Tracker  —  {n} transaction{'s' if n != 1 else ''}")

    def _build_statusbar(self):
        """Thin status bar pinned to the bottom of the window."""
        self.statusbar = tk.Label(
            self, text="Ready — add your first transaction to get started.",
            font=("Segoe UI", 9), bg=BG_ENTRY, fg=TEXT_MUTED,
            anchor="w", padx=12, pady=4
        )
        self.statusbar.pack(fill="x", side="bottom")

    def _set_status(self, msg: str):
        """Update the status bar text."""
        self.statusbar.config(text=msg)


# =============================================================================
# Entry point
# =============================================================================

if __name__ == "__main__":
    app = BudgetTracker()
    app.mainloop()
