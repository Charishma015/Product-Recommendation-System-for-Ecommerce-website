from flask import Flask, render_template, request
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from scipy.sparse import csr_matrix
from scipy.sparse.linalg import svds

# Initialize the Flask app
app = Flask(__name__, static_folder='static')

# Load and preprocess the dataset
electronics_df = pd.read_csv(r'C:\Users\Lenovo\OneDrive\Desktop\ratings_Electronics.csv', names=['userId', 'productId', 'ratings', 'timestamp'])
electronics_df.drop('timestamp', axis=1, inplace=True)
electronics_df1 = electronics_df.iloc[:50000, :]

# Function to generate popularity-based recommendations
def recommend_popularity(user_id):
    train_data_grouped = electronics_df.groupby('productId').agg({'userId': 'count'}).reset_index()
    train_data_grouped.rename(columns={'userId': 'score'}, inplace=True)
    train_data_sort = train_data_grouped.sort_values(['score', 'productId'], ascending=[0, 1])
    train_data_sort['rank'] = train_data_sort['score'].rank(ascending=0, method='first')
    return train_data_sort.head(5)

# Function to generate collaborative filtering recommendations
def recommend_cf(user_id):
    pivot_df = electronics_df.pivot(index='userId', columns='productId', values='ratings').fillna(0)
    pivot_sparse = csr_matrix(pivot_df.values)
    U, sigma, Vt = svds(pivot_sparse, k=10)
    all_user_predicted_ratings = np.dot(np.dot(U, np.diag(sigma)), Vt)
    preds_df = pd.DataFrame(all_user_predicted_ratings, columns=pivot_df.columns)
    
    if user_id in preds_df.index:
        return preds_df.iloc[user_id].sort_values(ascending=False).head(5)
    else:
        return pd.DataFrame()  # Return empty DataFrame if user_id is not found

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/recommend', methods=['POST'])
def recommend():
    user_id = request.form.get('userId', type=int)
    method = request.form.get('method', 'popularity')

    if method == 'popularity':
        recommendations = recommend_popularity(user_id)
    elif method == 'cf':
        recommendations = recommend_cf(user_id)
    else:
        recommendations = pd.DataFrame()

    if isinstance(recommendations, pd.DataFrame) and recommendations.empty:
        recommendations = None
    
    return render_template('recommendations.html', recommendations=recommendations)

if __name__ == '__main__':
    app.run(debug=True)
