import os
import google.generativeai as genai
import json

class AIService:
    """
    Implementación del Patrón Singleton para la predicción salud materno infantil (IA).
    Garantiza que solo se inicialice una conexión a la API en todo el sistema.
    """
    _instancia = None

    def __new__(cls):
        if cls._instancia is None:
            print("🧠 Inicializando la predicción (Patrón Singleton)...")
            cls._instancia = super(AIService, cls).__new__(cls)
            cls._instancia._inicializar()
        return cls._instancia

    def _inicializar(self):
        # Este método solo se ejecuta la primera vez que se llama a la clase
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.modo_simulacion = False

        if not self.api_key or self.api_key == "tu_clave_aqui_cuando_la_tengas":
            print("⚠️ [IA MODO SIMULACIÓN]: No se detectó GEMINI_API_KEY.")
            self.modo_simulacion = True
        else:
            print("🔍 Escaneando servidores de Google buscando el mejor modelo...")
            genai.configure(api_key=self.api_key)
            
            # AUTO-DESCUBRIMIENTO: Buscamos qué modelos están disponibles para tu API Key
            modelo_elegido = 'gemini-pro' # Fallback universal por defecto
            
            try:
                for m in genai.list_models():
                    if 'generateContent' in m.supported_generation_methods:
                        # Preferimos cualquier versión de flash o pro que esté disponible
                        if 'flash' in m.name or 'pro' in m.name:
                            modelo_elegido = m.name.replace('models/', '')
                            break
            except Exception as e:
                print(f"⚠️ No se pudo listar los modelos, usando fallback. Detalle: {e}")

            print(f"✅ IA establecida. Utilizando el modelo dinámico: {modelo_elegido}")
            self.modelo = genai.GenerativeModel(modelo_elegido)

    def predecir_riesgo_clinico(self, datos_paciente):
        """
        Método central donde la IA actúa como médico experto.
        """
        if self.modo_simulacion:
            return {
                "enfermedad_predicha": "Preeclampsia (Simulada)",
                "justificacion": "La IA simulada detectó una presión sistólica elevada combinada con edad materna avanzada.",
                "recomendacion_medica": "Programar monitoreo estricto de presión arterial y proteinuria 24h.",
                "nivel_riesgo": "Alto",
                "confianza_ia": 92,
                "alerta_glucosa": "Niveles estables."
            }

        prompt = f"""
        Eres un 'Oráculo Clínico', un sistema experto en ginecobstetricia de la plataforma Materchild Predic.
        Analiza los siguientes signos vitales de una paciente gestante: {datos_paciente}
        
        Basado estrictamente en estos datos, debes determinar:
        1. La complicación materna MÁS PROBABLE.
        2. El nivel de riesgo general (Alto, Medio, Bajo).
        3. Un porcentaje de confianza de tu predicción (número entero entre 70 y 99).
        4. Una alerta específica sobre el nivel de azúcar en la sangre.

        Responde ESTRICTAMENTE en formato JSON con esta estructura exacta, sin texto adicional:
        {{
            "enfermedad_predicha": "Nombre de la enfermedad",
            "justificacion": "Explica de forma directa POR QUÉ asignaste ese nivel de riesgo y esa enfermedad, basándote en los signos vitales específicos que están alterados.",
            "recomendacion_medica": "Acción clínica sugerida",
            "nivel_riesgo": "Alto",
            "confianza_ia": 95,
            "alerta_glucosa": "Nota clínica sobre los niveles de azúcar."
        }}
        """

        try:
            respuesta = self.modelo.generate_content(prompt)
            texto_limpio = respuesta.text.replace("```json", "").replace("```", "").strip()
            return json.loads(texto_limpio)
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Error analizando respuesta de IA: {error_msg}")
            
            # Detectamos si es el límite de velocidad de Google
            if "Quota" in error_msg or "429" in error_msg or "exhausted" in error_msg.lower():
                print("⚠️ Límite de velocidad de la API alcanzado. Reintente en 1 minuto")
                return None
        
    def generar_identidades_sinteticas(self, cantidad):
        if self.modo_simulacion:
            return [{"nombres_ficticios": f"Paciente {i}", "apellidos_ficticios": "Simulada", "identificacion_ficticia": f"100000{i}", "peso": 70.5} for i in range(cantidad)]

        prompt = f"""
        Genera {cantidad} identidades ficticias de mujeres gestantes en Colombia.
        Para cada una debes inventar:
        1. Un nombre ("nombres_ficticios").
        2. Un apellido ("apellidos_ficticios").
        4. Un peso corporal realista durante el embarazo entre 50.0 y 95.0 kg ("peso").
        
        Devuelve SOLO un array JSON válido. NO uses formato markdown, NO escribas ```json, NO escribas texto antes ni después.
        Ejemplo exacto de lo que debes devolver:
        [
            {{"nombres_ficticios": "Ana Maria", "apellidos_ficticios": "Perez Gomez", "peso": 65.4}},
            {{"nombres_ficticios": "Luisa Fernanda", "apellidos_ficticios": "Diaz Ruiz", "peso": 78.1}}
        ]
        """

        try:
            respuesta = self.modelo.generate_content(prompt)
            texto_limpio = respuesta.text.strip()
            
            if texto_limpio.startswith("```json"):
                texto_limpio = texto_limpio[7:]
            if texto_limpio.startswith("```"):
                texto_limpio = texto_limpio[3:]
            if texto_limpio.endswith("```"):
                texto_limpio = texto_limpio[:-3]
                
            identidades = json.loads(texto_limpio.strip())
            
            while len(identidades) < cantidad:
                identidades.append({"nombres_ficticios": "Maria", "apellidos_ficticios": "Generada", "peso": 70.0})
                
            return identidades[:cantidad]
            
        except Exception as e:
            print(f"\n❌ ERROR EXACTO DE IA: {e}")
            return None