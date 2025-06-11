from src.main_view import App

if __name__ == "__main__":
    try:
        App().mainloop()
    except KeyboardInterrupt:
        print("Keyboard interrupt received")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        print("Application terminated")