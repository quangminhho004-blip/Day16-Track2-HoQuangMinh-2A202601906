import pandas as pd
import numpy as np
import lightgbm as lgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, accuracy_score, f1_score, precision_score, recall_score
import time
import json
import os
import warnings

warnings.filterwarnings('ignore')

def main():
    results = {}
    
    # 1. Load data
    print("Loading data...")
    start_time = time.time()
    data_path = os.path.expanduser('~/ml-benchmark/creditcard.csv')
    if not os.path.exists(data_path):
        print(f"Error: Data not found at {data_path}. Please download dataset first.")
        return

    df = pd.read_csv(data_path)
    
    X = df.drop('Class', axis=1)
    y = df['Class']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    results['Thời gian load data'] = f"{time.time() - start_time:.4f} seconds"
    print("Data loaded successfully.")
    
    # 2. Train model
    print("Training model...")
    start_time = time.time()
    model = lgb.LGBMClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    results['Thời gian training'] = f"{time.time() - start_time:.4f} seconds"
    
    if hasattr(model, 'best_iteration_') and model.best_iteration_ is not None:
        results['Best iteration'] = str(model.best_iteration_)
    else:
        results['Best iteration'] = '100'
    print("Training completed.")
        
    # 3. Evaluate
    print("Evaluating model...")
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    
    results['AUC-ROC'] = f"{roc_auc_score(y_test, y_pred_proba):.4f}"
    results['Accuracy'] = f"{accuracy_score(y_test, y_pred):.4f}"
    results['F1-Score'] = f"{f1_score(y_test, y_pred):.4f}"
    results['Precision'] = f"{precision_score(y_test, y_pred):.4f}"
    results['Recall'] = f"{recall_score(y_test, y_pred):.4f}"
    
    # 4. Inference Latency (1 row)
    print("Measuring inference latency...")
    single_row = X_test.iloc[[0]]
    start_time = time.time()
    model.predict(single_row)
    results['Inference latency (1 row)'] = f"{(time.time() - start_time) * 1000:.4f} ms"
    
    # 5. Inference Throughput (1000 rows)
    print("Measuring inference throughput...")
    thousand_rows = X_test.iloc[:1000]
    while len(thousand_rows) < 1000:
        thousand_rows = pd.concat([thousand_rows, X_test.iloc[:1000-len(thousand_rows)]])
        
    start_time = time.time()
    model.predict(thousand_rows)
    results['Inference throughput (1000 rows)'] = f"{(time.time() - start_time) * 1000:.4f} ms"
    
    # Print and save
    print("\n--- BENCHMARK RESULTS ---")
    print(json.dumps(results, indent=4, ensure_ascii=False))
    
    with open('benchmark_result.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=4, ensure_ascii=False)
    print("\nResults saved to benchmark_result.json")

if __name__ == "__main__":
    main()
