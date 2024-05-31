# Facturación Electrónica API
This Django project implements an API for electronic invoicing system. It provides endpoints to manage users, companies, invoices, products, clients, and more.

## Installation
1. Clone the Repository
  ```bash
  git clone <repository-url>
  cd <project-folder>
  ```
2. Set Up Environment
Create a virtual environment and activate it:
  ```bash
  python3 -m venv venv
  source venv/bin/activate  # On Windows, use venv\Scripts\activate
  ```
3. Install Dependencies
Install the required Python packages using pip:
  ```bash
  pip install -r requirements.txt
  ```
4. Set Up Database
Configure your database settings in settings.py. By default, this project uses SQLite.
Apply migrations to create database schema:
  ```bash
  python manage.py migrate
  ```
5. Run the Server
Start the Django development server:
  ```bash
  python manage.py runserver
  ```
The API will be accessible at http://127.0.0.1:8000/.

## Usage
### API Endpoints
- CerrarFacturaView: Close invoices and generate PDF/XML documents.
- FormaPagoView: Retrieve or create payment methods.
- ProductoEstrellaView: Get the top-selling product for a company.
- ClienteEstrellaView: Get the top-spending client for a company.
### Classes
- Factura: Model representing invoices.
- Detalle_factura: Model representing invoice details.
- Empresa: Model representing companies.
- Usuario: Model representing users.
- Producto: Model representing products.
- Cliente: Model representing clients.
- Forma_pago: Model representing payment methods.
- Documento: Model representing generated documents (PDF/XML).
### Dependencies
- Django: Web framework for building APIs.
- reportlab: Library for generating PDF documents.
- cryptography: Library for handling encryption and signing.
- signxml: Library for XML signing and verification.
- suds: Library for consuming SOAP web services.
