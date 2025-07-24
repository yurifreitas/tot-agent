curl -X POST http://localhost:8000/runs \
  -H "Content-Type: application/json" \
  -d '{
    "agent_name": "multi_step_agent",
    "input": [
      {
        "role": "user",
        "parts": [
          {
            "content": "Leia as infos dessa imagen: https://lh7-rt.googleusercontent.com/docsz/AD_4nXdpK2zHbFKJOysyQKHioIs0walFWRkF4ofSG4F3UoN9NaPHc4Rt-9suiJXy1RFMzo7VI31nSChlnn-KjWQHMbZfXB4jFiF5GmaslBa1BAY5ZPMOPpnn-qWGNR8vE-Ovk1LbeDVUeBVLUZGP1QPN1sQOafsK?key=EYqhVGgK_DvkU9gLMkh-5A"
          }
        ]
      }
    ]
  }'

