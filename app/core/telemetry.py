from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor

from fastapi import FastAPI

def setup_telemetry(app: FastAPI) -> None:
    """Configures OpenTelemetry tracing for FastAPI and outbound HTTP calls."""
    tracer = TracerProvider()
    trace.set_tracer_provider(tracer_provider=tracer)
    cse = ConsoleSpanExporter()
    bsp = BatchSpanProcessor(cse)
    tracer.add_span_processor(bsp)
    FastAPIInstrumentor.instrument_app(app)
    HTTPXClientInstrumentor().instrument()
    