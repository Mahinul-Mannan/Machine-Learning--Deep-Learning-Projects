# Car-Purchase-Amount-Prediction-Using-ANNs

## Project Overview
### Goals
This project aims to develop a machine learning model using an Artificial Neural Network (ANN) to predict the car purchase amount based on various customer features. By predicting purchase amounts accurately, businesses in the automotive industry can make data-driven decisions related to pricing, marketing, and customer segmentation.

### Dataset
The dataset used in this project contains customer information such as:

Age: Customer's age, which may influence purchasing power.
Annual Income: A factor that directly impacts the potential for purchasing a car.
Credit Score: A reflection of the customer's financial reliability.
Gender: A demographic feature.
These features are used as inputs to predict the target variable: Car Purchase Amount.

### Model Purpose
We use an Artificial Neural Network (ANN) to predict continuous values (i.e., the car purchase amount). ANNs are ideal for regression tasks because they can model complex, non-linear relationships between input features and target variables.

### Outline
The workflow for this project consists of:

### Exploratory Data Analysis (EDA): Understand the distribution and relationships of features in the dataset.
Data Preprocessing: Prepare the dataset by handling missing values, scaling features, and encoding categorical data.
Model Building: Construct and compile the ANN model with appropriate layers, activation functions, and optimizers.
Training and Evaluation: Train the model using training data and evaluate its performance using metrics like Mean Absolute Error (MAE) and Mean Squared Error (MSE).
Testing with New Data: Test the model's ability to predict car purchase amounts on unseen data.
Project Setup
Requirements
Python 3.x
TensorFlow 2.x
Keras
scikit-learn
Pandas
Matplotlib (for visualizations)
Numpy

### Installation
To set up the environment, clone this repository and install the necessary dependencies.

#### Clone the repository:

git clone https://github.com/yourusername/Car-Purchase-Amount-Prediction-Project.git
Install dependencies (create a virtual environment and activate it first):

pip install -r requirements.txt
#### Files
car_purchase_data.csv: The dataset containing customer data.
Car Purchase Amount Prediction.ipynb: Jupyter notebook implementing the project.

## Data
The dataset used in this project can be found in the data folder. This file contains customer-related features that are used to predict the car purchase amount.

## How to Run the Project
Open the Car Purchase Amount Prediction.ipynb Jupyter notebook.
Follow the steps in the notebook:
Load and preprocess the dataset.
Build and train the model.
Evaluate the model's performance.
Test the model with new data to make predictions.
Results and Evaluation
In this section, the model's performance is evaluated using:

Mean Absolute Error (MAE): Measures the average absolute error between predicted and actual values.
Mean Squared Error (MSE): Measures the average squared error, which penalizes large errors more.

## Future Improvements
Hyperparameter Tuning: Experiment with different hyperparameters like the number of layers, neurons, and learning rate for better performance.
Cross-Validation: Implement cross-validation for more robust model evaluation.
Additional Features: Integrate additional customer features (e.g., geographic location) to improve prediction accuracy.

## License
This project is licensed under the MIT License - see the LICENSE file for details.

