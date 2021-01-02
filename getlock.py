import yaml
import json
import os
import namesgenerator

from box import Box

from flask import Flask, make_response
from flask_restful import Api

from lib.storage import RedisStorage

from lib.health import Health
from lib.lock_manager import LockManager
from lib.lock_catalog import LockCatalog

name = namesgenerator.get_random_name().replace('_', '-')

config = Box.from_yaml(
    filename=os.environ.get("CONFIG_PATH", "./config.example.yml"),
    Loader=yaml.FullLoader,
)

app = Flask(__name__)
api = Api(app)


@api.representation('application/json')
def output_json(data, code, headers=None):
    resp = make_response(json.dumps(data), code)
    resp.headers.extend(headers or {})
    resp.headers.extend({"Server": f"GetLock/{name}"})
    return resp


storage = RedisStorage(**config.redis)


# TODO Add namespaces
# TODO Consider separate create/refresh paths
api.add_resource(Health, "/health")
api.add_resource(LockManager, "/<uuid:lock_id>", resource_class_kwargs={"storage": storage})
api.add_resource(LockCatalog, "/locks", resource_class_kwargs={"storage": storage})

# TODO Add metrics

if __name__ == "__main__":
    app.run(**config.flask)
