from locust import HttpUser, task, between

class MaterchildUser(HttpUser):
    """
    Simulación de usuarios concurrentes - Materchild Predic
    Equipo: Creciendo Juntos
    """
    wait_time = between(1, 3)  # Espera entre 1 y 3 segundos entre tareas

    # ============================================================
    # PR-01: Prueba de rendimiento - Login (solicitar OTP)
    # ============================================================
    @task(3)
    def test_solicitar_otp(self):
        self.client.post("/api/auth/solicitar-otp", json={
            "correo": "fresitadeborojo@gmail.com"
        }, name="PR-01 Solicitar OTP")

    # ============================================================
    # PR-02: Prueba de rendimiento - Login administrador
    # ============================================================
    @task(2)
    def test_admin_login(self):
        self.client.post("/api/auth/admin-login", json={
            "usuario": "admin",
            "contrasena": "14521"
        }, name="PR-02 Login Administrador")

    # ============================================================
    # PR-03: Prueba de rendimiento - Obtener pacientes
    # ============================================================
    @task(4)
    def test_obtener_pacientes(self):
        self.client.get("/api/pacientes",
            name="PR-03 Obtener Pacientes")

    # ============================================================
    # PR-04: Prueba de rendimiento - Estado del sistema
    # ============================================================
    @task(1)
    def test_estado_sistema(self):
        self.client.get("/api/estado",
            name="PR-04 Estado del Sistema")

    # ============================================================
    # PR-05: Prueba de rendimiento - Registro de médico
    # ============================================================
    @task(2)
    def test_registro(self):
        import random
        correo = f"medico{random.randint(1000,9999)}@usc.edu.co"
        self.client.post("/api/auth/register", json={
            "nombres": "Test",
            "apellidos": "Medico",
            "correo_institucional": correo,
            "especialidad": "Ginecología"
        }, name="PR-05 Registro Médico")
