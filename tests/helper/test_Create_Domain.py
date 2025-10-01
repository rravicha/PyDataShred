
import os, sys
if os.uname().nodename == 'zebronics':
    sys.path.append('/home/susi/workspace/github/PyDataShred')
else:
    sys.path.append('/workspaces/PyDataShred')
    
from datashredpy.core.delegator import CreateEntity
def main():
    output = CreateEntity("domain", {
        "domain_name" : "sales"
    })
    print(dir(output))




if __name__ == "main":
    main()