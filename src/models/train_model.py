import pandas as pd
import numpy as np
import joblib
import os
import sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    classification_report, f1_score, recall_score,
    precision_score, accuracy_score, brier_score_loss,
    roc_auc_score, roc_curve, confusion_matrix, ConfusionMatrixDisplay
)
from xgboost import XGBClassifier

# Importar preprocesamiento modular
sys.path.append(os.getcwd())
from src.features.build_features import preprocess_data

FIGURES_DIR = "reports/figures"


# Entrena y compara LogReg vs RandomForest vs XGBoost
def evaluate_and_compare(X_train, X_test, y_train, y_test, preprocessor):
    results = {}

    # Calcular scale_pos_weight para XGBoost
    neg_count = (y_train == 0).sum()
    pos_count = (y_train == 1).sum()
    scale_ratio = neg_count / pos_count if pos_count > 0 else 1.0

    models = {
        'LogisticRegression': LogisticRegression(
            max_iter=1000, random_state=42, class_weight='balanced'
        ),
        'RandomForest': RandomForestClassifier(
            n_estimators=100, max_depth=8, random_state=42, class_weight='balanced'
        ),
        'XGBoost': XGBClassifier(
            n_estimators=150, max_depth=6, learning_rate=0.1,
            scale_pos_weight=scale_ratio, random_state=42,
            eval_metric='logloss', verbosity=0
        ),
    }

    for name, clf in models.items():
        print(f"🚀 Entrenando {name}...")
        pipeline = Pipeline([
            ('preprocessor', preprocessor),
            ('clf', clf)
        ])

        pipeline.fit(X_train, y_train)
        y_pred = pipeline.predict(X_test)
        y_prob = pipeline.predict_proba(X_test)[:, 1]

        results[name] = {
            'pipeline': pipeline,
            'accuracy': accuracy_score(y_test, y_pred),
            'f1': f1_score(y_test, y_pred),
            'recall': recall_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred),
            'auc': roc_auc_score(y_test, y_prob),
            'brier': brier_score_loss(y_test, y_prob),
            'report': classification_report(y_test, y_pred),
            'y_pred': y_pred,
            'y_prob': y_prob,
        }

    return results


# Genera la curva ROC comparativa de todos los modelos
def generate_roc_curves(results, y_test):
    os.makedirs(FIGURES_DIR, exist_ok=True)

    fig, ax = plt.subplots(figsize=(8, 6))
    colors = {'LogisticRegression': '#3B82F6', 'RandomForest': '#22C55E', 'XGBoost': '#F59E0B'}

    for name, metrics in results.items():
        fpr, tpr, _ = roc_curve(y_test, metrics['y_prob'])
        ax.plot(fpr, tpr, label=f"{name} (AUC={metrics['auc']:.4f})",
                color=colors.get(name, '#888'), linewidth=2)

    ax.plot([0, 1], [0, 1], 'k--', alpha=0.4, label='Aleatorio (AUC=0.50)')
    ax.set_xlabel('Tasa de Falsos Positivos', fontsize=12)
    ax.set_ylabel('Tasa de Verdaderos Positivos', fontsize=12)
    ax.set_title('Curvas ROC Comparativas — Modelos de Churn', fontsize=14, fontweight='bold')
    ax.legend(fontsize=10, loc='lower right')
    ax.grid(True, alpha=0.3)
    plt.tight_layout()

    path = os.path.join(FIGURES_DIR, "roc_comparison.png")
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"📊 Curvas ROC guardadas en {path}")


# Genera la matriz de confusión para un modelo
def generate_confusion_matrices(results, y_test):
    os.makedirs(FIGURES_DIR, exist_ok=True)

    for name, metrics in results.items():
        cm = confusion_matrix(y_test, metrics['y_pred'])
        fig, ax = plt.subplots(figsize=(5, 4))
        disp = ConfusionMatrixDisplay(cm, display_labels=['Activo', 'Churned'])
        disp.plot(ax=ax, cmap='Blues', values_format='d')
        ax.set_title(f'Matriz de Confusión: {name}', fontsize=12, fontweight='bold')
        plt.tight_layout()

        safe_name = name.replace(' ', '_')
        path = os.path.join(FIGURES_DIR, f"confusion_matrix_{safe_name}.png")
        fig.savefig(path, dpi=150, bbox_inches='tight')
        plt.close(fig)
        print(f"📊 Matriz de confusión {name} guardada en {path}")


# Genera el reporte markdown enriquecido
def generate_benchmark_report(results):
    report = "# 📊 Benchmark de Modelos de Churn\n\n"
    report += "## Tabla Comparativa\n\n"
    report += "| Modelo | Accuracy | Precision | Recall | F1-Score | AUC | Brier |\n"
    report += "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n"

    best_auc = 0
    winner = ""
    for name, m in results.items():
        report += (f"| {name} | {m['accuracy']:.4f} | {m['precision']:.4f} | "
                   f"{m['recall']:.4f} | {m['f1']:.4f} | {m['auc']:.4f} | {m['brier']:.4f} |\n")
        if m['auc'] > best_auc:
            best_auc = m['auc']
            winner = name

    report += f"\n🏆 **Modelo Ganador**: {winner} (AUC = {best_auc:.4f})\n\n"
    report += "## Curvas ROC Comparativas\n\n"
    report += "![Curvas ROC](figures/roc_comparison.png)\n\n"
    report += "## Matrices de Confusión\n\n"

    for name in results:
        safe_name = name.replace(' ', '_')
        report += f"### {name}\n"
        report += f"![Matriz de Confusión {name}](figures/confusion_matrix_{safe_name}.png)\n\n"

    report += "## Interpretación\n\n"
    report += "- **AUC (Área Bajo la Curva ROC)**: Mide la capacidad de discriminar entre Churned y Activo. Mayor es mejor.\n"
    report += "- **Brier Score**: Mide la calibración de probabilidades. Menor es mejor.\n"
    report += "- **Recall**: Proporción de churners reales detectados. Crítico para campañas de retención.\n"
    report += "- **XGBoost** usa `scale_pos_weight` para manejar el desbalance de clases de forma nativa.\n"

    os.makedirs("reports", exist_ok=True)
    with open("reports/model_benchmarking.md", "w") as f:
        f.write(report)
    print("📝 Reporte de benchmark guardado en reports/model_benchmarking.md")


# Pipeline completo de entrenamiento y benchmarking
def train_pipeline(data_path, model_output_path):
    print(f"📦 Cargando datos desde {data_path}...")
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"No se encontró el archivo {data_path}.")

    df = pd.read_csv(data_path)

    # 1. Preprocesamiento modular
    print("🛠️ Aplicando preprocesamiento modular...")
    df = preprocess_data(df)

    target = 'is_churned'
    X = df.drop(columns=[target, 'Internal_ID'], errors='ignore')
    y = df[target]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # 2. Preprocesamiento por tipo de columna
    categorical_cols = X_train.select_dtypes(include=['object', 'category', 'str']).columns.tolist()
    numerical_cols = X_train.select_dtypes(exclude=['object', 'category', 'str']).columns.tolist()

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', Pipeline([
                ('imputer', SimpleImputer(strategy='constant', fill_value=0)),
                ('scaler', StandardScaler())
            ]), numerical_cols),
            ('cat', Pipeline([
                ('imputer', SimpleImputer(strategy='most_frequent')),
                ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
            ]), categorical_cols)
        ]
    )

    # 3. Benchmark con 3 modelos
    comparison = evaluate_and_compare(X_train, X_test, y_train, y_test, preprocessor)

    # 4. Generar gráficos y reporte
    generate_roc_curves(comparison, y_test)
    generate_confusion_matrices(comparison, y_test)
    generate_benchmark_report(comparison)

    # 5. Guardar el modelo ganador
    winner_name = max(comparison, key=lambda k: comparison[k]['auc'])
    print(f"\n🏆 El ganador es: {winner_name} (AUC={comparison[winner_name]['auc']:.4f})")

    for name, metrics in comparison.items():
        print(f"\n--- {name} ---")
        print(metrics['report'])

    os.makedirs(os.path.dirname(model_output_path), exist_ok=True)
    joblib.dump(comparison[winner_name]['pipeline'], model_output_path)
    print(f"💾 Modelo {winner_name} guardado en {model_output_path}")


if __name__ == "__main__":
    DATA_PATH = "data/processed/user_features_churn.csv"
    MODEL_OUTPUT = "models/churn_pipeline_v1.joblib"
    train_pipeline(DATA_PATH, MODEL_OUTPUT)
