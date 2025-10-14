#!/usr/bin/env python3
"""
Script para registrar documentos de muestra solo en la base de datos SQLite
"""

import os
import sys
import glob
from models.db import create_source, connect_db

def register_sample_documents_only():
    """Registrar documentos de muestra solo en la base de datos SQLite"""
    print("=" * 60)
    print("📝 REGISTRANDO DOCUMENTOS DE MUESTRA EN BASE DE DATOS")
    print("=" * 60)
    print()
    
    try:
        sample_dir = "./static/sample_documents"
        if not os.path.exists(sample_dir):
            print(f"❌ El directorio {sample_dir} no existe")
            return False
        
        print(f"✅ Directorio encontrado: {sample_dir}")
        
        # Get all sample files
        supported_extensions = [".txt", ".pdf", ".docx", ".csv", ".html", ".md", ".xlsx", ".xls"]
        
        registered_count = 0
        
        for ext in supported_extensions:
            pattern = os.path.join(sample_dir, f"*{ext}")
            files = glob.glob(pattern)
            print(f"🔍 Buscando archivos {ext}: {len(files)} encontrados")
            
            for file_path in files:
                filename = os.path.basename(file_path)
                print(f"  📄 Procesando: {filename}")
                
                # Check if document is already registered
                conn = connect_db()
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id FROM sources WHERE name = ? AND chat_id = 1 AND type = 'sample_document'",
                    (filename,)
                )
                
                existing = cursor.fetchone()
                conn.close()
                
                if existing:
                    print(f"    ℹ️  Ya registrado en DB (ID: {existing[0]})")
                else:
                    print(f"    📝 Registrando en DB...")
                    
                    # Create description based on filename
                    if "politica" in filename.lower():
                        description = "Política de devoluciones y cambios de EcoMarket"
                    elif "preguntas" in filename.lower():
                        description = "Preguntas frecuentes de EcoMarket"
                    elif "inventario" in filename.lower():
                        description = "Inventario de productos sostenibles"
                    else:
                        description = f"Documento de muestra: {filename}"
                    
                    # Register in database
                    try:
                        create_source(
                            filename,
                            description,
                            1,  # System chat
                            source_type="sample_document"
                        )
                        print(f"    ✅ Registrado exitosamente: {filename}")
                        registered_count += 1
                    except Exception as e:
                        print(f"    ❌ Error registrando {filename}: {e}")
        
        # Verificar el resultado
        print("\n" + "=" * 40)
        print("📊 VERIFICANDO RESULTADO")
        print("=" * 40)
        
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM sources WHERE type = 'sample_document'")
        count = cursor.fetchone()[0]
        print(f"📈 Documentos de muestra en DB: {count}")
        
        cursor.execute("SELECT name, source_text FROM sources WHERE type = 'sample_document'")
        docs = cursor.fetchall()
        print("📄 Documentos registrados:")
        for doc in docs:
            print(f"  - {doc[0]}: {doc[1][:50] if doc[1] else 'Sin descripción'}...")
        
        conn.close()
        
        return count > 0
        
    except Exception as e:
        print(f"❌ Error en registro: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Función principal"""
    print("🚀 Iniciando registro de documentos de muestra...")
    print()
    
    success = register_sample_documents_only()
    
    if success:
        print("\n🎉 ¡Documentos registrados exitosamente!")
        print("Los documentos deberían aparecer ahora en el panel de admin.")
        print("Nota: Para que funcionen las consultas, necesitas configurar la API key de OpenAI")
    else:
        print("\n❌ El registro falló")

if __name__ == "__main__":
    main()
