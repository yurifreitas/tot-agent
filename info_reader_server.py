
from mcp.server.fastmcp import FastMCP
from openai import AzureOpenAI
from dotenv import load_dotenv
import os

load_dotenv()

AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")

client = AzureOpenAI(
    api_key=AZURE_OPENAI_API_KEY,
    api_version=AZURE_OPENAI_API_VERSION,
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
)
mcp = FastMCP("info_reader_server")

@mcp.tool(name="extract_info_from_image", description="Extrai info a partir de uma imagem via Azure OpenAI")
def extract_barcode_from_image(image_url: str) -> str:
    """Extrai informaçoes de uma imagem.
        Args:
            image_url: url de imagem
        Returns:
            Info image
        """
    messages = [{
        "role": "user",
        "content": [
            {
                "type": "image_url",
                "image_url": {
                    "url": image_url,
                    "detail": "auto"
                }
            },
            {
                "type": "text",
                "text": "Extraia info dessa imagem"
            }
        ]
    }]
    try:
        response = client.chat.completions.create(
            model=AZURE_OPENAI_DEPLOYMENT,
            messages=messages,
            temperature=0,
            max_tokens=300
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Erro ao processar imagem: {e}"

# Inicia o servidor MCP
if __name__ == "__main__":
    mcp.run(transport="stdio")