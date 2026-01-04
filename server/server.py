import grpc
from concurrent import futures
from model.ocr_model import OCRModel
from generated import model_pb2,model_pb2_grpc
import os
from dotenv import load_dotenv
from PIL import Image
import io

load_dotenv()

MODEL_PATH = os.getenv("MODEL_PATH")
MAX_TOKENS = int(os.getenv("MAX_TOKENS"))
PORT = int(os.getenv('GRPC_PORT'))
HOST = os.getenv('GRPC_HOST')

class ModelServer(model_pb2_grpc.ModelServiceServicer):
    """
    gRPC Servicer that handles Client requests.

    This class implements the ModelService defined in the proto files, 
    linking gRPC network calls to the our model.
    """
    def __init__(self):
        """
        Initializes the ModelServer by instantiating the OCRModel.
        """
        self.model = OCRModel(MODEL_PATH,MAX_TOKENS)
    
    def ExtractOCR(self, request, context):
        """
        RPC method to process an image and extract text fields.

        Args:
            request (model_pb2.ModelRequest): The incoming gRPC request containing:
                - image: the image file.
                - prompt: text instructions.

            context (grpc.ServicerContext): Contextual information about the RPC.

        Returns:
            model_pb2.ModelResponse: A protobuf message containing the extracted text.
        """

        print("An Image Received")
        bytes= request.image
        prompt = request.prompt
        image = Image.open(io.BytesIO(bytes)).convert("RGB")
        output = self.model.extract_fields(image,prompt)

        response = model_pb2.ModelResponse(output = output)
        return response


def serve():
    """
    Configures and starts the gRPC server.
    
    - Initializes a ThreadPoolExecutor for handling concurrent requests.
    - Binds the ModelServer to port 50051.
    - Keeps the process alive until manual termination.
    """
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=2))
    model_pb2_grpc.add_ModelServiceServicer_to_server(ModelServer(), server)
    server.add_insecure_port(f"{HOST}:{PORT}")
    print(f"gRPC server running on port {PORT} ...")
    server.start()
    server.wait_for_termination()


if __name__ =="__main__":
    serve()