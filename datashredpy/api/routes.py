from datashredpy.api.models import Client

class Register(Client):
    @classmethod
    def metadata(cls, metadata_json):
        client_dict = json.loads(json_data)
        return Client(**client_dict)
