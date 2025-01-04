

def navigate_file():
    """
    Allows the user to navigate through the lines of a text file.
    """
    try:
       
        filename = input("Enter the filename: ").strip()

      
        with open(filename, 'r') as file:
            lines = file.readlines()

        if not lines:
            print(f"The file '{filename}' is empty.")
            return

      
        print(f"The file '{filename}' has {len(lines)} lines.")

        while True:
            try:
               
                line_number = int(input("Enter a line number (0 to quit): "))

                if line_number == 0:
                    print("Exiting the program.")
                    break

                if 1 <= line_number <= len(lines):
                    print(f"Line {line_number}: {lines[line_number - 1].strip()}")
                else:
                    print(f"Invalid line number. Please enter a number between 1 and {len(lines)}.")
            except ValueError:
                print("Invalid input. Please enter a valid integer.")

    except FileNotFoundError:
        print("Error: File not found. Please check the filename and try again.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    navigate_file()
