import plotly.graph_objs as go
from plotly.subplots import make_subplots
import pandas as pd
import plotly.io as pio

import mysql.connector
import pandas as pd
from io import BytesIO
import os
import json

pio.renderers.default = "browser"

def load_db_config(path="db_config.json"):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(base_dir, path)
    with open(full_path, "r") as f:
        return json.load(f)


SIGNALS = [
    "ram_psi_actual",
    "ram_position",
    "kwh_actual",
    "material_temp_actual",
    "chamber_temp_actual",
    "rotor_temp_actual"
]

COLOR_POOL = [
    "#1f77b4",  # blue
    "#ff7f0e",  # orange
    "#2ca02c",  # green
    "#d62728",  # red
    "#9467bd",  # purple
    "#8c564b",  # brown
    "#e377c2",  # pink
    "#7f7f7f",  # gray
    "#bcbd22",  # olive
    "#17becf",  # cyan
    "#aec7e8",  # light blue
    "#ffbb78",  # light orange
    "#98df8a",  # light green
    "#ff9896",  # light red
    "#c5b0d5",  # light purple
    "#c49c94",  # light brown
    "#f7b6d2",  # light pink
    "#c7c7c7",  # light gray
    "#dbdb8d",  # light olive
    "#9edae5",  # light cyan
    "#393b79",  # dark navy
    "#637939",  # olive green
    "#8c6d31",  # golden brown
    "#843c39",  # dark red
    "#7b4173",  # plum
    "#17bebb",  # teal
    "#f29e4c",  # peach
    "#e15759",  # coral red
    "#76b7b2",  # turquoise
    "#59a14f"   # forest green
]

def build_dynamic_title(df):
    programs = sorted(df["program"].dropna().unique())
    dates = pd.to_datetime(df["date"].dropna().unique())

    # Build program (compound) string
    if len(programs) == 1:
        program_part = programs[0]
    elif len(programs) <= 3:
        program_part = ", ".join(programs)
    else:
        program_part = f"{len(programs)} Compounds"

    # Build date string
    if len(dates) == 0:
        date_part = ""
    elif len(dates) == 1:
        date_part = f"on {dates[0].date()}"
    else:
        years = sorted(set(date.year for date in dates))
        if len(years) == 1:
            date_range = f"{min(dates).date()} to {max(dates).date()}"
            date_part = f"from {date_range}"
        else:
            date_part = f"from {min(years)} to {max(years)}"

    return f"Mixer Data Analysis: {program_part} {date_part}".strip()

def prettify(name):
    return name.replace("_", " ").title()

def format_timestamp(group):
    date_col = "date_x" if "date_x" in group.columns else "date"
    time_col = "time_x" if "time_x" in group.columns else "time"

    date_val = group[date_col].iloc[0] if date_col in group.columns else ""
    time_val = group[time_col].iloc[0] if time_col in group.columns else ""

    if pd.api.types.is_timedelta64_dtype(time_val):
        total_seconds = time_val.total_seconds()
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        seconds = int(total_seconds % 60)
        time_str = f"{hours:02}:{minutes:02}:{seconds:02}"
    else:
        time_str = str(time_val)

    return f"{date_val} {time_str}"


def add_signal_trace(fig, group, signal, label, color, row, col, timestamp):
    fig.add_trace(
        go.Scatter(
            x=group["elapsed_batch_time"],
            y=group[signal],
            mode="lines",
            name=f"{label}",
            line=dict(color=color),
            legendgroup=str(label),
            showlegend=(row == 1 and col == 1),
            customdata=[[str(label)]] * len(group),
            hovertemplate=(
                f"<b>{prettify(signal)}</b><br>"
                "%{customdata[0]}<br>"  # Already includes program, batch, and timestamp
                "Time: %{x}<br>"
                "Value: %{y}<extra></extra>"
            ),
        ),
        row=row, col=col
    )

def plot_all_signals_db(df):
    df.columns = df.columns.astype(str).str.strip().str.lower()

    fig = make_subplots(
        rows=2,
        cols=3,
        subplot_titles=[prettify(s) for s in SIGNALS],
        shared_xaxes=False
    )

    if "id_summary" in df.columns:
        groups = df.groupby("id_summary")
    else:
        groups = [(None, df)]

    for idx, (label, group) in enumerate(groups):
        color = COLOR_POOL[idx % len(COLOR_POOL)]
        batch = group["batch"].iloc[0] if "batch" in group.columns else "Unknown"
        program = group["program"].iloc[0] if "program" in group.columns else "Unknown Program"
        timestamp = format_timestamp(group)

        # Combine into a descriptive label
        batch_label = f"{program} | {batch} | {timestamp}"


        for i, signal in enumerate(SIGNALS):
            if signal not in group.columns:
                continue

            row = (i // 3) + 1
            col = (i % 3) + 1

            add_signal_trace(
                fig=fig,
                group=group,
                signal=signal,
                label=batch_label,
                color=color,
                row=row,
                col=col,
                timestamp=timestamp
            )

    fig.update_layout(
        height=900,
        width=1400,
        title_text=build_dynamic_title(df),
        legend_title="Batch ID",
        hovermode="closest",
        dragmode="zoom",
        clickmode='event+select',
        legend=dict(itemclick="toggle", itemdoubleclick="toggleothers"),
        margin=dict(t=80, l=40, r=40, b=40),
        updatemenus=[
            dict(
                type="buttons",
                showactive=False,
                buttons=[dict(label="Reset Zoom", method="relayout", args=[{"xaxis.autorange": True}])],
                x=1.05, xanchor="right", y=1.1, yanchor="top"
            )
        ]
    )

    #fig.show()
    return fig

def plot_all_signals_html(df):
    fig = plot_all_signals_db(df)
    return pio.to_html(fig, full_html=False)