import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ==== 1. Motion classification thresholds ====
ACC_THRESHOLD_STILL = 0.2
ACC_THRESHOLD_SPIKE = 2.0
GYRO_THRESHOLD_TILT = 20.0

# ==== 2. Motion classification function ====
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

# ==== Streamlit UI ====

st.title("Motion Classification and Visualization")

uploaded_file = st.file_uploader("Upload CSV with columns: timestamp, AccX, AccY, AccZ, GyroX, GyroY, GyroZ", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    
    # Parse timestamp
    df['timestamp'] = pd.to_datetime(df['timestamp'], dayfirst=True, errors='coerce')
    if df['timestamp'].isnull().any():
        st.error("Error parsing timestamps. Check your timestamp format.")
    else:
        # Apply classification
        df['Label'] = df.apply(classify_motion, axis=1)
        
        st.success("Motion classification applied!")
        
        # Show a sample of the labeled data
        st.dataframe(df.head(20))
        
        # Dropdowns for motion and axis
        motions = df['Label'].unique().tolist()
        axes = ['AccX', 'AccY', 'AccZ']
        
        selected_motion = st.selectbox("Select Motion Label", motions)
        selected_axis = st.selectbox("Select Axis", axes)
        
        filtered_df = df[df['Label'] == selected_motion]
        
        if filtered_df.empty:
            st.warning(f"No data for motion '{selected_motion}'")
        else:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=filtered_df['timestamp'],
                y=filtered_df[selected_axis],
                mode='lines',
                name=f"{selected_motion} - {selected_axis}"
            ))
            fig.update_layout(
                title=f"Time Series for {selected_motion} ({selected_axis})",
                xaxis_title="Timestamp",
                yaxis_title="Sensor Value",
                height=400,
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Provide CSV download button
        csv_labeled = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download labeled CSV",
            data=csv_labeled,
            file_name="labeled_output.csv",
            mime="text/csv"
        )
else:
    st.info("Please upload a CSV file to start.")
