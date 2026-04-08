import asyncio
import json
import logging
from argparse import ArgumentParser
import httpx

# Configuración básica de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

async def submit_analysis(client: httpx.AsyncClient, api_url: str, doc_id: int) -> str | None:
    """Envía una solicitud de análisis a la API."""
    payload = {
        "text": f"This is a simulated stress test document {doc_id}. The payment service depends on the user authentication module. There is a risk that the database migration may fail.",
        "source_filename": f"stress-test-doc-{doc_id}.md"
    }
    try:
        response = await client.post(f"{api_url}/api/v1/analysis/analyze", json=payload)
        response.raise_for_status()
        data = response.json()
        analysis_id = data.get("analysis_id")
        logger.info(f"Doc {doc_id}: Generado análisis ID = {analysis_id}")
        return analysis_id
    except Exception as e:
        logger.error(f"Doc {doc_id}: Error al enviar solicitud: {e}")
        return None

async def wait_for_analysis(client: httpx.AsyncClient, api_url: str, analysis_id: str, doc_id: int):
    """Realiza un polling hasta que el análisis pase de 'processing' a completado o falle."""
    while True:
        try:
            response = await client.get(f"{api_url}/api/v1/analysis/{analysis_id}")
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "completed":
                    logger.info(f"Doc {doc_id}: Análisis {analysis_id} completado con éxito.")
                    return True
            elif response.status_code != 404:
                # 404 se espera si está en procesamiento (según nuestra implementación en memoria/BD fallback asíncrono)
                logger.warning(f"Doc {doc_id}: Análisis {analysis_id} código {response.status_code}.")
        except Exception as e:
            logger.error(f"Doc {doc_id}: Error en polling {analysis_id}: {e}")
            return False
            
        await asyncio.sleep(2) # Espera 2 segundos antes de reintentar

async def worker(client: httpx.AsyncClient, api_url: str, doc_id: int):
    """Combina el envío y el polling de una única solicitud."""
    analysis_id = await submit_analysis(client, api_url, doc_id)
    if analysis_id:
        await wait_for_analysis(client, api_url, analysis_id, doc_id)

async def run_stress_test(api_url: str, num_requests: int):
    """Ejecuta múltiples solicitudes concurrentes (simulando carga)."""
    logger.info(f"Iniciando test de estrés con {num_requests} peticiones concurrentes...")
    
    # Configuramos un límite de conexiones para no ahogar nuestra propia máquina
    limits = httpx.Limits(max_connections=100, max_keepalive_connections=20)
    timeout = httpx.Timeout(30.0)
    
    async with httpx.AsyncClient(limits=limits, timeout=timeout) as client:
        # Creamos las tareas concurrentes
        tasks = [worker(client, api_url, i) for i in range(1, num_requests + 1)]
        await asyncio.gather(*tasks)

    logger.info("Test de estrés finalizado.")

if __name__ == "__main__":
    parser = ArgumentParser(description="Stress test for Risk Analysis API")
    parser.add_argument("--url", default="http://localhost:8000", help="API Base URL")
    parser.add_argument("-n", "--num-requests", type=int, default=50, help="Number of concurrent documents to analyze")
    
    args = parser.parse_args()
    asyncio.run(run_stress_test(args.url, args.num_requests))
