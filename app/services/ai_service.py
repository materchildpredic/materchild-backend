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
            print("⚠️ [IA MODO SIMULACIÓN]: No se detectó GEMINI_API_KEY. Usando respuestas simuladas.")
            self.modo_simulacion = True
        else:
            print("✅ Conexión con IA establecida exitosamente.")
            genai.configure(api_key=self.api_key)
            # Usamos el modelo más capaz para razonamiento clínico
            self.modelo = genai.GenerativeModel('gemini-1.5-pro')

    def predecir_riesgo_clinico(self, datos_paciente):
        """
        Método central donde la IA actúa como médico experto.
        """
        if self.modo_simulacion:
            # Respuesta rápida para pruebas de frontend sin gastar tokens
            return {
                "enfermedad_predicha": "Preeclampsia (Simulada)",
                "justificacion": "La IA simulada detectó una presión sistólica elevada combinada con edad materna avanzada.",
                "recomendacion_medica": "Programar monitoreo estricto de presión arterial y proteinuria 24h."
            }

        # PROMPT ENGINEERING: Aquí le damos la personalidad y las reglas a la IA
        prompt = f"""
        Eres un programa de predicción de salud materno infantil, un sistema experto en ginecobstetricia de la plataforma Materchild Predic.
        Analiza los siguientes signos vitales de una paciente gestante.
        
        Datos de la paciente: {datos_paciente}

        Tu tarea es identificar la complicación materna MÁS PROBABLE (ej. Preeclampsia, Diabetes Gestacional, Sepsis, Anemia, etc.).
        
        Responde ESTRICTAMENTE en formato JSON con la siguiente estructura, sin texto adicional:
        {{
            "enfermedad_predicha": "Nombre de la enfermedad",
            "justificacion": "Explicación médica breve basada en las variables alteradas",
            "recomendacion_medica": "Acción clínica sugerida"
        }}
        """

        try:
            respuesta = self.modelo.generate_content(prompt)
            # Limpiamos posibles formatos extraños que devuelva la IA (como bloques de markdown)
            texto_limpio = respuesta.text.replace("```json", "").replace("```", "").strip()
            return json.loads(texto_limpio)
        except Exception as e:
            print(f"❌ Error en la predicción de IA: {e}")
            return None