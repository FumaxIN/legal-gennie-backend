# Vendor-Management Backend

Backend system for managing Vendors and Purchase orders, built on [DRF](https://www.django-rest-framework.org/)

## Requirements

##### For running the script

**NOTE**: I have deployed Celery which seemed a better solution instead of Django signals. <br />
You can either install Docker for hassle-free setup, or install  Redis for conventional setup.


- [Python](https://www.python.org/downloads/)
- [Docker](https://docs.docker.com/get-docker/)
- [Redis](https://redis.io/download)


## Clone

* Use `git clone` to clone the repo
```bash
git clone git@github.com:FumaxIN/Vendor-Management.git
```

## Run

### Docker
```bash
docker build -t app .
docker run -d --name vendor-management -p 8000:8000 app
```

To run the tests in Docker setup, keep the container running and run the following commands in a new terminal:
```bash
 docker exec -it <CONTAINER ID> bash
 python manage.py test
```
(`Container ID` can be found using `docker ps`)

### Conventional Setup

* Create a virtual environment
```bash
python -m venv ./venv
source ./venv/bin/activate
```

* Install the requirements
```bash
  pip install -r requirements.txt
```
* Migrations
```bash
python manage.py migrate
```
* Run tests
```bash
python manage.py test
```
* Run server and start celery in a new terminal
```bash
python manage.py runserver
```
```bash
celery -A core.celery_app worker --beat --loglevel=info
```



## Swagger-Doc

**Note**: In each post request, `url` and `external_id` field are auto generated for navigation. <br />

### Auth Endpoints:
* **Login for existing employee**
    ```
    POST: /api/auth/login
    ```
   Request body:
    ```
    {
        "email": "testuser1@gmail.com",
        "password": "qwerty@123"
    }
    ```
   An `access` token will be returned. 
   Click the `Authorize` button at the top-right section of the swagger page and paste the token to login


* **Registration for a new employee**
    ```
    POST: /api/auth/register
    ```
    Request body:
    ```
    {
        "email": "user@example.com",
        "name": "Jane Smith",
        "password": "string",
        "password2": "string"
    }
    ```
  An `access` token will be returned.
  Click the `Authorize` button at the top-right section of the swagger page and paste the token to login

### Vendor endpoints

**Note:** Instead of `_id`, fields like `vendor_code`, `po_number`, etc. are used for navigation. To switch it to `_id`, change the `lookup_field` in the respective `views`.

* **Add a new vendor**
    ```
    POST: /api/vendors
    ```
    Request body:
    ```
    {
      "name": "Test Vendor",
      "address": "Delhi, India",
      "contact_details": "9876543210"
    }
    ```

* **Get vendors**
    ```
    GET: /api/vendors
    ```

* **Fetch a vendor** `/api/vendors/{vendor_code}`
    ```
    GET: /api/vendors/1f0afb51-c740-4d2b-8e0a-4fd99bbf7075
    ```


* **Update a vendor** `/api/vendors/{vendor_code}`
    ```
    PATCH: /api/vendor/1f0afb51-c740-4d2b-8e0a-4fd99bbf7075
    ```
  Request body:
    ```
    {
        "address": "Bangalore, India"
    }
    ```

* **Delete a vendor**
    ```
    DELETE: /api/vendors/{vendor_code}
    ```
  
* **Fetch performance of a vendor** `/api/vendors/{vendor_code}/performance`
    ```
    GET: /api/vendors/1f0afb51-c740-4d2b-8e0a-4fd99bbf7075/performance
    ```
  `avg_response_time` is stored in seconds which can be converted to any unit using serializers.


### Purchase Order endpoints
* **Assumptions:**
  - `issue_date` is set to the current date-time.
  - `status` is set to `Pending` by default.
  - There are separate endpoints for acknowledging, completing and cancelling a purchase order.


* **Create a new Purchase Order**
    ```
    POST: /api/purchase_orders
    ```
  Request body:
    ```
    {
      "vendor_id": "1f0afb51-c740-4d2b-8e0a-4fd99bbf7075",
      "items": {"item1":2, "item3":3},
      "delivery_date": "2024-05-05T09:20:56.260Z"
    }
    ```
  `quantity` gets calculated by adding the values of `items`. It can be supplied manually as well.


* **Get Purchase Orders**
    ```
    GET: /api/purchase_orders
    ```
  Params for filtering:
  * `?vendor_id=1f0afb51-c740-4d2b-8e0a-4fd99bbf7075`
  * `?vendor_name=Test`


* **Fetch a Purchase Order** `/api/purchase_orders/{po_number}`
    ```
    GET: /api/purchase_orders/40ce191c-65a5-44b2-8bd8-94705800e4a3
    ```

* **Update a PO** `/api/purchase_orders/{po_number}`
    ```
    PATCH: /api/purchase_orders/40ce191c-65a5-44b2-8bd8-94705800e4a3
    ```
  Request body:
    ```
    {
        "items": {"item1":3, "item2":4, "item3":5}
    }
    ```

* **Delete a PO** `/api/purchase_orders/{po_number}`
    ```
    DELETE: /api/purchase_orders/40ce191c-65a5-44b2-8bd8-94705800e4a3
    ```
  
* **Acknowledge a PO** `/api/purchase_orders/{po_number}/acknowledge`
    ```
    POST: /api/purchase_orders/40ce191c-65a5-44b2-8bd8-94705800e4a3/acknowledge
    ```
  
* **Complete a PO** `/api/purchase_orders/{po_number}/complete`
    ```
    POST: /api/purchase_orders/40ce191c-65a5-44b2-8bd8-94705800e4a3/complete
    ```
  Request body:
    ```
    {
        "quality_rating": 8
    }
    ```
  
* **Cancel a PO** `/api/purchase_orders/{po_number}/cancel`
    ```
    POST: /api/purchase_orders/40ce191c-65a5-44b2-8bd8-94705800e4a3/cancel
    ```