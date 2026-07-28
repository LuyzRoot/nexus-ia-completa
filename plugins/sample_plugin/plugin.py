import logging

logger = logging.getLogger(__name__)

class SamplePlugin:
    def on_load(self):
        logger.info("SamplePlugin loaded")

    def on_enable(self):
        logger.info("SamplePlugin enabled")

    def on_disable(self):
        logger.info("SamplePlugin disabled")

    def on_unload(self):
        logger.info("SamplePlugin unloaded")
