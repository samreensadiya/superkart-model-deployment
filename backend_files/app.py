import numpy as np
import joblib
import pandas as pd
from flask import Flask, request, jsonify

superkart_api = Flask("SuperKartSalesAPI")

# Load model
model = joblib.load("xgb_tuned_model.joblib")

@superkart_api.get('/')
def home():
    return "Welcome to the SuperKart Sales Prediction API!"

@superkart_api.post('/v1/predict')
def predict_sales():
    data = request.get_json()

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

    input_data = pd.DataFrame([sample])
    prediction = model.predict(input_data).tolist()[0]

    return jsonify({'Predicted_Sales': round(float(prediction), 2)})

@superkart_api.post('/v1/batch_predict')
def predict_batch_sales():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded. Please send a CSV file under the key "file".'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected.'}), 400

    try:
        input_df = pd.read_csv(file)
        
        required_features = [
            'Product_Weight', 'Product_Sugar_Content', 'Product_Allocated_Area',
            'Product_MRP', 'Store_Size', 'Store_Location_City_Type',
            'Store_Type', 'Product_Id_char', 'Store_Age_Years', 'Product_Type_Category'
        ]
        
        feature_df = input_df[required_features]
        predictions = model.predict(feature_df).tolist()
        rounded_predictions = [round(float(p), 2) for p in predictions]
        
        output_df = input_df.copy()
        output_df['Predicted_Sales'] = rounded_predictions

        return jsonify({
            'total_records': len(rounded_predictions),
            'predictions': output_df.to_dict(orient='records')
        })

    except KeyError as missing_col:
        return jsonify({'error': f'Missing required feature column: {missing_col}'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    superkart_api.run(host='0.0.0.0', port=7860, debug=True)