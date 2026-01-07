"""
Mental Health Support Chatbot - Gradio Interface
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import gradio as gr
from src.pipeline import get_pipeline


WELCOME = "Hi there! 👋 I'm here to listen and support you. How are you feeling today?"


def create_chatbot():
    """Create Gradio chatbot."""
    
    pipeline = None
    
    def get_or_init_pipeline():
        nonlocal pipeline
        if pipeline is None:
            pipeline = get_pipeline()
        return pipeline
    
    def respond(message, history):
        if not message.strip():
            return history, ""
        
        try:
            p = get_or_init_pipeline()
            response = p.chat(message)
        except Exception as e:
            response = f"I'm having a moment. Could you try again? 💙"
        
        # Gradio 6.x format
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": response})
        return history, ""
    
    def clear():
        nonlocal pipeline
        if pipeline:
            pipeline.reset()
        return [{"role": "assistant", "content": WELCOME}], ""
    
    # Build UI
    with gr.Blocks(title="Mental Health Support") as demo:
        
        gr.Markdown("# 🧠 Mental Health Support")
        
        chatbot = gr.Chatbot(
            value=[{"role": "assistant", "content": WELCOME}],
            height=450,
        )
        
        with gr.Row():
            msg = gr.Textbox(
                placeholder="Share what's on your mind...",
                show_label=False,
                scale=9,
            )
            send = gr.Button("Send", variant="primary", scale=1)
        
        clear_btn = gr.Button("🗑️ New Conversation", size="sm")
        
        # Events
        msg.submit(respond, [msg, chatbot], [chatbot, msg])
        send.click(respond, [msg, chatbot], [chatbot, msg])
        clear_btn.click(clear, outputs=[chatbot, msg])
        
        gr.Markdown("*💡 For crisis support: Call 988 (US)*")
    
    return demo


if __name__ == "__main__":
    print("🚀 Starting Mental Health Support Chatbot...")
    demo = create_chatbot()
    demo.launch(server_name="0.0.0.0", server_port=7860, share=False)
