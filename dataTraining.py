import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from flask import Flask, jsonify, request

app = Flask(__name__)

file_path = 'master_data.csv'
master_data = pd.read_csv(file_path)

features = master_data[['brand', 'model', 'model_year', 'mileage']].dropna()
target = master_data['list_price'][features.index]

# One-hot encode categorical features
features_encoded = pd.get_dummies(features)

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(features_encoded, target, test_size=0.2, random_state=42)

# Model training
rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
rf_model.fit(X_train, y_train)

# Function to predict the price
def predict_price(model_year, brand, model, mileage, trained_model, training_features):
    # Initialize input data with zeros for all features
    input_data = pd.DataFrame(columns=training_features.columns)
    input_data.loc[0] = 0
    # Set the values for the input data
    input_data['model_year'] = model_year
    input_data['mileage'] = mileage
    input_data[f'brand_{brand}'] = 1
    input_data[f'model_{model}'] = 1
    # Predict the price using the trained model
    predicted_price = trained_model.predict(input_data)
    return predicted_price[0]

# Flask web server routes
app = Flask(__name__, static_url_path='', static_folder='/Users/lokitha/Desktop/vehiclePriceEstimation/website')

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Print statements to log data received
        data = request.form
        print("Form data received:", data)

        # Convert form data to the correct data types
        model_year = int(data['year'])
        brand = data['make']
        model = data['model']
        mileage = int(data['mileage'])

        average_price = float(target.mean())
        lowest_price = float(target.min())
        highest_price = float(target.max())

        # Logging the values before prediction
        print(f"Predicting price for {model_year} {brand} {model} with {mileage} mileage.")

        # Predict the price and print the prediction
        prediction = predict_price(model_year, brand, model, mileage, rf_model, X_train)
        print(f"Prediction: {prediction}")

        # Return the prediction in a JSON response
        return jsonify({
            'prediction': float(prediction),
            'averagePrice': average_price,
            'lowestPrice': lowest_price,
            'highestPrice': highest_price
        })
    except Exception as e:
        # If there's an error, print it to the console
        print(f"An error occurred: {e}")
        # And return an error message in the JSON response
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)