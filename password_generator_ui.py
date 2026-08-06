"""Modern Tkinter password generator.

This desktop application generates strong passwords with Python's standard
library only. Passwords are generated with the ``secrets`` module, which is
designed for security-sensitive random values.
"""

from __future__ import annotations

import secrets
import string
import tkinter as tk
from tkinter import ttk
from typing import Callable


MIN_LENGTH = 4
MAX_LENGTH = 128
DEFAULT_LENGTH = 16
MAX_HISTORY_ITEMS = 5

SIMILAR_CHARACTERS = set("0Ol1")


class PasswordGeneratorApp:
    """A beginner-friendly, polished Tkinter password generator."""

    def __init__(self, root: tk.Tk) -> None:
        """Initialize application state, styles, layout, and shortcuts."""
        self.root = root
        self.root.title("Secure Password Generator")
        self.root.geometry("820x720")
        self.root.minsize(620, 640)

        self.colors = {
            "background": "#0f172a",
            "panel": "#111827",
            "panel_light": "#1f2937",
            "text": "#f8fafc",
            "muted": "#94a3b8",
            "accent": "#38bdf8",
            "accent_hover": "#0ea5e9",
            "success": "#22c55e",
            "warning": "#f59e0b",
            "danger": "#ef4444",
            "input": "#020617",
            "border": "#334155",
        }

        self.fonts = {
            "title": ("Segoe UI", 24, "bold"),
            "heading": ("Segoe UI", 13, "bold"),
            "body": ("Segoe UI", 11),
            "small": ("Segoe UI", 10),
            "password": ("Consolas", 16, "bold"),
        }

        self.length_var = tk.IntVar(value=DEFAULT_LENGTH)
        self.length_text_var = tk.StringVar(value=str(DEFAULT_LENGTH))
        self.include_lowercase = tk.BooleanVar(value=True)
        self.include_uppercase = tk.BooleanVar(value=True)
        self.include_numbers = tk.BooleanVar(value=True)
        self.include_symbols = tk.BooleanVar(value=True)
        self.exclude_similar = tk.BooleanVar(value=False)
        self.show_password = tk.BooleanVar(value=True)
        self.password_var = tk.StringVar()
        self.status_var = tk.StringVar()
        self.strength_var = tk.StringVar(value="Strength: Medium")

        self.history: list[str] = []
        self.status_after_id: str | None = None
        self.is_syncing_length = False

        self._configure_styles()
        self._build_layout()
        self._bind_shortcuts()
        self._update_strength_indicator()

    def _configure_styles(self) -> None:
        """Configure ttk widgets to match the dark interface."""
        self.root.configure(bg=self.colors["background"])

        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "Horizontal.TScale",
            background=self.colors["panel"],
            troughcolor=self.colors["input"],
            bordercolor=self.colors["border"],
            lightcolor=self.colors["accent"],
            darkcolor=self.colors["accent"],
        )

    def _build_layout(self) -> None:
        """Create the responsive application layout."""
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        main_frame = tk.Frame(self.root, bg=self.colors["background"])
        main_frame.grid(row=0, column=0, sticky="nsew", padx=24, pady=24)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)

        self._build_header(main_frame)
        self._build_password_card(main_frame)
        self._build_options_card(main_frame)
        self._build_history_card(main_frame)
        self._build_status_bar(main_frame)

    def _build_header(self, parent: tk.Frame) -> None:
        """Build the title and project-style description."""
        header = tk.Frame(parent, bg=self.colors["background"])
        header.grid(row=0, column=0, sticky="ew", pady=(0, 18))
        header.columnconfigure(0, weight=1)

        title = tk.Label(
            header,
            text="Secure Password Generator",
            bg=self.colors["background"],
            fg=self.colors["text"],
            font=self.fonts["title"],
            anchor="w",
        )
        title.grid(row=0, column=0, sticky="ew")

        subtitle = tk.Label(
            header,
            text="A polished Tkinter desktop app using cryptographically secure randomness.",
            bg=self.colors["background"],
            fg=self.colors["muted"],
            font=self.fonts["body"],
            anchor="w",
        )
        subtitle.grid(row=1, column=0, sticky="ew", pady=(6, 0))

    def _build_password_card(self, parent: tk.Frame) -> None:
        """Build the generated password output, strength, and action buttons."""
        card = self._create_card(parent)
        card.grid(row=1, column=0, sticky="ew", pady=(0, 16))
        card.columnconfigure(0, weight=1)

        password_label = self._create_label(card, "Generated Password", "heading")
        password_label.grid(row=0, column=0, sticky="w", pady=(0, 8))

        password_row = tk.Frame(card, bg=self.colors["panel"])
        password_row.grid(row=1, column=0, sticky="ew")
        password_row.columnconfigure(0, weight=1)

        self.password_entry = tk.Entry(
            password_row,
            textvariable=self.password_var,
            font=self.fonts["password"],
            bg=self.colors["input"],
            fg=self.colors["text"],
            insertbackground=self.colors["text"],
            relief="flat",
            bd=0,
            readonlybackground=self.colors["input"],
            justify="center",
        )
        self.password_entry.grid(row=0, column=0, sticky="ew", ipady=12)

        show_check = self._create_checkbutton(
            password_row,
            text="Show",
            variable=self.show_password,
            command=self._toggle_password_visibility,
        )
        show_check.grid(row=0, column=1, padx=(12, 0), sticky="e")

        strength_frame = tk.Frame(card, bg=self.colors["panel"])
        strength_frame.grid(row=2, column=0, sticky="ew", pady=(14, 0))
        strength_frame.columnconfigure(0, weight=1)

        self.strength_label = self._create_label(strength_frame, "", "body")
        self.strength_label.configure(textvariable=self.strength_var)
        self.strength_label.grid(row=0, column=0, sticky="w")

        self.strength_bar = tk.Canvas(
            strength_frame,
            height=10,
            bg=self.colors["input"],
            highlightthickness=0,
            bd=0,
        )
        self.strength_bar.grid(row=1, column=0, sticky="ew", pady=(8, 0))
        self.strength_bar.bind("<Configure>", lambda _event: self._draw_strength_bar())

        button_row = tk.Frame(card, bg=self.colors["panel"])
        button_row.grid(row=3, column=0, sticky="ew", pady=(18, 0))
        button_row.columnconfigure((0, 1, 2), weight=1, uniform="buttons")

        self._create_button(
            button_row,
            "Generate Password",
            self.generate_password,
            variant="primary",
        ).grid(row=0, column=0, sticky="ew", padx=(0, 8))

        self._create_button(
            button_row,
            "Copy to Clipboard",
            self.copy_current_password,
        ).grid(row=0, column=1, sticky="ew", padx=8)

        self._create_button(
            button_row,
            "Clear",
            self.clear_password,
            variant="secondary",
        ).grid(row=0, column=2, sticky="ew", padx=(8, 0))

    def _build_options_card(self, parent: tk.Frame) -> None:
        """Build password length controls and character-type options."""
        card = self._create_card(parent)
        card.grid(row=2, column=0, sticky="ew", pady=(0, 16))
        card.columnconfigure(0, weight=1)

        title = self._create_label(card, "Password Options", "heading")
        title.grid(row=0, column=0, sticky="w", pady=(0, 12))

        length_frame = tk.Frame(card, bg=self.colors["panel"])
        length_frame.grid(row=1, column=0, sticky="ew")
        length_frame.columnconfigure(0, weight=1)

        length_label = self._create_label(length_frame, "Length", "body")
        length_label.grid(row=0, column=0, sticky="w", pady=(0, 8))

        self.length_slider = ttk.Scale(
            length_frame,
            from_=MIN_LENGTH,
            to=MAX_LENGTH,
            orient="horizontal",
            variable=self.length_var,
            command=self._on_slider_change,
            style="Horizontal.TScale",
        )
        self.length_slider.grid(row=1, column=0, sticky="ew", padx=(0, 12))

        self.length_entry = tk.Entry(
            length_frame,
            textvariable=self.length_text_var,
            font=self.fonts["body"],
            bg=self.colors["input"],
            fg=self.colors["text"],
            insertbackground=self.colors["text"],
            relief="flat",
            bd=0,
            justify="center",
            width=7,
        )
        self.length_entry.grid(row=1, column=1, sticky="e", ipady=8)
        self.length_entry.bind("<FocusOut>", self._on_length_entry_commit)
        self.length_entry.bind("<Return>", self._on_length_entry_return)
        self.length_text_var.trace_add("write", self._on_length_text_change)

        options_grid = tk.Frame(card, bg=self.colors["panel"])
        options_grid.grid(row=2, column=0, sticky="ew", pady=(18, 0))
        options_grid.columnconfigure((0, 1), weight=1)

        options: list[tuple[str, tk.BooleanVar]] = [
            ("Lowercase letters", self.include_lowercase),
            ("Uppercase letters", self.include_uppercase),
            ("Numbers", self.include_numbers),
            ("Symbols", self.include_symbols),
            ("Exclude similar characters", self.exclude_similar),
        ]

        for index, (text, variable) in enumerate(options):
            check = self._create_checkbutton(
                options_grid,
                text=text,
                variable=variable,
                command=self._update_strength_indicator,
            )
            check.grid(
                row=index // 2,
                column=index % 2,
                sticky="w",
                padx=(0, 16),
                pady=6,
            )

    def _build_history_card(self, parent: tk.Frame) -> None:
        """Build the session-only password history section."""
        card = self._create_card(parent)
        card.grid(row=3, column=0, sticky="nsew")
        card.columnconfigure(0, weight=1)
        card.rowconfigure(1, weight=1)

        header = tk.Frame(card, bg=self.colors["panel"])
        header.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        header.columnconfigure(0, weight=1)

        title = self._create_label(header, "Session History", "heading")
        title.grid(row=0, column=0, sticky="w")

        note = self._create_label(header, "Latest five passwords only", "small")
        note.configure(fg=self.colors["muted"])
        note.grid(row=0, column=1, sticky="e")

        self.history_frame = tk.Frame(card, bg=self.colors["panel"])
        self.history_frame.grid(row=1, column=0, sticky="nsew")
        self.history_frame.columnconfigure(0, weight=1)

        self._refresh_history()

    def _build_status_bar(self, parent: tk.Frame) -> None:
        """Build temporary status and validation message area."""
        self.status_label = tk.Label(
            parent,
            textvariable=self.status_var,
            bg=self.colors["background"],
            fg=self.colors["muted"],
            font=self.fonts["small"],
            anchor="w",
        )
        self.status_label.grid(row=4, column=0, sticky="ew", pady=(12, 0))

    def _create_card(self, parent: tk.Frame) -> tk.Frame:
        """Create a consistent dark panel container."""
        card = tk.Frame(
            parent,
            bg=self.colors["panel"],
            padx=18,
            pady=18,
            highlightbackground=self.colors["border"],
            highlightthickness=1,
        )
        return card

    def _create_label(self, parent: tk.Frame, text: str, font_key: str) -> tk.Label:
        """Create a consistently styled label."""
        return tk.Label(
            parent,
            text=text,
            bg=self.colors["panel"],
            fg=self.colors["text"],
            font=self.fonts[font_key],
            anchor="w",
        )

    def _create_checkbutton(
        self,
        parent: tk.Frame,
        text: str,
        variable: tk.BooleanVar,
        command: Callable[[], None] | None = None,
    ) -> tk.Checkbutton:
        """Create a dark themed checkbutton."""
        return tk.Checkbutton(
            parent,
            text=text,
            variable=variable,
            command=command,
            bg=self.colors["panel"],
            fg=self.colors["text"],
            activebackground=self.colors["panel"],
            activeforeground=self.colors["text"],
            selectcolor=self.colors["input"],
            font=self.fonts["body"],
            cursor="hand2",
            relief="flat",
        )

    def _create_button(
        self,
        parent: tk.Frame,
        text: str,
        command: Callable[[], None],
        variant: str = "default",
    ) -> tk.Button:
        """Create a button with a consistent portfolio-ready look."""
        background = self.colors["panel_light"]
        foreground = self.colors["text"]
        active_background = self.colors["border"]

        if variant == "primary":
            background = self.colors["accent"]
            foreground = "#031525"
            active_background = self.colors["accent_hover"]
        elif variant == "secondary":
            background = self.colors["input"]
            active_background = self.colors["border"]

        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=background,
            fg=foreground,
            activebackground=active_background,
            activeforeground=foreground,
            font=self.fonts["body"],
            relief="flat",
            bd=0,
            cursor="hand2",
            padx=14,
            pady=10,
        )

    def _bind_shortcuts(self) -> None:
        """Register app-wide keyboard shortcuts."""
        self.root.bind("<Return>", lambda _event: self.generate_password())
        self.root.bind("<Control-c>", lambda _event: self.copy_current_password())
        self.root.bind("<Control-C>", lambda _event: self.copy_current_password())
        self.root.bind("<Escape>", lambda _event: self.clear_password())

    def _on_slider_change(self, value: str) -> None:
        """Synchronize the numeric field when the slider moves."""
        if self.is_syncing_length:
            return

        self.is_syncing_length = True
        rounded_value = int(float(value))
        self.length_var.set(rounded_value)
        self.length_text_var.set(str(rounded_value))
        self.is_syncing_length = False
        self._update_strength_indicator()

    def _on_length_text_change(self, *_args: object) -> None:
        """Synchronize the slider while the numeric entry contains a valid value."""
        if self.is_syncing_length:
            return

        text = self.length_text_var.get().strip()
        if not text.isdigit():
            return

        value = int(text)
        if MIN_LENGTH <= value <= MAX_LENGTH:
            self.is_syncing_length = True
            self.length_var.set(value)
            self.is_syncing_length = False
            self._update_strength_indicator()

    def _on_length_entry_commit(self, _event: tk.Event | None = None) -> None:
        """Validate and normalize the numeric length field."""
        try:
            value = self._get_valid_length()
        except ValueError as error:
            self._show_status(str(error), "error")
            value = self.length_var.get()

        self.is_syncing_length = True
        self.length_var.set(value)
        self.length_text_var.set(str(value))
        self.is_syncing_length = False
        self._update_strength_indicator()

    def _on_length_entry_return(self, _event: tk.Event | None = None) -> str:
        """Validate length and generate when Enter is pressed in the input field."""
        try:
            self._get_valid_length()
        except ValueError as error:
            self._show_status(str(error), "error")
            self._on_length_entry_commit()
            return "break"

        self._on_length_entry_commit()
        self.generate_password()
        return "break"

    def _get_valid_length(self) -> int:
        """Return a validated password length from the numeric input."""
        text = self.length_text_var.get().strip()

        if not text:
            raise ValueError("Please enter a password length.")

        if not text.isdigit():
            raise ValueError("Password length must be a whole number.")

        length = int(text)

        if length < MIN_LENGTH or length > MAX_LENGTH:
            raise ValueError(
                f"Password length must be between {MIN_LENGTH} and {MAX_LENGTH}."
            )

        return length

    def _get_selected_character_sets(self) -> list[str]:
        """Return character pools selected by the user."""
        character_sets: list[str] = []

        if self.include_lowercase.get():
            character_sets.append(string.ascii_lowercase)
        if self.include_uppercase.get():
            character_sets.append(string.ascii_uppercase)
        if self.include_numbers.get():
            character_sets.append(string.digits)
        if self.include_symbols.get():
            character_sets.append(string.punctuation)

        if self.exclude_similar.get():
            character_sets = [
                "".join(char for char in group if char not in SIMILAR_CHARACTERS)
                for group in character_sets
            ]

        return [group for group in character_sets if group]

    def _get_password_pool(self, character_sets: list[str]) -> str:
        """Combine selected character sets into one password pool."""
        return "".join(character_sets)

    def generate_password(self) -> None:
        """Generate a secure password that includes every selected type."""
        try:
            length = self._get_valid_length()
            character_sets = self._get_selected_character_sets()

            if not character_sets:
                raise ValueError("Select at least one character type.")

            if length < len(character_sets):
                raise ValueError(
                    "Length is too short for every selected character type."
                )

            password = self._build_password(length, character_sets)
        except ValueError as error:
            self._show_status(str(error), "error")
            return
        except tk.TclError:
            self._show_status("Unable to update the app window. Please try again.", "error")
            return

        self.password_var.set(password)
        self._add_to_history(password)
        self._update_password_entry_state()
        self._update_strength_indicator(password)
        self._show_status("Password generated successfully.", "success")

    def _build_password(self, length: int, character_sets: list[str]) -> str:
        """Build a password with at least one character from each selected set."""
        password_chars = [secrets.choice(group) for group in character_sets]
        password_pool = self._get_password_pool(character_sets)

        remaining_length = length - len(password_chars)
        password_chars.extend(
            secrets.choice(password_pool) for _ in range(remaining_length)
        )

        secure_random = secrets.SystemRandom()
        secure_random.shuffle(password_chars)

        return "".join(password_chars)

    def copy_current_password(self) -> None:
        """Copy the generated password without showing a popup."""
        password = self.password_var.get()

        if not password:
            self._show_status("Generate a password before copying.", "error")
            return

        self._copy_to_clipboard(password)

    def _copy_history_password(self, password: str) -> None:
        """Copy a password from the in-memory session history."""
        self._copy_to_clipboard(password)

    def _copy_to_clipboard(self, password: str) -> None:
        """Copy text to the system clipboard with friendly error handling."""
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(password)
            self.root.update_idletasks()
        except tk.TclError:
            self._show_status("Unable to access the clipboard.", "error")
            return

        self._show_status("Copied successfully.", "success", temporary=True)

    def clear_password(self) -> None:
        """Clear the current password and validation messages."""
        self.password_var.set("")
        self._update_password_entry_state()
        self._update_strength_indicator()
        self._show_status("Cleared.", "info", temporary=True)

    def _toggle_password_visibility(self) -> None:
        """Show or mask the generated password field."""
        self._update_password_entry_state()

    def _update_password_entry_state(self) -> None:
        """Apply masking based on the Show Password option."""
        self.password_entry.configure(show="" if self.show_password.get() else "*")

    def _add_to_history(self, password: str) -> None:
        """Store only the latest five generated passwords for this session."""
        if password in self.history:
            self.history.remove(password)

        self.history.insert(0, password)
        self.history = self.history[:MAX_HISTORY_ITEMS]
        self._refresh_history()

    def _refresh_history(self) -> None:
        """Refresh the password history rows."""
        for widget in self.history_frame.winfo_children():
            widget.destroy()

        if not self.history:
            empty_label = self._create_label(
                self.history_frame,
                "Generated passwords will appear here for this session.",
                "body",
            )
            empty_label.configure(fg=self.colors["muted"])
            empty_label.grid(row=0, column=0, sticky="w", pady=8)
            return

        for index, password in enumerate(self.history):
            row = tk.Frame(
                self.history_frame,
                bg=self.colors["input"],
                highlightbackground=self.colors["border"],
                highlightthickness=1,
            )
            row.grid(row=index, column=0, sticky="ew", pady=4)
            row.columnconfigure(0, weight=1)

            password_label = tk.Entry(
                row,
                bg=self.colors["input"],
                fg=self.colors["text"],
                readonlybackground=self.colors["input"],
                font=("Consolas", 11),
                relief="flat",
                bd=0,
            )
            password_label.insert(0, password)
            password_label.configure(state="readonly")
            password_label.grid(row=0, column=0, sticky="ew", padx=12, pady=9)

            copy_button = self._create_button(
                row,
                "Copy",
                lambda value=password: self._copy_history_password(value),
                variant="secondary",
            )
            copy_button.grid(row=0, column=1, sticky="e", padx=8, pady=6)

    def _estimate_strength(self, password: str | None = None) -> tuple[str, str, float]:
        """Estimate password strength from length and selected character variety."""
        if password is None:
            try:
                length = self._get_valid_length()
            except ValueError:
                length = self.length_var.get()
            character_sets = self._get_selected_character_sets()
        else:
            length = len(password)
            character_sets = self._detect_character_sets(password)

        character_pool_size = len(self._get_password_pool(character_sets))
        type_count = len(character_sets)

        if character_pool_size == 0:
            return ("Weak", self.colors["danger"], 0.15)

        score = 0

        if length >= 8:
            score += 1
        if length >= 12:
            score += 1
        if length >= 16:
            score += 1
        if length >= 24:
            score += 1

        if type_count >= 2:
            score += 1
        if type_count >= 3:
            score += 1
        if type_count >= 4:
            score += 1

        if character_pool_size >= 60:
            score += 1

        if score <= 2:
            return ("Weak", self.colors["danger"], 0.25)
        if score <= 4:
            return ("Medium", self.colors["warning"], 0.50)
        if score <= 6:
            return ("Strong", self.colors["accent"], 0.75)
        return ("Very Strong", self.colors["success"], 1.0)

    def _detect_character_sets(self, password: str) -> list[str]:
        """Detect which character types appear in a generated password."""
        detected_sets: list[str] = []

        if any(char in string.ascii_lowercase for char in password):
            detected_sets.append(string.ascii_lowercase)
        if any(char in string.ascii_uppercase for char in password):
            detected_sets.append(string.ascii_uppercase)
        if any(char in string.digits for char in password):
            detected_sets.append(string.digits)
        if any(char in string.punctuation for char in password):
            detected_sets.append(string.punctuation)

        return detected_sets

    def _update_strength_indicator(self, password: str | None = None) -> None:
        """Update strength text and progress bar color."""
        label, color, _ratio = self._estimate_strength(password)
        self.strength_var.set(f"Strength: {label}")
        self.strength_label.configure(fg=color)
        self._draw_strength_bar()

    def _draw_strength_bar(self) -> None:
        """Draw a simple responsive strength bar on the canvas."""
        label, color, ratio = self._estimate_strength(self.password_var.get() or None)

        self.strength_bar.delete("all")
        width = max(self.strength_bar.winfo_width(), 1)
        height = max(self.strength_bar.winfo_height(), 1)

        self.strength_bar.create_rectangle(
            0,
            0,
            width,
            height,
            fill=self.colors["input"],
            outline="",
        )
        self.strength_bar.create_rectangle(
            0,
            0,
            int(width * ratio),
            height,
            fill=color,
            outline="",
        )
        self.strength_var.set(f"Strength: {label}")

    def _show_status(
        self,
        message: str,
        level: str = "info",
        temporary: bool = False,
    ) -> None:
        """Show a friendly status message below the app."""
        if self.status_after_id is not None:
            self.root.after_cancel(self.status_after_id)
            self.status_after_id = None

        color = self.colors["muted"]
        if level == "success":
            color = self.colors["success"]
        elif level == "error":
            color = self.colors["danger"]

        self.status_label.configure(fg=color)
        self.status_var.set(message)

        if temporary:
            self.status_after_id = self.root.after(2200, self._clear_status)

    def _clear_status(self) -> None:
        """Clear temporary status messages."""
        self.status_var.set("")
        self.status_after_id = None


def main() -> None:
    """Start the Tkinter password generator application."""
    root = tk.Tk()
    PasswordGeneratorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
