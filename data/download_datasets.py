import kagglehub
import os
import shutil
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# Asegurar que las credenciales estén disponibles para kagglehub/kaggle
if not os.getenv("KAGGLE_USERNAME") or not os.getenv("KAGGLE_KEY"):
    print("⚠️ Error: No se encontraron KAGGLE_USERNAME o KAGGLE_KEY en el archivo .env")
    exit(1)

# Download latest version
print("🚀 Iniciando descarga desde Kaggle...")
try:
    path = kagglehub.dataset_download("mustafakeser4/looker-ecommerce-bigquery-dataset")
    print("✓ Path to dataset files:", path)

    # Crear carpeta raw si no existe
    raw_data_path = "data/raw"
    os.makedirs(raw_data_path, exist_ok=True)

    # Copiar archivos CSV desde path a data/raw
    files = os.listdir(path)
    for file in files:
        if file.endswith(".csv"):
            src = os.path.join(path, file)
            dst = os.path.join(raw_data_path, file)
            shutil.copy(src, dst)
            print(f"✓ Copiado: {file}")

    print(f"\n✅ {len(files)} archivos copiados exitosamente a {raw_data_path}")

except Exception as e:
    print(f"❌ Error durante la descarga: {str(e)}")
    exit(1)
