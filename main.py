import asyncio
import AlbotBrain as AB
import utils.TwitchConnection as TC



#Sette opp testing av alle funksjoner og slikt, mocking, unit ... you name it...
#Test cooldown funker
#Milestone 4 osv.



async def main():
    abot = AB.AlbotBrain()
    tasks = await abot.start()
    
    print(f"Gotten {tasks}")
    # This will keep the program running until the task completes
    # or until interrupted with Ctrl+C
    await asyncio.gather(*tasks)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped by user - KEYBOARDINTERUPT! CTRL+C ?")
    except Exception as e:
        print(f"Bot stopped unexpectedly.. Did you remember to start he virtual environment? Exception saying: /{e}/")

