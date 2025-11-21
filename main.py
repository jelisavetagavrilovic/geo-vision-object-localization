import yaml
import logging
from src.pipeline import ObjectMappingPipeline


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)


if __name__ == "__main__":
    config = yaml.safe_load(open("src/config.yaml"))
    pipeline = ObjectMappingPipeline(config)
    pipeline.run()
