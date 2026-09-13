
# Import necessary libraries
import numpy as np
import joblib  # For loading the serialized model
import pandas as pd  # For data manipulation
from flask import Flask, request, jsonify  # For creating the Flask API

# Initialize Flask app with a name
superkart_api = Flask("SuperKartSalesAPI")

# Load the trained churn prediction model
# model = joblib.load("backend_files/xgb_tuned_model.joblib")
model = joblib.load("xgb_tuned_model.joblib")
# Define a route for the home page
@superkart_api.get('/')
def home():
    return "Welcome to the SuperKart Sales Prediction API!"

# Define an endpoint to predict churn for a single customer
@superkart_api.post('/v1/predict')
def predict_sales():
    # Get JSON data from the request
    data = request.get_json()

    # Extract relevant customer features from the input data. The order of the column names matters.
    sample = {
        'Product_Weight': data['Product_Weight'],
        'Product_Sugar_Content': data['Product_Sugar_Content'],
        'Product_Allocated_Area': data['Product_Allocated_Area'],
        'Product_MRP': data['Product_MRP'],
        'Store_Size': data['Store_Size'],
        'Store_Location_City_Type': data['Store_Location_City_Type'],
        'Store_Type': data['Store_Type'],
        'Product_Id_char': data['Product_Id_char'],
        'Store_Age_Years': data['Store_Age_Years'],
        'Product_Type_Category': data['Product_Type_Category']
    }

    # Convert the extracted data into a DataFrame
    input_data = pd.DataFrame([sample])

    # Make a churn prediction using the trained model
    prediction = model.predict(input_data).tolist()[0]

    # Return the prediction as a JSON response
    return jsonify({'Sales': prediction})

# Endpoint for batch inference accepting a CSV file
@superkart_api.post('/v1/predictbatch')
def predict_batch_sales():
    # Check if a file was included in the request
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded. Please send a CSV file under the key "file".'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No file selected.'}), 400

    try:
        # Read the uploaded CSV file into a DataFrame
        input_df = pd.read_csv(file)

        # Required features expected by the model
        required_features = [
            'Product_Weight', 'Product_Sugar_Content', 'Product_Allocated_Area',
            'Product_MRP', 'Store_Size', 'Store_Location_City_Type',
            'Store_Type', 'Product_Id_char', 'Store_Age_Years', 'Product_Type_Category'
        ]

        # Select and preserve feature order
        feature_df = input_df[required_features]

        # Generate batch predictions
        predictions = model.predict(feature_df).tolist()
        rounded_predictions = [round(float(p), 2) for p in predictions]

        # Append predictions to the input dataframe for full contextual output
        output_df = input_df.copy()
        output_df['Predicted_Sales'] = rounded_predictions

        # Return predictions as JSON records
        return jsonify({
            'total_records': len(rounded_predictions),
            'predictions': output_df.to_dict(orient='records')
        })

    except KeyError as missing_col:
        return jsonify({'error': f'Missing required feature column: {missing_col}'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Run the Flask app in debug mode
if __name__ == '__main__':
    superkart_api.run(debug=True)
