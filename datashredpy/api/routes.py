from datashredpy.api.models import Client

class Register(Client):
    @classmethod
    def metadata(cls, metadata_json):
        print(f'metadata_json - routes.py {metadata_json}')
        client_dict = json.loads(metadata_json)
        return Client(**client_dict)
