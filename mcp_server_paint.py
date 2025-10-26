# -------------------------------
# MCP Server for controlling Paint
# -------------------------------

from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent
from pywinauto.application import Application
import subprocess
import win32gui
import win32con
import time
import sys
import pyautogui

# Instantiate MCP server
mcp = FastMCP("Painter")
paint_app = None  # global reference to Paint app


# -------------------------------
# TOOLS
# -------------------------------


# 🧭 Update this with your actual pinned Paint icon coordinates
PAINT_ICON_X = 850 # example
PAINT_ICON_Y = 1055  # example

@mcp.tool()
async def open_paint() -> dict:
    """Open Microsoft Paint if not open, by clicking pinned icon; maximize it"""
    global paint_app
    try:
        # Try connecting to existing Paint instance
        try:
            paint_app = Application().connect(path="mspaint.exe")
            paint_window = paint_app.window(class_name="MSPaintApp")
            win32gui.ShowWindow(paint_window.handle, win32con.SW_MAXIMIZE)
            return {
                "content": [
                    TextContent(
                        type="text",
                        text="🎨 Paint is already open and maximized."
                    )
                ]
            }
        except Exception:
            pass  # not open, will try to launch via click

        # Click the pinned Paint icon on the taskbar
        pyautogui.click(PAINT_ICON_X, PAINT_ICON_Y)
        time.sleep(2)  # allow it to launch

        # Try to connect again
        for _ in range(10):
            try:
                paint_app = Application().connect(path="mspaint.exe")
                paint_window = paint_app.window(class_name="MSPaintApp")
                win32gui.ShowWindow(paint_window.handle, win32con.SW_MAXIMIZE)
                return {
                    "content": [
                        TextContent(
                            type="text",
                            text="✅ Paint launched via pinned icon and maximized."
                        )
                    ]
                }
            except Exception:
                time.sleep(0.3)

        return {
            "content": [
                TextContent(
                    type="text",
                    text="⚠️ Clicked Paint icon but could not connect within timeout."
                )
            ]
        }

    except Exception as e:
        return {
            "content": [
                TextContent(type="text", text=f"❌ Error opening Paint: {e}")
            ]
        }

# @mcp.tool()
# async def open_paint() -> dict:
#     """Open Microsoft Paint maximized and keep it open independently"""
#     global paint_app
#     try:
#         # Detach flags to keep Paint alive after MCP process ends
#         DETACHED_PROCESS = 0x00000008
#         CREATE_NEW_PROCESS_GROUP = 0x00000200

#         # Check if Paint is already open
#         try:
#             paint_app = Application().connect(path="mspaint.exe")
#             paint_window = paint_app.window(class_name="MSPaintApp")
#             win32gui.ShowWindow(paint_window.handle, win32con.SW_MAXIMIZE)
#             return {
#                 "content": [
#                     TextContent(
#                         type="text",
#                         text="🖌️ Paint is already open and maximized."
#                     )
#                 ]
#             }
#         except Exception:
#             pass  # not open yet, continue to launch

#         # Launch Paint in detached mode so it persists
#         subprocess.Popen(
#             ["mspaint.exe"],
#             creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP,
#             close_fds=True
#         )

#         # Give Paint time to start before connecting
#         time.sleep(2)

#         # Connect via pywinauto
#         paint_app = Application().connect(path="mspaint.exe")
#         paint_window = paint_app.window(class_name="MSPaintApp")
#         win32gui.ShowWindow(paint_window.handle, win32con.SW_MAXIMIZE)

#         return {
#             "content": [
#                 TextContent(
#                     type="text",
#                     text="✅ Paint opened successfully and will stay open after the tool exits."
#                 )
#             ]
#         }

#     except Exception as e:
#         return {
#             "content": [
#                 TextContent(type="text", text=f"❌ Error opening Paint: {e}")
#             ]
#         }


@mcp.tool()
async def draw_rectangle(x1: int, y1: int, x2: int, y2: int) -> dict:
    """Draw a rectangle in Paint from (x1,y1) to (x2,y2)"""
    global paint_app
    try:
        if not paint_app:
            return {"content": [TextContent(type="text", text="Call open_paint first.")]}

        paint_window = paint_app.window(class_name='MSPaintApp')
        if not paint_window.has_focus():
            paint_window.set_focus()
            time.sleep(0.2)

        # Click Rectangle tool
        paint_window.click_input(coords=(439, 66))
        time.sleep(0.2)

        # Draw rectangle
        canvas = paint_window.child_window(class_name='MSPaintView')
        canvas.press_mouse_input(coords=(x1, y1))
        canvas.move_mouse_input(coords=(x2, y2))
        canvas.release_mouse_input(coords=(x2, y2))

        return {"content": [TextContent(type="text", text=f"Rectangle drawn ({x1},{y1}) -> ({x2},{y2})")]}
    except Exception as e:
        return {"content": [TextContent(type="text", text=f"Error: {e}")]}


@mcp.tool()
async def add_text_in_paint(text: str, x1: int = 700, y1: int = 350) -> dict:
    """Add text in Paint"""
    global paint_app
    try:
        if not paint_app:
            return {"content": [TextContent(type="text", text="Call open_paint first.")]}

        paint_window = paint_app.window(class_name='MSPaintApp')
        if not paint_window.has_focus():
            paint_window.set_focus()
            time.sleep(0.2)

        # Click Text tool
        paint_window.click_input(coords=(292, 69))
        time.sleep(0.2)

        # Click canvas to start typing
        canvas = paint_window.child_window(class_name='MSPaintView')
        canvas.click_input(coords=(x1, y1))
        time.sleep(0.2)

        # Type the text
        paint_window.type_keys(text, with_spaces=True)
        time.sleep(0.2)

        # Click outside to exit text mode
        canvas.click_input(coords=(88, 33))

        return {"content": [TextContent(type="text", text=f"Text '{text}' added.")]}
    except Exception as e:
        return {"content": [TextContent(type="text", text=f"Error: {e}")]}

@mcp.tool()
async def fill_color_in_paint(x: int = 400, y: int = 400) -> dict:
    """Fill a color in Paint at given coordinates"""
    global paint_app
    try:
        color_x = 872
        color_y= 62
        if not paint_app:
            return {"content": [TextContent(type="text", text="Call open_paint first.")]}

        paint_window = paint_app.window(class_name='MSPaintApp')
        if not paint_window.has_focus():
            paint_window.set_focus()
            time.sleep(0.2)

        # Select 'Fill with color' tool (bucket icon)
        paint_window.click_input(coords=(268, 67))  # Approx tool location
        time.sleep(0.5)

        # Optionally select a color from color palette
        paint_window.click_input(coords=(color_x, color_y))  # Adjust palette color position
        time.sleep(0.5)

       
        # Click canvas area to fill color
        canvas = paint_window.child_window(class_name='MSPaintView')
        canvas.click_input(coords=(x, y))
        time.sleep(0.5)

         # Select 'Fill with color' tool (bucket icon)
        paint_window.click_input(coords=(762, 60))  # Approx tool location
        time.sleep(0.5)


        return {"content": [TextContent(type="text", text=f"Color filled at ({x}, {y}).")]}
    except Exception as e:
        return {"content": [TextContent(type="text", text=f"Error: {e}")]}


# -------------------------------
# RUN SERVER
# -------------------------------

if __name__ == "__main__":
    # Run MCP server
    if len(sys.argv) > 1 and sys.argv[1] == "dev":
        mcp.run()
    else:
        mcp.run(transport="stdio")
