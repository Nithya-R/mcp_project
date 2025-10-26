import os
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import asyncio
from google import genai

# -------------------------------
# Load environment variables
# -------------------------------
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env file")

gemini_client = genai.Client(api_key=GEMINI_API_KEY)

# -------------------------------
# Global iteration settings
# -------------------------------
MAX_ITERATIONS = 10
last_response = None
iteration_response = []

# -------------------------------
# Helper: LLM generate with timeout
# -------------------------------
async def generate_with_timeout(client, prompt, timeout=15):
    """Generate content from Gemini 2.0 Flash model with timeout."""
    loop = asyncio.get_event_loop()
    try:
        response = await asyncio.wait_for(
            loop.run_in_executor(
                None,
                lambda: client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=prompt
                )
            ),
            timeout=timeout
        )
        return response.text.strip()
    except asyncio.TimeoutError:
        print("LLM generation timed out!")
        return None
    except Exception as e:
        print(f"Error in LLM generation: {e}")
        return None

# -------------------------------
# Main client loop
# -------------------------------
async def main():
    print("Starting MCP Client with Gemini 2.0 Flash integration...")

    server_params = StdioServerParameters(
        command="python",
        args=["mcp_server_paint.py"]
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools_result = await session.list_tools()
            tools = tools_result.tools
            if not tools:
                print("No tools available on server. Exiting.")
                return

            # Build tool description for system prompt
            tools_description = []
            for i, tool in enumerate(tools):
                try:
                    params = tool.inputSchema
                    desc = getattr(tool, "description", "No description")
                    name = getattr(tool, "name", f"tool_{i}")
                    if "properties" in params:
                        param_list = [f"{k}:{v.get('type','unknown')}" for k, v in params["properties"].items()]
                        param_str = ", ".join(param_list)
                    else:
                        param_str = "no parameters"
                    tools_description.append(f"{i+1}. {name}({param_str}) - {desc}")
                except Exception:
                    tools_description.append(f"{i+1}. Error reading tool")
            tools_description_text = "\n".join(tools_description)

            # System prompt template
            system_prompt = f"""You are an agent controlling Microsoft Paint via MCP tools.
Available tools:
{tools_description_text}

Rules:
- Only call one function per response.
- Parameters must match the tool's input schema.
- All X and Y coordinates must be within: X:20-1800, Y:200-900.
- Start with 'open_paint', then draw rectangles, then add text.
- Use 'draw_rectangle' for rectangles and 'add_text_in_paint' for text.
- Respond with EXACTLY ONE of these formats:
1. FUNCTION_CALL: function_name|param1|param2|...
2. FINAL_ANSWER: done
"""

            # ---------------------------
            # User query (changeable)
            # ---------------------------
            global last_response
            iteration = 0
            query = """ Here are some steps and instructions to follow. 
                    1. Open Paint, draw only 1 rectangle with medium height and good width.
                    2. Colour inside the rectange.
                    3. write 'School of AI' in the middle of that rectangle. Give the coordinates accordingly. 
                    When giving the coordinates for the text, make sure it is inside the rectange and is in the center of the rectange that was drawn earlier."""

            while iteration < MAX_ITERATIONS:
                print(f"\n--- Iteration {iteration + 1} ---")
                if last_response is None:
                    current_query = query
                else:
                    current_query = query + "\n" + " ".join(iteration_response) + " What should I do next?"

                prompt = f"{system_prompt}\nQuery: {current_query}"
                response_text = await generate_with_timeout(gemini_client, prompt, timeout=20)
                if not response_text:
                    print("No response from LLM, stopping.")
                    break

                print(f"LLM Response: {response_text}")

                # ---------------------------
                # Handle LLM response
                # ---------------------------
                response_text = response_text.strip()

                # Normalize response: remove leading numbers or spaces
                import re
                response_text = re.sub(r"^\d+\.\s*", "", response_text)

                if response_text.startswith("FUNCTION_CALL:"):
                    _, function_info = response_text.split("FUNCTION_CALL:", 1)
                    function_info = function_info.strip()
                    parts = [p.strip() for p in function_info.split("|")]
                    func_name, params = parts[0], parts[1:]

                    tool = next((t for t in tools if t.name == func_name), None)
                    if not tool:
                        print(f"Unknown tool: {func_name}")
                        break

                    # Map parameters to correct types
                    arguments = {}
                    if "properties" in tool.inputSchema:
                        for (param_name, param_info), value in zip(tool.inputSchema["properties"].items(), params):
                            type_ = param_info["type"]
                            if type_ == "integer":
                                arguments[param_name] = max(20, min(1800, int(value))) if 'x' in param_name else max(200, min(900, int(value)))
                            elif type_ == "number":
                                arguments[param_name] = float(value)
                            elif type_ == "array":
                                arguments[param_name] = eval(value)
                            else:
                                arguments[param_name] = value

                    print(f"Calling MCP tool {func_name} with {arguments}")
                    result = await session.call_tool(func_name, arguments=arguments)

                    if hasattr(result, "content") and result.content:
                        if isinstance(result.content[0], str):
                            iteration_result = result.content[0]
                        else:
                            iteration_result = result.content[0].text
                    else:
                        iteration_result = str(result)

                    iteration_response.append(
                        f"Iteration {iteration+1}: called {func_name}({arguments}), result={iteration_result}"
                    )
                    last_response = iteration_result
                    print(f"Tool result: {iteration_result}")

                elif response_text.startswith("FINAL_ANSWER:"):
                    print("\n=== Final Answer Received ===")
                    print(response_text)
                    break

                else:
                    print("LLM response not recognized. Stopping.")
                    break

                iteration += 1

    print("Client execution complete.")

# -------------------------------
# Run client
# -------------------------------
if __name__ == "__main__":
    asyncio.run(main())
