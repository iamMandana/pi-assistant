from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration
from transformers import AutoProcessor, AutoModelForCausalLM
import torch
import time
import os

class VisionModel:
    def __init__(self):
        print("Loading vision model...")
        start = time.time()

        # Model selection
        #self.MODE = "llava_cloud"
        self.MODE = "blip_base"
        #self.MODE = "blip_large"
        #self.MODE = "git_base" 

        # BLIP BASE model
        if self.MODE == "blip_base":
            self.processor = BlipProcessor.from_pretrained(
                "Salesforce/blip-image-captioning-base"
            )
            self.model = BlipForConditionalGeneration.from_pretrained(
                "Salesforce/blip-image-captioning-base"
            )

        # Larger BLIP model
        elif self.MODE == "blip_large":
            self.processor = BlipProcessor.from_pretrained(
                "Salesforce/blip-image-captioning-large"
            )
            self.model = BlipForConditionalGeneration.from_pretrained(
                "Salesforce/blip-image-captioning-large"
            )

        # GIT model
        elif self.MODE == "git_base":
            self.processor = AutoProcessor.from_pretrained(
                "microsoft/git-base-coco"
            )
            self.model = AutoModelForCausalLM.from_pretrained(
                "microsoft/git-base-coco"
            )

        # Cloud-based model
        elif self.MODE == "llava_cloud":
            import google.generativeai as genai
            genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

            # Uses Gemini model via API
            self.cloud_model = genai.GenerativeModel("gemini-2.5-flash")

        print(f"Vision model loaded in {time.time() - start:.2f}s")
        
        
        
    def describe(self, image_path):
        try:
            # Load image from disk (blocking I/O)
            image = Image.open(image_path).convert("RGB")

            # BLIP inference 
            if self.MODE in ["blip_base", "blip_large"]:
                inputs = self.processor(image, return_tensors="pt")
                out = self.model.generate(**inputs)
                caption = self.processor.decode(out[0], skip_special_tokens=True)
                return caption

            # GIT inference
            elif self.MODE == "git_base":
                inputs = self.processor(
                    images=image,
                    text="describe the image",
                    return_tensors="pt"
                )
                out = self.model.generate(**inputs)
                caption = self.processor.decode(out[0], skip_special_tokens=True)
                return caption

            # Cloud inference
            elif self.MODE == "llava_cloud":
                return self._describe_with_cloud(image)

            else:
                return "Unknown vision mode"

        except Exception as e:
            return f"Vision error: {e}"

    def _describe_with_cloud(self, image):
        try:
            t0 = time.time()

            # Sends both instruction and image to cloud model
            response = self.cloud_model.generate_content([
                "Describe this image briefly.",
                image
            ])

            t1 = time.time()
            print(f"[CLOUD GEMINI] latency={t1 - t0:.2f}s")

            # Basic validation of response
            if not response or not response.text:
                return "Cloud vision error: empty response"

            return response.text

        except Exception as e:
            # Same pattern: suppresses exception and returns string
            return f"Cloud vision error: {e}"


vision_model = VisionModel()        
