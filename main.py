import asyncio
import AlbotBrain as AB
import utils.TwitchConnection as TC


async def main():
    abot = AB.AlbotBrain()
    tasks = await abot.start()
    
    print(f"Gotten {tasks}")
    # This will keep the program running until the task completes
    # or until interrupted with Ctrl+C
    await asyncio.gather(*tasks)

    try:
        # This will keep the program running until tasks complete or are cancelled
        await asyncio.gather(*tasks)
    except asyncio.CancelledError:
        print("Tasks were cancelled - bot is shutting down")
    except Exception as e:
        print(f"An error occurred: {e}")
        # Trigger shutdown on error
        await abot.shutdown()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped by user - KEYBOARDINTERUPT! CTRL+C ?")
    except Exception as e:
        print(f"Bot stopped unexpectedly.. Did you remember to start the virtual environment? Exception saying: /{e}/")
    finally:
        print("Bot has shut down completely.")