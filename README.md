## Address Server

Python requirements (Flask and dependencies) are in `requirements.txt`

### Rest Endpoints

#### Add Addresses

**POST** to `server/create` use the parameter `address-block` to specify the CIDR block

### Acquire Address
**POST** to `server/acquire` use the parameter `address` to specify the address

### Release Address
**POST** to `server/release` use the parameter `address` to specify the address

### List Addresses
**GET** to `server/list` to retrieve a list of addresses. They will be listed under the `data` element of the returned JSON.