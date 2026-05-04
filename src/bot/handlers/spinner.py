"""
Animated loading indicator for long-running AI operations.
@Architecture-Map: [HND-SPINNER]
"""
import asyncio
from aiogram.types import Message

class ProcessingSpinner:
    def __init__(self, message: Message, text: str = "🧠 Processing..."):
        self.message = message
        self.base_text = text
        self.msg_obj = None
        self.is_running = False
        self._task = None

    async def start(self):
        self.is_running = True
        try:
            self.msg_obj = await self.message.answer(f"{self.base_text} ⏳")
            self._task = asyncio.create_task(self._spin())
        except Exception as e:
            print(f"Failed to start spinner: {e}")

    async def _spin(self):
        frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        idx = 0
        while self.is_running:
            try:
                # Keep 'typing' status alive in Telegram
                await self.message.bot.send_chat_action(chat_id=self.message.chat.id, action="typing")
                await self.msg_obj.edit_text(f"{self.base_text} {frames[idx]}")
                idx = (idx + 1) % len(frames)
            except Exception:
                # If editing fails (e.g. message deleted), we just quietly stop
                break
            await asyncio.sleep(1.5)

    async def stop(self, final_text: str = None):
        self.is_running = False
        if self._task:
            self._task.cancel()
        if self.msg_obj:
            try:
                if final_text:
                    await self.msg_obj.edit_text(final_text, parse_mode="HTML")
                else:
                    await self.msg_obj.delete()
            except Exception:
                pass
