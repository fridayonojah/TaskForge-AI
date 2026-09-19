import os
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor


def configure_tracing(app=None) -> None:
    otlp_endpoint = os.environ.get("OTLP_ENDPOINT", "")
    if not otlp_endpoint:
        return
    provider = TracerProvider()
    exporter = OTLPSpanExporter(endpoint=f"{otlp_endpoint}/v1/traces")
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)
    if app is not None:
        FastAPIInstrumentor.instrument_app(app)
