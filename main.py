import asyncio
import os
import AlbotBrain as AB

# The dashboard reads this file to know if Albot is running, and which process to stop
PID_FILE = "albot.pid"


def write_pid_file():
    with open(PID_FILE, "w") as f:
        f.write(str(os.getpid()))


def remove_pid_file():
    # Only remove it if it is ours
    try:
        with open(PID_FILE) as f:
            pid_in_file = f.read().strip()

        # Windows can't delete a file that is still open, so this is done after the with-block
        if pid_in_file == str(os.getpid()):
            os.remove(PID_FILE)
    except OSError:
        pass


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
    write_pid_file()
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped by user - KEYBOARDINTERUPT! CTRL+C ?")
    except Exception as e:
        print(f"Bot stopped unexpectedly.. Did you remember to start the virtual environment? Exception saying: /{e}/")
    finally:
        remove_pid_file()
        print("Bot has shut down completely.")