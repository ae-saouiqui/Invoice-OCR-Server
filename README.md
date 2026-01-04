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


### 📜 Proto File Definition

The `.proto` file acts as a **contract** between the client and the server. It defines the communication rules and ensures that data sent by the client is perfectly understood by the AI server. It uses a binary format that is much faster and more efficient than standard HTTP/JSON.



#### 📊 Message & Service Summary

| Component | Type | Description |
| :--- | :--- | :--- |
| **`ModelService`** | Service | The main interface that handles OCR and extraction requests. |
| **`ExtractOCR`** | Method | The specific function (RPC) called to trigger the VLM inference. |
| **`image`** | `bytes` | The raw binary data of the document (JPG, PNG, or PDF scan). |
| **`prompt`** | `string` | Natural language instructions (e.g., "Extract total and date"). |
| **`output`** | `string` | The VLM's response, typically formatted as a structured JSON string. |
---
### 🛠️ Quick Start 
Follow these steps to set up the microservice on your local machine.
#### 1. Clone the Project
You must clone recursively to download the **InternVL** model weights along with the source code:
```
git clone --recursive https://github.com/ae-saouiqui/Invoice-OCR-Server.git
cd Invoice-OCR-Server
```
#### 2. Create the environment
```shell
python -m venv vlm-env
```
#### 3. Activate it 
> For linux/Max :
```
./vlm-env/bin/activate
```
> For Windows :
```
.\vlm-env\Scripts\activate
```
#### 3. Install Dependencies :
Install the required AI frameworks and gRPC tools:
```
pip install -r requirements.txt
```
#### 4. Generate gRPC Stubs:
Compile the `.proto` definitions into the `generated/` folder so the Python server can use them:
```shell
python -m grpc_tools.protoc -I./protos --python_out=./generated --grpc_python_out=./generated ./protos/model.proto
```
#### 5. ⚙️ Environment Configuration (`.env`) : 

To generalize the server connection and model behavior, the following environment variables are used. The server is configured to use safe defaults if these are not explicitly provided.

| Variable | Default Value | Description |
| :--- | :--- | :--- |
| **`GRPC_HOST`** | `[::]` | The network interface the server binds to. `[::]` allows universal access (IPv4/IPv6). |
| **`GRPC_PORT`** | `50051` | The port used for gRPC communication. |
| **`MODEL_PATH`** | *Required* | The absolute local path to your `InternVL3-1B-hf` folder. |
| **`MAX_TOKENS`** | `default : 1024` | The maximum number of tokens the VLM can generate in its JSON response. |

#### 5. Run the Server : 
Ensure your `.env.local` is configured with the correct `MODEL_PATH` and `MAX_TOKENS`, then start the service:
```
python -m server.server
```
If the server initializes and receives a request correctly, your terminal will look like this:
```
gRPC server running on port 50051 ...
An Image Received
```
> __Note:__ The `"An Image Received"` message appears every time a client _(like Odoo or your test script)_ successfully sends a document for processing.
> 
## 🚀 Usage

Once the server is running, you can interact with it using a gRPC client. Below is a simple implementation of a Python client to test the OCR extraction.

### Basic Python Client (`test_client.py`)

```python
import grpc
import os
from generated import model_pb2, model_pb2_grpc

class ModelClient:
    def __init__(self, host="localhost", port=50051):
        # Create a communication channel to the server
        self.channel = grpc.insecure_channel(f"{host}:{port}")
        # Bind the client to the service definition
        self.stub = model_pb2_grpc.ModelServiceStub(self.channel)

    def extract_ocr(self, image_path, prompt):
        # Read the image as binary bytes
        with open(image_path, "rb") as f:
            image_bytes = f.read()

        # Build the gRPC request
        request = model_pb2.UserRequest(
            image=image_bytes,
            prompt=prompt
        )

        # Call the server and return the response
        response = self.stub.ExtractOCR(request)
        return response.output

if __name__ == "__main__":
    client = ModelClient()
    
    # Path to your sample document
    IMAGE_PATH = "invoice_sample.jpg" 
    PROMPT = "Extract all fields into a structured JSON."

    if os.path.exists(IMAGE_PATH):
        print(f"📡 Sending request...")
        result = client.extract_ocr(IMAGE_PATH, PROMPT)
        print("\n✅ Extracted Data:")
        print(result)
    else:
        print(f"❌ Error: {IMAGE_PATH} not found.")
```
### ⚠️ Troubleshooting : 
| Issue | Cause | Solution |
| :--- | :--- | :--- |
| **`OutOfMemoryError` (CUDA)** | GPU VRAM is insufficient for the 1B model. | Quantize the model before running inference. |
| **Empty `InternVL` folder** | Cloned without the `--recursive` flag. | Run `git submodule update --init --recursive` in the root folder. |
| **`ModuleNotFoundError`** | gRPC stubs were not generated in `generated/`. | Ensure you ran the `protoc` command in [Step 4](#4-generate-grpc-stubs) of the Quick Start. |

## 🔗 References & Documentation

This microservice is a core component of a larger ecosystem. For further details on the implementation and the underlying model, refer to the links below:

| Project | Logo | Description | Link |
| :--- | :---: | :--- | :--- |
| **Invoice OCR Integration** | <img src="" width="100" height="100"> | The main project utilizing this service for automated ERP workflows. | [View Project]([https://github.com/ae-saouiqui/Invoice-OCR-Server](https://github.com/Amal-dadda/Ocr-odoo.git)) |
| **InternVL Official** | <img width="100" height="100" alt="image" src="https://github.com/user-attachments/assets/586ce225-9929-4641-9302-253744c42ffd" />| The official repository for the InternVL family of models. | [Open-MMLab/InternVL](https://github.com/OpenGVLab/InternVL) |

---

### 📖 Further Reading
* **gRPC Documentation:** Learn more about the [gRPC Python implementation](https://grpc.io/docs/languages/python/).
* **HuggingFace InternVL:** Access the [1B model weights](https://huggingface.co/OpenGVLab/InternVL2-1B).


---

## ✉️ Contact & Support

If you have any questions, run into issues, or want to collaborate on this OCR project, feel free to reach out!

* **📧 Email:** [amineessaouiqui2@gmail.com](mailto:amineessaouiqui2@gmail.com)
* **🔗 LinkedIn:** [Amine Es-saouiqui](https://linkedin.com/in/your-profile](https://www.linkedin.com/in/amine-es-saouiqui))
* **💻 GitHub:** [ae-saouiqui](https://github.com/ae-saouiqui)

---

### ❤️ Final Word

> "Innovation is the result of curiosity and collaboration. Thank you for exploring this project and contributing to the future of automated document processing!"

**Happy Coding! 🚀**

---
