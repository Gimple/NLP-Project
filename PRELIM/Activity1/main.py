from GenZBot.genz import GenZChatbot

def main():
    #Main function to run the chatbot
    try:
        bot = GenZChatbot(name="ZenBot")
        
        bot.chat()
        
    except KeyboardInterrupt:
        print(bot.get_interrupt_message())
    except Exception as e:
        print(f"An error occurred: {e}")
        print("Bestie, something went wrong pero I'm still here for you! 💪")

if __name__ == "__main__":
    main()