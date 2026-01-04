# Invoice-OCR-Server
This gRPC server digitizes documents like Invoices, POs, and SOs using a Multimodal VLM. It extracts data into a structured JSON response for seamless integration with any service. A key use case is its Odoo integration, where it automates ERP workflows by transforming images into validated records, eliminating manual data entry.
# 🚀 Multimodal Document Digitization Microservice

This high-performance gRPC service automates the digitization of unstructured business documents using the **InternVL** Vision-Language Model (VLM).

## 🌟 Key Features
- **Intelligent Extraction:** Optimized for document digitzation sush as **Invoices, Purchase Orders (PO), and Sales Orders (SO),...**.
- **Structured JSON Output:** Returns clean, machine-readable JSON for direct database mapping.
- **gRPC Architecture:** A language-agnostic microservice ensuring low-latency communication.
- **VLM-Powered:** Processes complex layouts and tables with human-like semantic understanding.

## 📂 Project Structure
```text
OCR_model/
├── exceptions/          
├── generated/           
├── InternVL3-1B-hf/    
├── model/               
├── protos/              
├── server/             
├── .env.local           
├── .gitmodules         
└── requirements.txt
```
| Folder / File | Responsibility | Contents |
| :--- | :--- | :--- |
| **`exceptions/`** | Error Management | Custom exception classes for model loading and inference failures. |
| **`generated/`** | gRPC Interface | Auto-generated Python code (`pb2` and `pb2_grpc`) based on the Proto definition. |
| **`InternVL3-1B-hf/`**| Model Weights | Git submodule containing the pre-trained weights and VLM configurations. |
| **`model/`** | Inference Logic | Python scripts for image preprocessing and model execution. |
| **`protos/`** | API Definition | The `model.proto` file defining the `ModelService` and message structures. |
| **`server/`** | Service Layer | Server-side implementation of the `ExtractOCR` RPC method. |
| **`.env.local`** | Configuration | Local environment variables for VLM paths and the maximum generated tokens. |
## 🛠️ Quick Start
1. **Clone:** `git clone --recursive [YOUR_REPO_URL]`
2. **Setup:** Create a `.env` with `MODEL_PATH=./InternVL3-1B-hf`
3. **Run:** `python server/server.py`.
