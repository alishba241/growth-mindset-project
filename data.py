import streamlit as st
import pandas as pd
import plotly.express as px
import io

# ** Custom designing

st.markdown("""
    <style>
        /* Background Gradient */
        .stApp {
           background: linear-gradient(to right, pink, wheat);
            color: black;
            font-family: 'Arial', sans-serif;
        }
         /* File uploader background white */
    div[data-testid="stFileUploader"] {
        background: white !important;
        border-radius: 10px !important;
        padding: 10px !important;
        box-shadow: 0px 0px 5px rgba(0, 0, 0, 0.2) !important;
    }
            div[data-testid="stFileUploader"] * {
        color: black !important;
    }

        /* Buttons Gradient */
        .stButton>button {
            background: linear-gradient(45deg, purple, #00ccff) !important;
            color: white !important;
            border-radius: 8px !important;
            font-size: 16px !important;
            border: none !important;
            padding: 10px 20px !important;
        }

        /* Scrollbar Customization */
        ::-webkit-scrollbar {
            width: 10px;
        }
        ::-webkit-scrollbar-thumb {
            background: #00ffcc;
            border-radius: 10px;
        }
    </style>
""", unsafe_allow_html=True)

# ** App Title

st.title("⚡ Data Sweeper - Clean & Visualize Your Data")

# ** upload file

upload_file = st.file_uploader("Upload your dataset", type=["csv", "xlsx", "json", "txt"])

# ** processing data
@st.cache_resource
def load_data(file):
    file_extension = file.name.split(".")[-1]
    
    if file_extension == "csv":
        df = pd.read_csv(file)
    elif file_extension == "xlsx":
        df = pd.read_excel(file)
    elif file_extension == "json":
        df = pd.read_json(file)
    elif file_extension == "txt":
        df = pd.read_csv(file, delimiter="\t")
    else:
        return None
    return df

if upload_file:
    df = load_data(upload_file)
    
    if df is None:
        st.error("Unsupported file format!")
        st.stop()

    # ** File Information 
    st.subheader("📂 File Information")
    st.write(f"**File Name:** {upload_file.name}")
    st.write(f"**File Type:** {upload_file.type}")
    st.write(f"**File Size:** {upload_file.size / 1024:.2f} KB")
    st.write(f"**Rows:** {df.shape[0]} | **Columns:** {df.shape[1]}")

    # ** Raw Data Preview
    st.subheader("📋 Raw Data Preview")
    st.write(df.head())

    # ** Data Cleaning
    cleaned_df = df.copy()

    # ** Column Renaming
    st.subheader("✏️ Rename Columns")
    new_column_names = {
        col: st.text_input(f'Rename `{col}`', col) for col in cleaned_df.columns
        }
    cleaned_df.rename(columns=new_column_names, inplace=True)

    # **Cleaning Options
    if st.button("Remove Missing Values"):
        cleaned_df = cleaned_df.dropna()
        st.success("✅ Missing values removed!")

    if st.button("Remove Duplicates"):
        cleaned_df = cleaned_df.drop_duplicates()
        st.success("✅ Duplicate rows removed!")

    # ** Filtering Columns
    selected_columns = st.multiselect(
        "Select Columns to Keep", 
        cleaned_df.columns, 
        default=cleaned_df.columns.tolist()
        )
    cleaned_df = cleaned_df[selected_columns]

    # ** Convert Text Columns to Lowercase
    for col in cleaned_df.select_dtypes(include=['object']).columns:
        if st.checkbox(f"Convert `{col}` to Lowercase"):
            cleaned_df[col] = cleaned_df[col].str.lower()

    # ** Display Cleaned Data
    st.subheader("🔍 Preview Cleaned Data")
    st.dataframe(cleaned_df)

    # ** Data Statistics
    st.subheader("📊 Data Statistics")
    st.write(cleaned_df.describe())

   # ** Data visualization
    st.subheader("📊 Data visualization")

    numeric_cols = df.select_dtypes(include=['int', 'float']).columns.tolist()

    if numeric_cols:
        x_col = st.selectbox("Select X-axis Column", df.columns, key="x_col")
        y_col = st.selectbox("Select Y-axis Column", numeric_cols, key="y_col")

        if st.button("Generate Interactive Chart"):
            fig = px.bar(df, x=x_col, y=y_col, color=x_col, title=f"{x_col} vs {y_col}")
            fig.update_layout(template="plotly_dark", width=800, height=500)  
            st.plotly_chart(fig, use_container_width=True)

    else:
        st.warning("⚠️ No numeric columns available for visualization.")

    # ** Download Cleaned Data
    st.subheader("📩 Download Cleaned Data")
    
    # ** Convert DataFrame to CSV
    csv_data = cleaned_df.to_csv(index=False).encode()

    # ** Convert DataFrame to Excel
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
        cleaned_df.to_excel(writer, index=False, sheet_name="Cleaned Data")
    excel_data = excel_buffer.getvalue()

    # ** Download Buttons
    col1, col2 = st.columns(2)

    # ** Download in CSV format
    with col1:
        st.download_button(
            label="Download CSV",
            data=csv_data,
            file_name="cleaned_data.csv",
            mime="text/csv"
        )

         # ** Download in xlsx format
    with col2:
        st.download_button(
            label="Download Excel",
            data=excel_data,
            file_name="cleaned_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
