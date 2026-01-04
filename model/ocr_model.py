from transformers import AutoProcessor, AutoModelForImageTextToText
import torch
from typing import List,Dict
from exceptions.model_exception import ModelFailedToLoadException
import re
class OCRModel :
    """
    A wrapper class for our VLMdesigned to perform structured field extraction.

    Attributes:
        device : The device being used for inference ('cuda' or 'cpu').
        processor : The Hugging Face processor for multimodal inputs.
        model : The pre-trained model instance.
        max_tokens : Maximum number of new tokens to generate during inference.
    """
    def __init__(self,model_path:str,generated_tokens:int=64):
        try :
            # Check GPU availability 
            self.device  = "cuda" if torch.cuda.is_available() else "cpu"
            # set the processor
            self.processor = AutoProcessor.from_pretrained(model_path,local_files_only=True,trust_remote_code=True)
            # set the model 
            self.model  = AutoModelForImageTextToText.from_pretrained(model_path,dtype=torch.bfloat16,local_files_only=True,trust_remote_code=True).to(self.device)
            # Set pad token to eos token
            self.processor.tokenizer.pad_token = self.processor.tokenizer.eos_token
            # set the amount of generated tokens
            self.max_tokens = generated_tokens
            # sey the model in the inference mode 
            self.model.eval()

        # Raise Exception if failed
        except Exception as e :
            raise ModelFailedToLoadException()  from e
    


    def set_message_template(self,image,prompt) ->List[Dict]:
        """
        Generate the approptiate template acceptable by the model .

        Args:
            image  The image to be processed.
            prompt : The text instructions/query for the model.

        Returns:
            List[Dict]: A list of dictionaries representing the user message structure.
        """
        return [{
            "role": "user",
            "content": [
                {"type": "image", "image": image},
                {"type": "text", "text": prompt},
                ]
            }]
    

    def extract_fields(self,image,prompt) -> str:
        """
        Processes an image and a prompt to extract specific information using the VLM.

        This method handles the full inference pipeline: 
              1 - preprocessing.
              2 - extraction.
              3- response cleaning 

        Args:
            image : The input image .
            prompt : The prompt defining which fields to extract.

        Returns:
            str: The cleaned, decoded string output from the model .
        """
        message = self.set_message_template(image,prompt)
        # Transform input to tensor (image -> visual_tokends) / (text -> tokens)
        inputs = self.processor.apply_chat_template(message,add_generation_prompt=True, 
                                                   tokenize=True, 
                                                   return_dict=True, 
                                                   return_tensors="pt"
                                                   ).to(self.model.device, dtype=torch.bfloat16)
        with torch.no_grad():
            generate_ids = self.model.generate(**inputs, max_new_tokens=self.max_tokens,
                                      pad_token_id=self.processor.tokenizer.pad_token_id)
        # Skip the input tokens (the inputs_ids is tensor of dimension : batch_size x prompt_length)
        input_ids = inputs["input_ids"].shape[1]
        output = generate_ids[0,input_ids:]
        # return the decoded output 
        output_decoded = self.processor.decode(output,skip_special_tokens=True)
        cleaned_output = self.clean_output(output_decoded)
        return cleaned_output
    
    def clean_output(self,text):
        """
        Clean the raw model string to extract and sanitize content.

        It removes Markdown JSON blocks and strips leading zeros from numeric 
        values to ensure valid python formatting.

        Args:
            text : The output.

        Returns:
            str: The cleaned string.
        """
        model_output = text.strip()  # remove leading/trailing spaces
        if model_output.startswith("```json"):
            model_output = model_output.split("```json")[1].split("```")[0].strip()
            # Delering leading zeros since python doesn't support them 
            clean_output = re.sub(r'": 0+(\d+)', r'": \1', model_output)
        return clean_output