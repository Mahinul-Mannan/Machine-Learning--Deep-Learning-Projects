# CiFAR-10 Image Classification Using CNNs

## Author
**Mahinul Mannan**

---

## Overview
This project demonstrates the classification of images from the CiFAR-10 dataset using Convolutional Neural Networks (CNNs). The dataset contains 60,000 images (32x32 pixels each) categorized into 10 distinct classes:
1. Airplanes  
2. Cars  
3. Birds  
4. Cats  
5. Deer  
6. Dogs  
7. Frogs  
8. Horses  
9. Ships  
10. Trucks  

The primary goal is to build a robust CNN model to accurately classify images into these categories.

---

## Features
- **Visualization**: Displays sample images from the dataset.
- **Model Building**: A sequential CNN with multiple layers for feature extraction and classification.
- **Evaluation**: Model accuracy assessed on test data with confusion matrices.
- **Data Augmentation**: Techniques like rotation, flipping, and brightness adjustments to enhance model generalization.
- **Model Saving**: Trained models are saved for future use.

---

## Dataset
- **Name**: CiFAR-10
- **Source**: [CIFAR-10 Dataset](https://www.cs.toronto.edu/~kriz/cifar.html)
- **Description**:
  - 60,000 32x32 color images.
  - 50,000 images for training and 10,000 images for testing.
  - 10 classes with 6,000 images each.

---

## Steps
### 1. Problem Definition
- Understand the dataset and define the classification task.

### 2. Data Preparation
- Import and preprocess the CiFAR-10 dataset:
  - Normalize image pixel values.
  - One-hot encode class labels.

### 3. Visualize Dataset
- Randomly display images from the dataset with their labels.

### 4. Build the Model
- Create a sequential CNN model with layers:
  - Convolutional layers for feature extraction.
  - Pooling layers for dimensionality reduction.
  - Dropout layers for regularization.
  - Dense layers for classification.

### 5. Train the Model
- Train the model on the training dataset.
- Evaluate the model using accuracy and loss metrics.

### 6. Improve with Data Augmentation
- Enhance model generalization using techniques such as:
  - Rotation
  - Flipping
  - Brightness adjustment

### 7. Save the Model
- Save the trained model for future inference.

---

## Results
- **Baseline Test Accuracy**: Achieved approximately **75% accuracy** using the original dataset.
- **Enhanced Test Accuracy**: Achieved approximately **82% accuracy** with data augmentation.

---

## Instructions to Run
### Requirements
- Python 3.8+
- Libraries: `numpy`, `keras`, `tensorflow`, `matplotlib`, `seaborn`

### Steps
1. Clone the repository:
   ```bash
   git clone **[CiFAR-10 Image Classification Using CNNs](https://github.com/Mahinul-Mannan/Machine-Learning--Deep-Learning-Projects/blob/main/Project-2%20---%20CiFAR-10%20Images%20Classification%20Using%20CNNs/Mahin's%20Project%202%20-%20CiFAR-10%20Images%20Classification%20Using%20CNNs.ipynb)**
   cd cifar10-cnn

## File Structure
plaintext
Copy code
    ```bash
    cifar10-cnn/
    │
    ├── cifar10_classification.ipynb  # Jupyter notebook with implementation
    ├── saved_models/                # Directory to save trained models
    ├── data/                        # (Optional) Dataset folder, if required
    ├── README.md                    # Documentation
    └── requirements.txt             # Dependencies

## License
This project is licensed under the MIT License. See the LICENSE file for details.
