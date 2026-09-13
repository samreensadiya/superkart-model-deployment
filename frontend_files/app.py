import streamlit as st
import pandas as pd
import requests
import os

st.set_page_config(page_title="SuperKart Sales Prediction", layout="wide")
st.title("SuperKart Sales Prediction App")

# Environment-aware URL configuration (defaults to Docker network bridge)
API_BASE_URL = os.getenv("API_BASE_URL", "http://172.17.0.1:7860")

# -------------------------------------------------------------------
# Section 1: Single Product Online Prediction
# -------------------------------------------------------------------
st.subheader("Single Product Sales Prediction")

col1, col2 = st.columns(2)

with col1:
    Product_Weight = st.number_input("Product Weight", min_value=0.0, value=12.66)
    Product_Sugar_Content = st.selectbox("Product Sugar Content", ["Low Sugar", "Regular", "No Sugar"])
    Product_Allocated_Area = st.number_input("Product Allocated Area", min_value=0.0, value=50.0)
    Product_MRP = st.number_input("Product MRP", min_value=0.0, value=100.0)
    Store_Size = st.selectbox("Store Size", ["Small", "Medium", "High"])

with col2:
    Store_Location_City_Type = st.selectbox("Store Location City Type", ["Tier 1", "Tier 2", "Tier 3"])
    Store_Type = st.selectbox("Store Type", ["Type 1", "Type 2", "Type 3", "Type 4"])
    Product_Id_char = st.text_input("Product Id Char", value="P001")
    Store_Age_Years = st.number_input("Store Age Years", min_value=0, value=10)
    Product_Type_Category = st.selectbox("Product Type Category", ["Category 1", "Category 2", "Category 3"])

product_data = {
    "Product_Weight": Product_Weight,
    "Product_Sugar_Content": Product_Sugar_Content,
    "Product_Allocated_Area": Product_Allocated_Area,
    "Product_MRP": Product_MRP,
    "Store_Size": Store_Size,
    "Store_Location_City_Type": Store_Location_City_Type,
    "Store_Type": Store_Type,
    "Product_Id_char": Product_Id_char,
    "Store_Age_Years": Store_Age_Years,
    "Product_Type_Category": Product_Type_Category
}

if st.button("Predict Sales", type='primary'):
    try:
        response = requests.post(f"{API_BASE_URL}/v1/predict", json=product_data)
        if response.status_code == 200:
            result = response.json()
            predicted_sales = result.get("Predicted_Sales", result.get("Sales", 0.0))
            st.success(f"Predicted Product Store Sales Total: ₹{predicted_sales:.2f}")
        else:
            st.error(f"Error {response.status_code}: {response.text}")
    except Exception as e:
        st.error(f"Failed to connect to API ({API_BASE_URL}): {e}")

# -------------------------------------------------------------------
# Section 2: Batch Sales Prediction
# -------------------------------------------------------------------
st.divider()
st.subheader("Batch Sales Prediction")

uploaded_file = st.file_uploader("Upload CSV file for batch prediction", type=["csv"])

if uploaded_file is not None:
    if st.button("Predict Batch", type="primary"):
        with st.spinner("Processing batch predictions..."):
            try:
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "text/csv")}
                response = requests.post(f"{API_BASE_URL}/v1/batch_predict", files=files)
                
                if response.status_code == 200:
                    batch_result = response.json()
                    predictions_list = batch_result.get("predictions", [])
                    
                    if predictions_list:
                        batch_df = pd.DataFrame(predictions_list)
                        st.success(f"Successfully generated predictions for {len(batch_df)} records!")
                        st.dataframe(batch_df, use_container_width=True)
                        
                        csv_data = batch_df.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            label="Download Batch Predictions CSV",
                            data=csv_data,
                            file_name="superkart_batch_predictions.csv",
                            mime="text/csv"
                        )
                    else:
                        st.warning("API responded successfully, but returned 0 records.")
                else:
                    st.error(f"Batch API Error {response.status_code}: {response.text}")
            except Exception as e:
                st.error(f"Failed to process batch request: {e}")