# Sistema de logging para Python
# Compatible con estilos snake_case y PascalCase

def logDebug(msg, *args):
    print(f"🔍 [DEBUG] {msg}", *args)

def logInfo(msg, *args):
    print(f"ℹ️ [INFO] {msg}", *args)

def logSequence(module, msg):
    print(f"🔄 [SEQ] {module} >> {msg}")

def logWarn(msg, *args):
    print(f"⚠️ [WARN] {msg}", *args)

def logError(msg, *args):
    print(f"❌ [ERROR] {msg}", *args)

# Alias para compatibilidad
log_debug = logDebug
log_info = logInfo
log_sequence = logSequence
log_warn = logWarn
log_error = logError
