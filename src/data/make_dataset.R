# ==============================================================================
# 🚀 TheLook Churn: Pipeline de Procesamiento de Datos (R Version)
# ==============================================================================
# Este script replica fielmente la lógica de make_dataset.py para R Studio.
# Garantiza: Integridad Temporal y Privacidad (Zero Trust).
# ==============================================================================

# 1. Carga de Librerías (Equivalentes a Pandas/OS)
if (!require(\"dplyr\")) install.packages(\"dplyr\")
if (!require(\"lubridate\")) install.packages(\"lubridate\")
if (!require(\"readr\")) install.packages(\"readr\")
if (!require(\"digest\")) install.packages(\"digest\") # Para Hashing SHA-256

library(dplyr)
library(lubridate)
library(readr)
library(digest)

# 2. Configuración de Rutas
RAW_DIR <- \"data/raw\"
PROCESSED_DIR <- \"data/processed\"
SALT <- \"default_salt_antigravity\" # Debe coincidir con Python para trazabilidad

# 3. Carga de Datos
message(\"🧪 Cargando archivos CSV crudos...\")
orders <- read_csv(file.path(RAW_DIR, \"orders.csv\"), show_col_types = FALSE)
order_items <- read_csv(file.path(RAW_DIR, \"order_items.csv\"), show_col_types = FALSE)
events <- read_csv(file.path(RAW_DIR, \"events.csv\"), show_col_types = FALSE)
users <- read_csv(file.path(RAW_DIR, \"users.csv\"), show_col_types = FALSE)

# 4. Manejo de Fechas y Definición de CUTOFF (Anti-Leakage)
order_items <- order_items %>%
  mutate(created_at = as_datetime(created_at))

MAX_DATE <- max(order_items$created_at, na.rm = TRUE)
CHURN_WINDOW <- days(120)
CUTOFF_DATE <- MAX_DATE - CHURN_WINDOW

message(paste(\"📅 Fecha Máxima:\", MAX_DATE))
message(paste(\"📅 Fecha de Corte (Honesta):\", CUTOFF_DATE))

# 5. Filtrado Aguas Arriba (Upstream Filtering)
valid_status <- c('Complete', 'Shipped', 'Processing')

order_items_clean <- order_items %>%
  filter(status %in% valid_status, created_at <= CUTOFF_DATE)

events_clean <- events %>%
  mutate(created_at = as_datetime(created_at)) %>%
  filter(created_at <= CUTOFF_DATE)

# 6. Agregación RFM y Features de Usuario
message(\"🧮 Calculando métricas RFM...\")

user_features <- order_items_clean %>%
  group_by(user_id) %>%
  summarise(
    total_orders = n_distinct(order_id),
    total_items = n(),
    total_revenue = sum(sale_price),
    first_purchase = min(created_at),
    last_purchase = max(created_at)
  ) %>%
  mutate(
    recency_days = as.integer(as.duration(last_purchase %--% CUTOFF_DATE) / ddays(1)),
    customer_tenure_days = as.integer(as.duration(first_purchase %--% CUTOFF_DATE) / ddays(1))
  )

# 7. Eventos Web (Pivot simple)
message(\"🌐 Procesando eventos web...\")
event_features <- events_clean %>%
  group_by(user_id, event_type) %>%
  summarise(n = n(), .groups = 'drop') %>%
  tidyr::pivot_wider(names_from = event_type, values_from = n, names_prefix = \"events_\", values_fill = 0)

user_features <- user_features %>%
  left_join(event_features, by = \"user_id\") %>%
  mutate(across(starts_with(\"events_\"), ~replace_na(., 0)))

# 8. Definición de Target Churn (Ventana Futura)
users_with_purchases_post_cutoff <- order_items %>%
  filter(status %in% valid_status, created_at > CUTOFF_DATE) %>%
  pull(user_id) %>%
  unique()

user_features <- user_features %>%
  mutate(is_churned = if_else(user_id %in% users_with_purchases_post_cutoff, 0, 1))

# 9. Anonimización (Zero Trust Hashing)
# Aplicar el mismo SHA-256 + Salt que en Python
message(\"🔒 Aplicando seudonimización SHA-256 con Salt...\")

salt_hash <- function(id, salt) {
  # serialize=FALSE asegura que se comporte como un string raw igual que Python
  sapply(id, function(x) substr(digest(paste0(x, salt), algo=\"sha256\", serialize=FALSE), 1, 12))
}

user_features <- user_features %>%
  mutate(Internal_ID = salt_hash(user_id, SALT)) %>%
  select(-user_id) # Destruir ID original

# 10. Guardar Resultado
if (!dir.exists(PROCESSED_DIR)) dir.create(PROCESSED_DIR, recursive = TRUE)
output_path <- file.path(PROCESSED_DIR, \"user_features_churn_R.csv\")
write_csv(user_features, output_path)

message(paste(\"✅ Dataset procesado en R guardado en:\", output_path))
