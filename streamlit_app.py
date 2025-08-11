import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.title("Motion Data Viewer with Plotly Dropdowns")

uploaded_file = st.file_uploader("Upload CSV with timestamp, AccX, AccY, AccZ, Label columns", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    df['timestamp'] = pd.to_datetime(df['timestamp'], dayfirst=True)
    
    axes = ['AccX', 'AccY', 'AccZ']
    motions = df['Label'].unique()
    
    # Default filter
    default_motion = motions[0]
    default_axis = axes[0]
    filtered_df = df[df['Label'] == default_motion]

    fig = go.Figure()

    # Initial trace
    fig.add_trace(go.Scatter(
        x=filtered_df['timestamp'],
        y=filtered_df[default_axis],
        mode='lines',
        name=f"{default_motion} - {default_axis}"
    ))

    # Dropdown buttons for motion
    motion_buttons = [
        dict(
            label=motion,
            method="update",
            args=[
                {
                    "x": [df[df['Label'] == motion]['timestamp']],
                    "y": [df[df['Label'] == motion][default_axis]],
                    "name": f"{motion} - {default_axis}"
                }
            ]
        )
        for motion in motions
    ]

    # Dropdown buttons for axis
    axis_buttons = [
        dict(
            label=axis,
            method="update",
            args=[
                {
                    "y": [df[df['Label'] == default_motion][axis]],
                    "name": f"{default_motion} - {axis}"
                }
            ]
        )
        for axis in axes
    ]

    fig.update_layout(
        updatemenus=[
            dict(
                buttons=motion_buttons,
                direction="down",
                x=0,
                xanchor="left",
                y=1.1,
                yanchor="top",
                showactive=True,
                pad={"r": 10, "t": 10},
                name="Select Motion"
            ),
            dict(
                buttons=axis_buttons,
                direction="down",
                x=0.25,
                xanchor="left",
                y=1.1,
                yanchor="top",
                showactive=True,
                pad={"r": 10, "t": 10},
                name="Select Axis"
            )
        ],
        title="Motion Data Viewer",
        xaxis_title="Timestamp",
        yaxis_title="Sensor Value",
        height=500,
        margin=dict(t=80)
    )
    
    st.plotly_chart(fig, use_container_width=True)
