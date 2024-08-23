import azure.functions as func
import logging

app = func.FunctionApp()

@app.cosmos_db_trigger(arg_name="azcosmosdb", container_name="PyDataShred_cosmos_container",
                        database_name="PyDataShred_cosmos_container_db", connection="undefined")  
def PyDataShred_cosmos(azcosmosdb: func.DocumentList):
    logging.info('Python CosmosDB triggered.')
    
