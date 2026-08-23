
import os, sys
    
from datashredpy.core.delegator import CreateEntity
def main():
    output = CreateEntity("domain", {
        "domain_name" : "sales"
    })
    print(dir(output))




if __name__ == "main":
    main()