import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Thresholds for classification
ACC_THRESHOLD_STILL = 0.2
ACC_THRESHOLD_SPIKE = 2.0
GYRO_THRESHOLD_TILT = 20.0

def classify_motion(row):
    ax, ay, az = row['AccX'], row['AccY'], row['AccZ']
    gx, gy, gz = row['GyroX'], row['GyroY'], row['GyroZ']

    if abs(ax) < ACC_THRESHOLD_STILL and abs(ay) < ACC_THRESHOLD_STILL and abs(az) < ACC_THRESHOLD_STILL:
        return "Still"
    if az > ACC_THRESHOLD_SPIKE:
        return "Throw (+Z)"
    if az < -ACC_THRESHOLD_SPIKE:
        return "Drop (-Z)"
    if abs(ax) > ACC_THRESHOLD_SPIKE or abs(ay) > ACC_THRESHOLD_SPIKE:
        return "Slide (±XY)"
    if abs(gx) > GYRO_THRESHOLD_TILT or abs(gy) > GYRO_THRESHOLD_TILT or abs(gz) > GYRO_THRESHOLD_TILT:
        return "Tilt"
    return "Misc"

st.title("Motion Labeling and Viewer")

uploaded_file = st.file_uploader("Upload CSV with columns: timestamp, AccX, AccY, AccZ, GyroX, GyroY, GyroZ", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    df['timestamp'] = pd.to_datetime(df['timestamp'], dayfirst=True, errors='coerce')

    if df['timestamp'].isnull().any():
        st.error("Timestamp parsing failed. Check your CSV date format.")
    else:
        # Apply labeling
        df['Label'] = df.apply(classify_motion, axis=1)
        st.success("Motion labeling complete!")

        st.dataframe(df.head(20))

        axes = ['AccX', 'AccY', 'AccZ']
        motions = df['Label'].unique()

        default_motion = motions[0]
        default_axis = axes[0]
        filtered_df = df[df['Label'] == default_motion]

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=filtered_df['timestamp'],
            y=filtered_df[default_axis],
            mode='lines',
            name=f"{default_motion} - {default_axis}"
        ))

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
                )
            ],
            title="Motion Data Viewer",
            xaxis_title="Timestamp",
            yaxis_title="Sensor Value",
            height=500,
            margin=dict(t=80)
        )

        st.plotly_chart(fig, use_container_width=True)

        # Download labeled CSV
        csv_labeled = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download labeled CSV",
            data=csv_labeled,
            file_name="labeled_output.csv",
            mime="text/csv"
        )

else:
    st.info("Please upload a CSV file to begin.")
