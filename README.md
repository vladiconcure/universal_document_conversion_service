# Universal Document Conversion Service

Generated by LLM :) Vibe coding!11

A REST API service for converting documents between various formats using LibreOffice's UNO API.

## Features

- RESTful API using FastAPI
- Supports various document formats (PDF, DOCX, ODT, XLSX, ODS, PPTX, ODP, etc.)
- Docker deployment ready
- Kubernetes deployment support
- Simple file upload and download interface
- Health check endpoint
- Background task for file cleanup

## Installation

### Prerequisites

- Python 3.8 or higher
- LibreOffice
- Python UNO bridge

### Local Installation

1. Install LibreOffice and Python UNO:

```bash
sudo apt-get update
sudo apt-get install -y libreoffice python3-uno
```

2. Add UNO to Python path:

```bash
uno_path=$(find /usr -name "uno.py" 2>/dev/null | head -1 | xargs dirname)
echo "$uno_path" > $(python3 -c "import site; print(site.getsitepackages()[0])")/libreoffice.pth
python3 -c "import uno; print('PyUNO is available')"
```

3. Install Python dependencies:

```bash
pip install -r requirements.txt
```

4. Run LibreOffice in headless mode:

```bash
soffice --headless --accept="socket,host=localhost,port=2002;urp;StarOffice.ServiceManager" &
```

5. Start the FastAPI server:

```bash
uvicorn app:app --reload
```

## Docker Deployment

The simplest way to deploy is using Docker and Docker Compose:

1. Make sure Docker and Docker Compose are installed:

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

2. Create data directories:

```bash
mkdir -p ./data/uploads ./data/output
chmod -R 777 ./data
```

3. Build and run using Docker Compose:

```bash
docker-compose up -d
```

4. Or use the provided deployment script:

```bash
chmod +x deploy.sh
./deploy.sh
```

## Kubernetes Deployment

To deploy on a Kubernetes cluster:

1. Build and push the Docker image:

```bash
docker build -t your-registry/document-converter:latest .
docker push your-registry/document-converter:latest
```

2. Update the Kubernetes deployment file with your image:

```bash
# In kubernetes-deployment.yaml, change:
image: document-converter:latest
# to:
image: your-registry/document-converter:latest
```

3. Apply the Kubernetes manifests:

```bash
kubectl apply -f kubernetes-deployment.yaml
```

## API Usage

Once the service is running, you can access:

- API documentation: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`

### Converting a Document

Send a POST request to `/convert/` with:

- `file`: The document file to convert
- `output_format`: The desired output format (pdf, docx, odt, etc.)

Example with curl:

```bash
curl -X POST "http://localhost:8000/convert/" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/your/document.docx" \
  -F "output_format=pdf" \
  --output "converted_document.pdf"
```

## Supported Formats

- PDF: `pdf`
- Word Document: `docx`
- OpenDocument Text: `odt`
- Excel Spreadsheet: `xlsx`
- OpenDocument Spreadsheet: `ods`
- PowerPoint Presentation: `pptx`
- OpenDocument Presentation: `odp`

## Production Considerations

For production environments, consider the following:

1. **Security**:
   - Add authentication/authorization
   - Implement rate limiting
   - Scan uploaded files for malware
   - Use HTTPS with a proper SSL certificate

2. **Scaling**:
   - Deploy multiple instances behind a load balancer
   - Use a shared storage solution for file storage
   - Implement a job queue for processing documents

3. **Monitoring**:
   - Set up logging with Elasticsearch, Fluentd, and Kibana (EFK) or similar
   - Implement monitoring with Prometheus and Grafana
   - Configure alerts for service health and performance issues

4. **Backup and Recovery**:
   - Regular backups of the data volume
   - Implement disaster recovery procedures

## License

[MIT License](LICENSE)
