import pandas as pd
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig
import logging

# Configuración de logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PIIAnonymizer:
    def __init__(self):
        # Inicializamos los motores de Presidio
        self.analyzer = AnalyzerEngine()
        self.anonymizer = AnonymizerEngine()
        
    def scan_dataframe(self, df, sample_size=10, ignore_cols=None):
        """
        Escanea un DataFrame en busca de PII en todas sus columnas (excepto ignore_cols).
        """
        pii_report = {}
        ignore_cols = ignore_cols or []
        
        # Filtrar columnas que no queremos escanear (IDs, métricas técnicas)
        cols_to_scan = [c for c in df.columns if c not in ignore_cols]
        
        # Muestreo proactivo
        sample_df = df[cols_to_scan].head(sample_size).astype(str)
        
        for col in cols_to_scan:
            detections = []
            for text in sample_df[col]:
                results = self.analyzer.analyze(text=text, language='en')
                if results:
                    top_result = max(results, key=lambda x: x.score)
                    if top_result.score > 0.4:
                        detections.append(top_result.entity_type)
            
            if detections:
                most_common_entity = max(set(detections), key=detections.count)
                pii_report[col] = most_common_entity
                
        return pii_report

    def anonymize_dataframe(self, df, pii_columns):
        """
        Anonimiza las columnas detectadas. 
        En el ETL (Shift-Left), este proceso es batch.
        """
        df_clean = df.copy()
        
        operators = {
            "PERSON": OperatorConfig("replace", {"new_value": "<NAME>"}),
            "EMAIL_ADDRESS": OperatorConfig("replace", {"new_value": "<EMAIL>"}),
            "PHONE_NUMBER": OperatorConfig("mask", {"type": "mask", "masking_char": "*", "chars_to_mask": 10, "from_end": True}),
            "LOCATION": OperatorConfig("replace", {"new_value": "<LOCATION>"}),
        }

        for col, entity_type in pii_columns.items():
            logger.info(f"🛡️ Anonimizando columna: {col} (Entidad: {entity_type})")
            
            # Optimización Batch: Procesar valores únicos para evitar redundancia
            unique_vals = df_clean[col].astype(str).unique()
            val_map = {}
            
            for val in unique_vals:
                results = self.analyzer.analyze(text=val, language='en')
                if results:
                    anonymized_result = self.anonymizer.anonymize(
                        text=val,
                        analyzer_results=results,
                        operators={entity_type: operators.get(entity_type, OperatorConfig("replace", {"new_value": f"<{entity_type}>"}))}
                    )
                    val_map[val] = anonymized_result.text
                else:
                    val_map[val] = val
                    
            # Mapeo masivo en lugar de .apply por cada fila
            df_clean[col] = df_clean[col].astype(str).map(val_map)
            
        return df_clean

# Registro de extensión para conveniencia
@pd.api.extensions.register_dataframe_accessor("pii")
class PIIAccessor:
    def __init__(self, pandas_obj):
        self._obj = pandas_obj
        self._engine = None

    def _get_engine(self):
        if self._engine is None:
            self._engine = PIIAnonymizer()
        return self._engine

    def scan(self, sample_size=10, ignore_cols=None):
        return self._get_engine().scan_dataframe(self._obj, sample_size, ignore_cols)

    def anonymize(self, pii_report):
        return self._get_engine().anonymize_dataframe(self._obj, pii_report)
